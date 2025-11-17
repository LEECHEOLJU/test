#!/usr/bin/env python3
"""
사용자 관리 스크립트
관리자 및 일반 사용자 추가, 수정, 삭제
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# 환경변수 로드
load_dotenv()


def init_app():
    """Flask 앱 초기화"""
    from flask import Flask
    from models import db

    app = Flask(__name__)

    # 데이터베이스 설정
    database_url = os.getenv('DATABASE_URL', 'sqlite:///cgv_alert.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app, db


def list_users(db):
    """사용자 목록 조회"""
    from models import db as database
    from app_vercel import User

    print()
    print("=" * 80)
    print("👥 사용자 목록")
    print("=" * 80)
    print()

    users = User.query.all()

    if not users:
        print("등록된 사용자가 없습니다")
        return

    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<10} {'Created':<20}")
    print("-" * 80)

    for user in users:
        is_admin = "✅ 관리자" if user.is_admin else "일반"
        created = user.created_at.strftime('%Y-%m-%d %H:%M')
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {is_admin:<10} {created:<20}")

    print()
    print(f"전체 사용자: {len(users)}명")
    print()


def add_user(db):
    """사용자 추가"""
    from app_vercel import User

    print()
    print("=" * 80)
    print("➕ 새 사용자 추가")
    print("=" * 80)
    print()

    # 사용자 정보 입력
    username = input("Username (로그인 ID): ").strip()
    if not username:
        print("❌ Username을 입력해야 합니다")
        return

    # 중복 확인
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"❌ Username '{username}'은 이미 사용 중입니다")
        return

    email = input("Email 주소: ").strip()
    if not email or '@' not in email:
        print("❌ 유효한 이메일 주소를 입력해야 합니다")
        return

    # 이메일 중복 확인
    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"❌ Email '{email}'은 이미 사용 중입니다")
        return

    password = input("비밀번호 (8자 이상): ").strip()
    if len(password) < 8:
        print("❌ 비밀번호는 최소 8자 이상이어야 합니다")
        return

    password_confirm = input("비밀번호 확인: ").strip()
    if password != password_confirm:
        print("❌ 비밀번호가 일치하지 않습니다")
        return

    is_admin_input = input("관리자 권한 부여? (y/n) [n]: ").strip().lower()
    is_admin = is_admin_input in ['y', 'yes', '예', 'ㅇ']

    # 사용자 생성
    try:
        user = User(
            username=username,
            email=email,
            is_admin=is_admin
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        print()
        print("=" * 80)
        print("✅ 사용자가 성공적으로 추가되었습니다!")
        print("=" * 80)
        print()
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"관리자: {'예' if is_admin else '아니오'}")
        print()

    except Exception as e:
        print(f"❌ 사용자 추가 실패: {e}")
        db.session.rollback()


def change_password(db):
    """비밀번호 변경"""
    from app_vercel import User

    print()
    print("=" * 80)
    print("🔐 비밀번호 변경")
    print("=" * 80)
    print()

    username = input("Username: ").strip()
    if not username:
        print("❌ Username을 입력해야 합니다")
        return

    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"❌ 사용자 '{username}'을 찾을 수 없습니다")
        return

    print(f"사용자: {user.username} ({user.email})")
    print()

    new_password = input("새 비밀번호 (8자 이상): ").strip()
    if len(new_password) < 8:
        print("❌ 비밀번호는 최소 8자 이상이어야 합니다")
        return

    password_confirm = input("새 비밀번호 확인: ").strip()
    if new_password != password_confirm:
        print("❌ 비밀번호가 일치하지 않습니다")
        return

    # 비밀번호 변경
    try:
        user.set_password(new_password)
        db.session.commit()

        print()
        print("=" * 80)
        print("✅ 비밀번호가 성공적으로 변경되었습니다!")
        print("=" * 80)
        print()

    except Exception as e:
        print(f"❌ 비밀번호 변경 실패: {e}")
        db.session.rollback()


def delete_user(db):
    """사용자 삭제"""
    from app_vercel import User

    print()
    print("=" * 80)
    print("🗑️  사용자 삭제")
    print("=" * 80)
    print()

    username = input("삭제할 Username: ").strip()
    if not username:
        print("❌ Username을 입력해야 합니다")
        return

    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"❌ 사용자 '{username}'을 찾을 수 없습니다")
        return

    print()
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"관리자: {'예' if user.is_admin else '아니오'}")
    print()

    # admin 계정 삭제 방지
    if user.username == 'admin':
        print("⚠️  주의: 기본 admin 계정을 삭제하려고 합니다")
        print("   admin 계정을 삭제하면 로그인할 수 없게 될 수 있습니다")
        print()

    confirm = input("정말 삭제하시겠습니까? (yes 입력): ").strip()
    if confirm != 'yes':
        print("취소되었습니다")
        return

    # 사용자 삭제
    try:
        db.session.delete(user)
        db.session.commit()

        print()
        print("=" * 80)
        print("✅ 사용자가 성공적으로 삭제되었습니다")
        print("=" * 80)
        print()

    except Exception as e:
        print(f"❌ 사용자 삭제 실패: {e}")
        db.session.rollback()


def toggle_admin(db):
    """관리자 권한 토글"""
    from app_vercel import User

    print()
    print("=" * 80)
    print("👑 관리자 권한 변경")
    print("=" * 80)
    print()

    username = input("Username: ").strip()
    if not username:
        print("❌ Username을 입력해야 합니다")
        return

    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"❌ 사용자 '{username}'을 찾을 수 없습니다")
        return

    print()
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"현재 관리자 권한: {'예' if user.is_admin else '아니오'}")
    print()

    # 권한 변경
    new_status = not user.is_admin

    try:
        user.is_admin = new_status
        db.session.commit()

        print()
        print("=" * 80)
        print("✅ 관리자 권한이 변경되었습니다")
        print("=" * 80)
        print()
        print(f"새로운 관리자 권한: {'예' if new_status else '아니오'}")
        print()

    except Exception as e:
        print(f"❌ 권한 변경 실패: {e}")
        db.session.rollback()


def show_menu():
    """메뉴 표시"""
    print()
    print("=" * 80)
    print("🎬 CGV IMAX 예매 알림 시스템 - 사용자 관리")
    print("=" * 80)
    print()
    print("1. 사용자 목록 조회")
    print("2. 새 사용자 추가")
    print("3. 비밀번호 변경")
    print("4. 사용자 삭제")
    print("5. 관리자 권한 변경")
    print("0. 종료")
    print()


def main():
    """메인 함수"""
    # Flask 앱 초기화
    app, db = init_app()

    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()

        while True:
            show_menu()
            choice = input("선택 (0-5): ").strip()

            if choice == '1':
                list_users(db)
            elif choice == '2':
                add_user(db)
            elif choice == '3':
                change_password(db)
            elif choice == '4':
                delete_user(db)
            elif choice == '5':
                toggle_admin(db)
            elif choice == '0':
                print()
                print("프로그램을 종료합니다")
                break
            else:
                print("❌ 잘못된 선택입니다")

            input("\nEnter를 눌러 계속...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("프로그램이 취소되었습니다")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
