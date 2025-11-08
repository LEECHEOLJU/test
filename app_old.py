"""
CGV 용산 IMAX 예매 알림 시스템 - Flask 서버
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

from config_manager import ConfigManager
from crawler import MockCGVCrawler, CGVCrawler
from email_sender import EmailSender
from scheduler import MovieMonitor

# 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)  # CORS 활성화

# 모듈 초기화
config_manager = ConfigManager()
email_sender = EmailSender()
# 개발 중에는 Mock 크롤러 사용, 프로덕션에서는 실제 크롤러 사용
USE_MOCK = os.getenv('USE_MOCK_CRAWLER', 'True').lower() == 'true'
movie_monitor = MovieMonitor(use_mock=USE_MOCK)
crawler = MockCGVCrawler() if USE_MOCK else CGVCrawler()


# ============================================================================
# 웹 페이지 라우트
# ============================================================================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')


# ============================================================================
# API 엔드포인트
# ============================================================================

# ===== 영화 관리 =====

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """CGV 용산 IMAX 영화 목록 조회"""
    try:
        theater = config_manager.get_theater()
        movies = crawler.get_imax_movies(theater)

        return jsonify({
            'success': True,
            'movies': movies,
            'count': len(movies)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/movies/select', methods=['POST'])
def select_movie():
    """감시할 영화 선택"""
    try:
        data = request.get_json()
        movie_title = data.get('movie_title', '').strip()

        if not movie_title:
            return jsonify({
                'success': False,
                'error': '영화 제목을 입력해주세요.'
            }), 400

        config_manager.set_monitoring_movie(movie_title)

        return jsonify({
            'success': True,
            'message': f'{movie_title} 선택 완료',
            'movie_title': movie_title
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 모니터링 제어 =====

@app.route('/api/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """현재 감시 상태 조회"""
    try:
        status = movie_monitor.get_status()
        last_notification = config_manager.get_last_notification()

        return jsonify({
            'success': True,
            'status': status,
            'last_notification': last_notification
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """감시 시작"""
    try:
        movie_title = config_manager.get_monitoring_movie()

        if not movie_title:
            return jsonify({
                'success': False,
                'error': '먼저 감시할 영화를 선택해주세요.'
            }), 400

        # 이메일 설정 확인
        recipients = config_manager.get_email_recipients()
        if not recipients:
            return jsonify({
                'success': False,
                'error': '먼저 이메일 주소를 설정해주세요.'
            }), 400

        email_config = config_manager.get_email_config()
        if not email_config.get('sender_email') or not email_config.get('sender_password'):
            return jsonify({
                'success': False,
                'error': '발신자 이메일 정보를 설정해주세요. (.env 파일 확인)'
            }), 400

        success = movie_monitor.start_monitoring()

        if success:
            return jsonify({
                'success': True,
                'message': f'{movie_title} 감시 시작'
            })
        else:
            return jsonify({
                'success': False,
                'error': '모니터링 시작 실패'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """감시 중지"""
    try:
        success = movie_monitor.stop_monitoring()

        if success:
            return jsonify({
                'success': True,
                'message': '감시 중지'
            })
        else:
            return jsonify({
                'success': False,
                'error': '모니터링 중지 실패'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 설정 관리 =====

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """설정 조회"""
    try:
        config = config_manager.load_config()

        # 비밀번호는 마스킹
        if 'email' in config and 'sender_password' in config['email']:
            config['email']['sender_password'] = '********' if config['email']['sender_password'] else ''

        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/settings/email', methods=['PUT'])
def update_email_settings():
    """이메일 주소 업데이트"""
    try:
        data = request.get_json()
        recipients = data.get('recipients', [])

        # 이메일 형식 검증
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

        valid_recipients = []
        for email in recipients:
            email = email.strip()
            if email and email_pattern.match(email):
                valid_recipients.append(email)

        if not valid_recipients:
            return jsonify({
                'success': False,
                'error': '유효한 이메일 주소를 입력해주세요.'
            }), 400

        config_manager.set_email_recipients(valid_recipients)

        return jsonify({
            'success': True,
            'message': '이메일 주소 업데이트 완료',
            'recipients': valid_recipients
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/settings/email/test', methods=['POST'])
def send_test_email():
    """테스트 이메일 발송"""
    try:
        email_config = config_manager.get_email_config()
        recipients = email_config.get('recipients', [])

        if not recipients:
            return jsonify({
                'success': False,
                'error': '수신자 이메일을 먼저 설정해주세요.'
            }), 400

        sender_email = email_config.get('sender_email', '')
        sender_password = email_config.get('sender_password', '')

        if not sender_email or not sender_password:
            return jsonify({
                'success': False,
                'error': '발신자 이메일 정보를 설정해주세요. (.env 파일 확인)'
            }), 400

        success = email_sender.send_test_email(
            sender_email=sender_email,
            sender_password=sender_password,
            recipients=recipients
        )

        if success:
            return jsonify({
                'success': True,
                'message': '테스트 이메일 발송 완료'
            })
        else:
            return jsonify({
                'success': False,
                'error': '테스트 이메일 발송 실패. 이메일 설정을 확인해주세요.'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== 헬스 체크 =====

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'service': 'CGV IMAX Booking Alert',
        'version': '1.0.0'
    })


# ============================================================================
# 서버 실행
# ============================================================================

if __name__ == '__main__':
    # 개발 모드
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    port = int(os.getenv('PORT', 5000))

    print("=" * 60)
    print("CGV 용산 IMAX 예매 알림 시스템")
    print("=" * 60)
    print(f"서버 주소: http://localhost:{port}")
    print(f"디버그 모드: {debug_mode}")
    print(f"Mock 크롤러 사용: {USE_MOCK}")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )
