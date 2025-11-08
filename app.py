"""
CGV IMAX 예매 알림 시스템 v2.0 - 완전판
실시간 알림, 사용자 인증, Supabase 연동
"""
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import time
import queue
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from models import db, Movie, Theater, Notification, CrawlLog, UserPreference
from notification_service import NotificationService
from advanced_crawler import AdvancedCGVCrawler, MockCGVCrawler

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cgv_alert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Supabase 또는 일반 PostgreSQL
database_url = os.getenv('DATABASE_URL', 'sqlite:///cgv_alert.db')
# Supabase URL 형식 처리
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# CORS 활성화
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 데이터베이스 초기화
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 서비스 초기화
notification_service = NotificationService()
USE_MOCK = os.getenv('USE_MOCK_CRAWLER', 'True').lower() == 'true'
crawler = MockCGVCrawler() if USE_MOCK else AdvancedCGVCrawler()

# SSE 이벤트 큐
sse_queues = {}

# 스케줄러
scheduler = BackgroundScheduler()
scheduler.start()

# 모니터링 상태
monitoring_active = False


# ============================================================================
# User Model (간단한 인증용)
# ============================================================================

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================================================
# 데이터베이스 초기화
# ============================================================================

def init_db():
    """데이터베이스 초기화"""
    with app.app_context():
        db.create_all()
        logger.info("데이터베이스 테이블 생성 완료")

        # 기본 사용자 생성 (개발용)
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')  # 프로덕션에서는 변경 필요
            db.session.add(admin)
            db.session.commit()
            logger.info("기본 관리자 계정 생성: admin/admin123")

        # 기본 설정 생성
        if not UserPreference.query.first():
            default_prefs = UserPreference(
                theme='light',
                notification_channels=['email'],
                email_addresses=[],
                check_interval=180
            )
            db.session.add(default_prefs)
            db.session.commit()
            logger.info("기본 사용자 설정 생성")

        # 기본 극장 추가
        if not Theater.query.first():
            theaters = [
                Theater(name='용산아이파크몰', location='서울', theater_type='IMAX', cgv_theater_id='0013'),
                Theater(name='강남', location='서울', theater_type='IMAX', cgv_theater_id='0056'),
                Theater(name='왕십리', location='서울', theater_type='IMAX', cgv_theater_id='0074'),
            ]
            db.session.add_all(theaters)
            db.session.commit()
            logger.info("기본 극장 추가")


# ============================================================================
# SSE (Server-Sent Events)
# ============================================================================

def send_sse_event(event_type, data):
    """모든 연결된 클라이언트에게 SSE 이벤트 전송"""
    for client_queue in sse_queues.values():
        try:
            client_queue.put({
                'event': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except:
            pass


@app.route('/api/stream')
def stream():
    """SSE 스트림 엔드포인트"""
    def event_stream():
        # 클라이언트별 큐 생성
        client_id = request.remote_addr + str(time.time())
        client_queue = queue.Queue()
        sse_queues[client_id] = client_queue

        try:
            while True:
                try:
                    # 큐에서 이벤트 가져오기 (타임아웃 30초)
                    event = client_queue.get(timeout=30)
                    yield f"event: {event['event']}\n"
                    yield f"data: {json.dumps(event['data'])}\n\n"
                except queue.Empty:
                    # Keep-alive
                    yield f": heartbeat\n\n"
        except GeneratorExit:
            # 클라이언트 연결 종료
            del sse_queues[client_id]

    return Response(stream_with_context(event_stream()), content_type='text/event-stream')


# ============================================================================
# 모니터링 작업
# ============================================================================

def monitoring_job():
    """백그라운드 모니터링 작업"""
    global monitoring_active

    if not monitoring_active:
        return

    try:
        with app.app_context():
            # 감시 중인 영화들 조회
            monitored_movies = Movie.query.filter_by(is_monitoring=True).all()

            if not monitored_movies:
                logger.info("감시 중인 영화가 없습니다")
                return

            logger.info(f"영화 {len(monitored_movies)}개 모니터링 중...")

            for movie in monitored_movies:
                try:
                    # 예매 확인
                    result = crawler.check_booking_available(movie.title)

                    if result and result.get('available'):
                        logger.info(f"🎉 예매 오픈 감지: {movie.title}")

                        # 알림 발송
                        send_booking_notification(movie, result)

                        # SSE 이벤트 전송
                        send_sse_event('booking_opened', {
                            'movie_id': movie.id,
                            'movie_title': movie.title,
                            'booking_url': result.get('url')
                        })

                except Exception as e:
                    logger.error(f"영화 확인 중 오류 ({movie.title}): {e}")

            # 크롤링 로그 저장
            log = CrawlLog(
                status='success',
                message=f'{len(monitored_movies)}개 영화 확인 완료',
                movies_found=len(monitored_movies),
                duration=0.0
            )
            db.session.add(log)
            db.session.commit()

    except Exception as e:
        logger.error(f"모니터링 작업 오류: {e}")


def send_booking_notification(movie, booking_info):
    """예매 오픈 알림 발송"""
    try:
        # 사용자 설정 가져오기
        prefs = UserPreference.query.first()
        if not prefs:
            return

        # 이메일 설정
        email_config = {
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'email_addresses': prefs.email_addresses or [],
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
            'telegram_chat_id': prefs.telegram_chat_id,
            'discord_webhook_url': prefs.discord_webhook_url
        }

        # 알림 발송
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            notification_service.send_notification(
                channels=prefs.notification_channels or ['email'],
                movie_title=movie.title,
                booking_url=booking_info.get('url', ''),
                theater='CGV 용산 IMAX',
                config=email_config
            )
        )
        loop.close()

        # 알림 히스토리 저장
        for channel, success in results.items():
            notification = Notification(
                movie_id=movie.id,
                notification_type=channel,
                booking_url=booking_info.get('url'),
                showtime_info=booking_info.get('showtime', ''),
                success=success,
                recipients=email_config.get('email_addresses', [])
            )
            db.session.add(notification)

        db.session.commit()
        logger.info(f"알림 발송 완료: {movie.title}")

    except Exception as e:
        logger.error(f"알림 발송 실패: {e}")


# ============================================================================
# 웹 페이지 라우트
# ============================================================================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index_v2.html')


@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/settings')
def settings_page():
    """설정 페이지"""
    return render_template('settings.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': '로그인 성공'})
            return redirect(url_for('index'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'error': '잘못된 사용자명 또는 비밀번호'}), 401
            return render_template('login.html', error='잘못된 사용자명 또는 비밀번호')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """로그아웃"""
    logout_user()
    return redirect(url_for('login'))


# ============================================================================
# API 엔드포인트 - 영화
# ============================================================================

@app.route('/api/v2/movies', methods=['GET'])
def get_movies():
    """영화 목록 조회"""
    try:
        theater_id = request.args.get('theater_id', '0013')

        # 크롤러에서 영화 가져오기
        movies_data = crawler.get_movies(theater_id)

        # DB 업데이트
        for movie_data in movies_data:
            movie = Movie.query.filter_by(cgv_movie_id=movie_data.get('cgv_movie_id')).first()

            if movie:
                for key, value in movie_data.items():
                    setattr(movie, key, value)
                movie.updated_at = datetime.utcnow()
            else:
                movie = Movie(**movie_data)
                db.session.add(movie)

        db.session.commit()

        # DB에서 전체 조회
        movies = Movie.query.order_by(Movie.created_at.desc()).all()

        return jsonify({
            'success': True,
            'movies': [m.to_dict() for m in movies],
            'count': len(movies)
        })

    except Exception as e:
        logger.error(f"영화 목록 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/movies/<int:movie_id>/monitor', methods=['POST'])
def toggle_movie_monitoring(movie_id):
    """영화 모니터링 토글"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        movie.is_monitoring = not movie.is_monitoring
        movie.updated_at = datetime.utcnow()
        db.session.commit()

        # SSE 이벤트
        send_sse_event('monitoring_changed', {
            'movie_id': movie.id,
            'is_monitoring': movie.is_monitoring
        })

        return jsonify({
            'success': True,
            'movie': movie.to_dict()
        })

    except Exception as e:
        logger.error(f"모니터링 토글 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API 엔드포인트 - 모니터링
# ============================================================================

@app.route('/api/v2/monitoring/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    global monitoring_active

    try:
        if monitoring_active:
            return jsonify({'success': False, 'error': '이미 모니터링 중입니다'}), 400

        # 감시 중인 영화 확인
        monitored_count = Movie.query.filter_by(is_monitoring=True).count()
        if monitored_count == 0:
            return jsonify({'success': False, 'error': '감시할 영화를 선택해주세요'}), 400

        # 이메일 설정 확인
        prefs = UserPreference.query.first()
        if not prefs or not prefs.email_addresses:
            return jsonify({'success': False, 'error': '이메일 주소를 설정해주세요'}), 400

        # 모니터링 시작
        monitoring_active = True

        # 스케줄러에 작업 추가
        interval = prefs.check_interval or 180
        scheduler.add_job(
            func=monitoring_job,
            trigger=IntervalTrigger(seconds=interval),
            id='movie_monitoring',
            name='영화 예매 모니터링',
            replace_existing=True
        )

        logger.info(f"모니터링 시작: {monitored_count}개 영화, {interval}초 간격")

        # SSE 이벤트
        send_sse_event('monitoring_started', {'interval': interval})

        return jsonify({
            'success': True,
            'message': '모니터링 시작',
            'monitored_count': monitored_count,
            'interval': interval
        })

    except Exception as e:
        logger.error(f"모니터링 시작 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    global monitoring_active

    try:
        monitoring_active = False

        # 스케줄러 작업 제거
        try:
            scheduler.remove_job('movie_monitoring')
        except:
            pass

        logger.info("모니터링 중지")

        # SSE 이벤트
        send_sse_event('monitoring_stopped', {})

        return jsonify({
            'success': True,
            'message': '모니터링 중지'
        })

    except Exception as e:
        logger.error(f"모니터링 중지 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        monitored_movies = Movie.query.filter_by(is_monitoring=True).all()
        prefs = UserPreference.query.first()

        return jsonify({
            'success': True,
            'active': monitoring_active,
            'monitored_movies': [m.to_dict() for m in monitored_movies],
            'count': len(monitored_movies),
            'interval': prefs.check_interval if prefs else 180
        })

    except Exception as e:
        logger.error(f"상태 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API 엔드포인트 - 알림 & 통계
# ============================================================================

@app.route('/api/v2/notifications', methods=['GET'])
def get_notifications():
    """알림 히스토리"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        notifications = Notification.query.order_by(
            Notification.sent_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'success': True,
            'notifications': [n.to_dict() for n in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page
        })

    except Exception as e:
        logger.error(f"알림 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/stats', methods=['GET'])
def get_stats():
    """통계 정보"""
    try:
        total_movies = Movie.query.count()
        monitored_movies = Movie.query.filter_by(is_monitoring=True).count()
        total_notifications = Notification.query.count()
        success_notifications = Notification.query.filter_by(success=True).count()

        recent_logs = CrawlLog.query.order_by(
            CrawlLog.created_at.desc()
        ).limit(10).all()

        return jsonify({
            'success': True,
            'stats': {
                'total_movies': total_movies,
                'monitored_movies': monitored_movies,
                'total_notifications': total_notifications,
                'success_rate': (success_notifications / total_notifications * 100) if total_notifications > 0 else 0,
                'recent_logs': [log.to_dict() for log in recent_logs]
            }
        })

    except Exception as e:
        logger.error(f"통계 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API 엔드포인트 - 설정
# ============================================================================

@app.route('/api/v2/preferences', methods=['GET'])
def get_preferences():
    """사용자 설정 조회"""
    try:
        prefs = UserPreference.query.first()
        if not prefs:
            prefs = UserPreference()
            db.session.add(prefs)
            db.session.commit()

        return jsonify({
            'success': True,
            'preferences': prefs.to_dict()
        })

    except Exception as e:
        logger.error(f"설정 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/preferences', methods=['PUT'])
def update_preferences():
    """사용자 설정 업데이트"""
    try:
        data = request.get_json()
        prefs = UserPreference.query.first()

        if not prefs:
            prefs = UserPreference()
            db.session.add(prefs)

        # 업데이트
        for key, value in data.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)

        prefs.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'preferences': prefs.to_dict()
        })

    except Exception as e:
        logger.error(f"설정 업데이트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/v2/preferences/test-email', methods=['POST'])
def test_email():
    """테스트 이메일 발송"""
    try:
        prefs = UserPreference.query.first()
        if not prefs or not prefs.email_addresses:
            return jsonify({'success': False, 'error': '이메일 주소를 먼저 설정하세요'}), 400

        from email_sender import EmailSender
        sender = EmailSender()

        success = sender.send_test(
            sender_email=os.getenv('SENDER_EMAIL'),
            sender_password=os.getenv('SENDER_PASSWORD'),
            recipients=prefs.email_addresses
        )

        return jsonify({
            'success': success,
            'message': '테스트 이메일 발송 완료' if success else '테스트 이메일 발송 실패'
        })

    except Exception as e:
        logger.error(f"테스트 이메일 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# API 엔드포인트 - 극장
# ============================================================================

@app.route('/api/v2/theaters', methods=['GET'])
def get_theaters():
    """극장 목록 조회"""
    try:
        theaters = Theater.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'theaters': [t.to_dict() for t in theaters],
            'count': len(theaters)
        })

    except Exception as e:
        logger.error(f"극장 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# 헬스 체크
# ============================================================================

@app.route('/health')
def health_check():
    """서버 상태 확인"""
    try:
        # DB 연결 확인
        db.session.execute('SELECT 1')

        return jsonify({
            'status': 'healthy',
            'service': 'CGV IMAX Alert v2.0',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'monitoring': monitoring_active
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ============================================================================
# 에러 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == '__main__':
    # 데이터베이스 초기화
    init_db()

    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))

    logger.info("=" * 60)
    logger.info("CGV IMAX 예매 알림 시스템 v2.0 - 완전판")
    logger.info("=" * 60)
    logger.info(f"서버: http://localhost:{port}")
    logger.info(f"디버그 모드: {debug_mode}")
    logger.info(f"데이터베이스: {database_url}")
    logger.info(f"Mock 크롤러: {USE_MOCK}")
    logger.info("=" * 60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
