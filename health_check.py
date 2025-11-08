"""
건강 검사 스크립트
애플리케이션의 모든 구성요소가 올바르게 작동하는지 확인
"""
import sys
import os

print("=" * 60)
print("🔍 CGV IMAX 예매 알림 시스템 - 건강 검사")
print("=" * 60)
print()

# 1. Python 버전 확인
print("1. Python 버전 확인...")
print(f"   ✅ Python {sys.version}")
print()

# 2. 필수 패키지 확인
print("2. 필수 패키지 확인...")
required_packages = [
    'flask',
    'flask_cors',
    'flask_sqlalchemy',
    'flask_login',
    'requests',
    'beautifulsoup4',
    'apscheduler',
    'python-dotenv',
    'lxml',
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - 설치 필요")
        missing_packages.append(package)

if missing_packages:
    print()
    print(f"⚠️  누락된 패키지: {', '.join(missing_packages)}")
    print(f"   실행: pip install {' '.join(missing_packages)}")
    sys.exit(1)
print()

# 3. 환경변수 확인
print("3. 환경변수 확인...")
from dotenv import load_dotenv
load_dotenv()

env_vars = {
    'FLASK_SECRET_KEY': os.getenv('FLASK_SECRET_KEY'),
    'DATABASE_URL': os.getenv('DATABASE_URL'),
    'SENDER_EMAIL': os.getenv('SENDER_EMAIL'),
    'SENDER_PASSWORD': os.getenv('SENDER_PASSWORD'),
    'USE_MOCK_CRAWLER': os.getenv('USE_MOCK_CRAWLER', 'True'),
}

for key, value in env_vars.items():
    if value:
        # 비밀번호는 마스킹
        if 'PASSWORD' in key or 'SECRET' in key:
            display_value = '*' * 8
        elif 'URL' in key and len(value) > 50:
            display_value = value[:30] + '...'
        else:
            display_value = value
        print(f"   ✅ {key}: {display_value}")
    else:
        print(f"   ⚠️  {key}: 설정되지 않음")
print()

# 4. 모듈 임포트 확인
print("4. 모듈 임포트 확인...")
try:
    from app import app, db
    print("   ✅ app 모듈")
except Exception as e:
    print(f"   ❌ app 모듈 임포트 실패: {e}")
    sys.exit(1)

try:
    from models import Movie, Theater, Notification, CrawlLog, UserPreference
    print("   ✅ models 모듈")
except Exception as e:
    print(f"   ❌ models 모듈 임포트 실패: {e}")
    sys.exit(1)

try:
    from notification_service import NotificationService
    print("   ✅ notification_service 모듈")
except Exception as e:
    print(f"   ❌ notification_service 모듈 임포트 실패: {e}")
    sys.exit(1)

try:
    from advanced_crawler import AdvancedCGVCrawler, MockCGVCrawler
    print("   ✅ advanced_crawler 모듈")
except Exception as e:
    print(f"   ❌ advanced_crawler 모듈 임포트 실패: {e}")
    sys.exit(1)
print()

# 5. 데이터베이스 연결 확인
print("5. 데이터베이스 연결 확인...")
try:
    with app.app_context():
        # 데이터베이스 연결 테스트
        from sqlalchemy import text
        result = db.session.execute(text("SELECT 1"))
        result.fetchone()
        print(f"   ✅ 데이터베이스 연결 성공")
        print(f"   📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
except Exception as e:
    print(f"   ❌ 데이터베이스 연결 실패: {e}")
    print(f"   💡 Tip: .env 파일의 DATABASE_URL을 확인하세요")
print()

# 6. 테이블 존재 확인
print("6. 데이터베이스 테이블 확인...")
try:
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        expected_tables = ['movies', 'theaters', 'notifications', 'crawl_logs', 'user_preferences', 'users']
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ⚠️  {table} - 테이블 생성 필요")

        if set(expected_tables).issubset(set(tables)):
            print(f"   📋 모든 테이블 존재")
        else:
            print()
            print(f"   💡 테이블 생성 명령:")
            print(f"      python -c \"from app import app, db; app.app_context().push(); db.create_all()\"")
except Exception as e:
    print(f"   ❌ 테이블 확인 실패: {e}")
print()

# 7. 크롤러 테스트
print("7. 크롤러 테스트...")
try:
    use_mock = os.getenv('USE_MOCK_CRAWLER', 'True').lower() == 'true'
    if use_mock:
        print("   📍 Mock 크롤러 모드")
        crawler = MockCGVCrawler()
    else:
        print("   📍 실제 크롤러 모드")
        crawler = AdvancedCGVCrawler()

    # 극장 목록 테스트
    theaters = crawler.get_theaters()
    if theaters:
        print(f"   ✅ 극장 목록 조회: {len(theaters)}개")
    else:
        print("   ⚠️  극장 목록이 비어있습니다")

    # 영화 목록 테스트
    movies = crawler.get_movies()
    if movies:
        print(f"   ✅ 영화 목록 조회: {len(movies)}개")
        if movies:
            print(f"   🎬 첫 번째 영화: {movies[0].get('title', 'N/A')}")
    else:
        print("   ⚠️  영화 목록이 비어있습니다")

except Exception as e:
    print(f"   ❌ 크롤러 테스트 실패: {e}")
print()

# 8. 알림 서비스 테스트
print("8. 알림 서비스 초기화...")
try:
    notification_service = NotificationService()
    print("   ✅ NotificationService 초기화 성공")
except Exception as e:
    print(f"   ❌ NotificationService 초기화 실패: {e}")
print()

# 9. Flask 앱 설정 확인
print("9. Flask 앱 설정 확인...")
try:
    print(f"   ✅ SECRET_KEY: {'설정됨' if app.config['SECRET_KEY'] else '미설정'}")
    print(f"   ✅ SQLALCHEMY_DATABASE_URI: {'설정됨' if app.config['SQLALCHEMY_DATABASE_URI'] else '미설정'}")
    print(f"   ✅ SQLALCHEMY_TRACK_MODIFICATIONS: {app.config['SQLALCHEMY_TRACK_MODIFICATIONS']}")
except Exception as e:
    print(f"   ❌ Flask 설정 확인 실패: {e}")
print()

# 최종 결과
print("=" * 60)
print("✅ 건강 검사 완료!")
print("=" * 60)
print()
print("📌 다음 단계:")
print("   1. 애플리케이션 실행: python app.py")
print("   2. 브라우저에서 접속: http://localhost:5000")
print("   3. 로그 확인: tail -f cgv_alert.log")
print()
print("📚 문서:")
print("   - README.md: 전체 가이드")
print("   - DEPLOYMENT.md: 배포 가이드")
print("   - SUPABASE_SETUP.md: Supabase 연동")
print("   - API.md: API 문서")
print()
