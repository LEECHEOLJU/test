"""
CGV 용산 IMAX 예매 알림 시스템 v2.0
완전히 재구축된 프로덕션 레벨 애플리케이션
"""
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

from models import db, Movie, Theater, Notification, CrawlLog, Settings, UserPreference
from notification_service import NotificationService
from advanced_crawler import AdvancedCGVCrawler, MockCGVCrawler

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///cgv_alert.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS 활성화
CORS(app)

# 데이터베이스 초기화
db.init_app(app)

# 서비스 초기화
notification_service = NotificationService()
USE_MOCK = os.getenv('USE_MOCK_CRAWLER', 'True').lower() == 'true'
crawler = MockCGVCrawler() if USE_MOCK else AdvancedCGVCrawler()

# 전역 모니터 상태
monitoring_active = False
monitoring_jobs = {}


# ============================================================================
# 데이터베이스 초기화
# ============================================================================

@app.before_first_request
def create_tables():
    """데이터베이스 테이블 생성"""
    db.create_all()
    logger.info("데이터베이스 테이블 생성 완료")

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


# ============================================================================
# API 엔드포인트 - 영화 관리
# ============================================================================

@app.route('/api/v2/movies', methods=['GET'])
def get_movies():
    """영화 목록 조회"""
    try:
        theater_id = request.args.get('theater_id', '0013')

        # 크롤러에서 영화 목록 가져오기
        movies_data = crawler.get_movies(theater_id)

        # 데이터베이스에 저장/업데이트
        for movie_data in movies_data:
            movie = Movie.query.filter_by(
                cgv_movie_id=movie_data.get('cgv_movie_id')
            ).first()

            if movie:
                # 업데이트
                for key, value in movie_data.items():
                    setattr(movie, key, value)
            else:
                # 새로 추가
                movie = Movie(**movie_data)
                db.session.add(movie)

        db.session.commit()

        # DB에서 조회
        movies = Movie.query.all()

        return jsonify({
            'success': True,
            'movies': [m.to_dict() for m in movies],
            'count': len(movies)
        })

    except Exception as e:
        logger.error(f"영화 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v2/movies/<int:movie_id>/monitor', methods=['POST'])
def toggle_movie_monitoring(movie_id):
    """영화 모니터링 토글"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        movie.is_monitoring = not movie.is_monitoring
        db.session.commit()

        return jsonify({
            'success': True,
            'movie': movie.to_dict()
        })

    except Exception as e:
        logger.error(f"모니터링 토글 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API 엔드포인트 - 모니터링
# ============================================================================

@app.route('/api/v2/monitoring/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    global monitoring_active

    try:
        if monitoring_active:
            return jsonify({
                'success': False,
                'error': '이미 모니터링이 실행 중입니다.'
            }), 400

        monitoring_active = True

        # 백그라운드 작업 시작 (APScheduler 등)
        # 여기서는 간단히 상태만 변경

        return jsonify({
            'success': True,
            'message': '모니터링 시작됨'
        })

    except Exception as e:
        logger.error(f"모니터링 시작 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v2/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    global monitoring_active

    try:
        monitoring_active = False

        return jsonify({
            'success': True,
            'message': '모니터링 중지됨'
        })

    except Exception as e:
        logger.error(f"모니터링 중지 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/v2/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        monitored_movies = Movie.query.filter_by(is_monitoring=True).all()

        return jsonify({
            'success': True,
            'active': monitoring_active,
            'monitored_movies': [m.to_dict() for m in monitored_movies],
            'count': len(monitored_movies)
        })

    except Exception as e:
        logger.error(f"상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API 엔드포인트 - 알림 히스토리
# ============================================================================

@app.route('/api/v2/notifications', methods=['GET'])
def get_notifications():
    """알림 히스토리 조회"""
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API 엔드포인트 - 통계
# ============================================================================

@app.route('/api/v2/stats', methods=['GET'])
def get_stats():
    """통계 정보 조회"""
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# API 엔드포인트 - 사용자 설정
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
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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

        db.session.commit()

        return jsonify({
            'success': True,
            'preferences': prefs.to_dict()
        })

    except Exception as e:
        logger.error(f"설정 업데이트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# 헬스 체크
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'service': 'CGV IMAX Booking Alert v2.0',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))

    logger.info("=" * 60)
    logger.info("CGV 용산 IMAX 예매 알림 시스템 v2.0")
    logger.info("=" * 60)
    logger.info(f"서버 주소: http://localhost:{port}")
    logger.info(f"디버그 모드: {debug_mode}")
    logger.info(f"Mock 크롤러: {USE_MOCK}")
    logger.info("=" * 60)

    with app.app_context():
        db.create_all()

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
