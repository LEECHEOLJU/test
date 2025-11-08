"""
초기 사용자 생성 스크립트
관리자 계정을 생성하여 로그인할 수 있도록 함
"""
import os
from dotenv import load_dotenv
from app import app, db, User

# 환경변수 로드
load_dotenv()

def create_initial_user():
    """초기 관리자 사용자 생성"""

    # 환경변수에서 읽기
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')

    with app.app_context():
        # 테이블 생성
        print("📊 데이터베이스 테이블 생성 중...")
        db.create_all()
        print("✅ 테이블 생성 완료")

        # 기존 사용자 확인
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            print(f"⚠️  사용자 '{username}'이(가) 이미 존재합니다.")
            print(f"   이메일: {existing_user.email}")

            # 비밀번호 업데이트 여부 확인
            update = input("비밀번호를 업데이트하시겠습니까? (y/N): ").strip().lower()
            if update == 'y':
                existing_user.set_password(password)
                db.session.commit()
                print("✅ 비밀번호 업데이트 완료")
            else:
                print("⏭️  스킵")
        else:
            # 새 사용자 생성
            print(f"👤 관리자 계정 생성 중...")
            user = User(
                username=username,
                email=email,
                is_admin=True
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            print("=" * 60)
            print("✅ 관리자 계정이 성공적으로 생성되었습니다!")
            print("=" * 60)
            print(f"사용자명: {username}")
            print(f"이메일:   {email}")
            print(f"비밀번호: {password}")
            print("=" * 60)
            print()
            print("⚠️  보안을 위해 첫 로그인 후 비밀번호를 변경하세요!")
            print()

        # 사용자 목록 표시
        print("\n📋 현재 등록된 사용자:")
        users = User.query.all()
        for u in users:
            admin_badge = "👑 관리자" if u.is_admin else "일반"
            print(f"   - {u.username} ({u.email}) [{admin_badge}]")

        print(f"\n총 {len(users)}명의 사용자")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 CGV IMAX 예매 알림 - 초기 설정")
    print("=" * 60)
    print()

    try:
        create_initial_user()
        print()
        print("✅ 초기 설정 완료!")
        print()
        print("다음 단계:")
        print("1. python app.py 실행")
        print("2. http://localhost:5000 접속")
        print("3. 생성된 계정으로 로그인")
        print()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print()
        print("해결 방법:")
        print("1. .env 파일이 존재하는지 확인")
        print("2. DATABASE_URL이 올바른지 확인")
        print("3. 필요한 패키지가 설치되었는지 확인: pip install -r requirements.txt")
        exit(1)
