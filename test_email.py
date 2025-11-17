#!/usr/bin/env python3
"""
이메일 발송 테스트 도구
Gmail 설정이 올바른지 확인하는 스크립트
"""
import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_email_configuration():
    """이메일 설정 검증"""
    print("=" * 60)
    print("📧 이메일 설정 테스트")
    print("=" * 60)
    print()

    # 환경변수 확인
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    print("1️⃣  환경변수 확인")
    print("-" * 60)

    if not sender_email:
        print("❌ SENDER_EMAIL이 설정되지 않았습니다")
        print("   .env 파일에서 SENDER_EMAIL을 설정하세요")
        return False
    else:
        print(f"✅ SENDER_EMAIL: {sender_email}")

    if not sender_password:
        print("❌ SENDER_PASSWORD가 설정되지 않았습니다")
        print("   .env 파일에서 SENDER_PASSWORD를 설정하세요")
        return False
    else:
        # 비밀번호 길이만 표시 (보안)
        print(f"✅ SENDER_PASSWORD: ******* ({len(sender_password)}자)")

    print()

    # 이메일 형식 확인
    print("2️⃣  이메일 형식 검증")
    print("-" * 60)

    if '@gmail.com' not in sender_email:
        print("⚠️  Gmail 주소가 아닙니다")
        print("   이 스크립트는 Gmail을 기준으로 작성되었습니다")
        print("   다른 이메일 서비스를 사용하는 경우 SMTP 설정을 변경해야 합니다")
    else:
        print("✅ Gmail 주소 형식 확인")

    print()

    # 앱 비밀번호 길이 확인
    print("3️⃣  Gmail 앱 비밀번호 검증")
    print("-" * 60)

    # 공백 제거 후 길이 확인
    password_no_space = sender_password.replace(' ', '')

    if len(password_no_space) != 16:
        print(f"⚠️  앱 비밀번호 길이가 {len(password_no_space)}자입니다")
        print("   Gmail 앱 비밀번호는 일반적으로 16자입니다")
        print("   공백을 제거한 비밀번호를 사용하세요")
        print()
        print("   Gmail 앱 비밀번호 생성 방법:")
        print("   1. https://myaccount.google.com/security")
        print("   2. 2단계 인증 활성화")
        print("   3. 앱 비밀번호 생성")
    else:
        print("✅ 앱 비밀번호 길이 확인 (16자)")

    print()

    # SMTP 연결 테스트
    print("4️⃣  SMTP 서버 연결 테스트")
    print("-" * 60)

    try:
        import smtplib

        print("Gmail SMTP 서버에 연결 중... (smtp.gmail.com:587)")

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()

        print("✅ SMTP 서버 연결 성공")
        print()
        print("로그인 시도 중...")

        server.login(sender_email, sender_password)

        print("✅ Gmail 로그인 성공!")
        server.quit()

        print()
        print("=" * 60)
        print("🎉 모든 테스트 통과!")
        print("=" * 60)
        print()
        print("이메일 설정이 올바릅니다.")
        print("이제 테스트 이메일을 발송하시겠습니까?")

        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail 로그인 실패")
        print()
        print("🔍 문제 해결 방법:")
        print()
        print("1. Gmail 2단계 인증이 활성화되어 있는지 확인")
        print("   → https://myaccount.google.com/security")
        print()
        print("2. 앱 비밀번호를 새로 생성")
        print("   → 검색: '앱 비밀번호'")
        print("   → 앱: 메일, 기기: 기타 (CGV Alert)")
        print()
        print("3. 생성된 16자리 비밀번호를 공백 없이 .env에 입력")
        print("   SENDER_PASSWORD=abcdefghijklmnop")
        print()
        return False

    except smtplib.SMTPException as e:
        print(f"❌ SMTP 오류: {e}")
        return False

    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        print()
        print("🔍 인터넷 연결을 확인하세요")
        return False


def send_test_email():
    """테스트 이메일 발송"""
    print()
    print("=" * 60)
    print("📨 테스트 이메일 발송")
    print("=" * 60)
    print()

    recipient = input("수신자 이메일 주소 입력: ").strip()

    if not recipient or '@' not in recipient:
        print("❌ 유효하지 않은 이메일 주소입니다")
        return

    print()
    print(f"테스트 이메일을 {recipient}로 발송합니다...")
    print()

    try:
        from email_sender import EmailSender

        sender = EmailSender()
        sender_email = os.getenv('SENDER_EMAIL')
        sender_password = os.getenv('SENDER_PASSWORD')

        success = sender.send_test(
            sender_email=sender_email,
            sender_password=sender_password,
            recipients=[recipient]
        )

        if success:
            print()
            print("=" * 60)
            print("✅ 테스트 이메일 발송 성공!")
            print("=" * 60)
            print()
            print(f"받은편지함을 확인하세요: {recipient}")
            print("(스팸 폴더도 확인해주세요)")
        else:
            print()
            print("❌ 테스트 이메일 발송 실패")
            print()
            print("위의 오류 메시지를 확인하고 설정을 수정하세요")

    except ImportError:
        print("❌ email_sender 모듈을 찾을 수 없습니다")
        print("   프로젝트 루트 디렉토리에서 실행하세요")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def main():
    """메인 함수"""
    print()
    print("🎬 CGV IMAX 예매 알림 시스템")
    print()

    # 설정 테스트
    config_ok = test_email_configuration()

    if not config_ok:
        print()
        print("=" * 60)
        print("⚠️  설정에 문제가 있습니다")
        print("=" * 60)
        print()
        print("위의 안내를 따라 문제를 해결하세요")
        sys.exit(1)

    # 테스트 이메일 발송 여부
    print()
    response = input("테스트 이메일을 발송하시겠습니까? (y/n): ").strip().lower()

    if response in ['y', 'yes', '예', 'ㅇ']:
        send_test_email()
    else:
        print()
        print("테스트를 종료합니다")

    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print("테스트가 취소되었습니다")
        sys.exit(0)
