"""
이메일 발송 모듈
Gmail SMTP를 사용하여 알림 이메일 발송
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class EmailSender:
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_notification(
        self,
        sender_email: str,
        sender_password: str,
        recipients: List[str],
        movie_title: str,
        booking_url: str
    ) -> bool:
        """
        예매 오픈 알림 이메일 발송

        Args:
            sender_email: 발신자 이메일
            sender_password: 발신자 앱 비밀번호
            recipients: 수신자 이메일 리스트
            movie_title: 영화 제목
            booking_url: 예매 URL

        Returns:
            bool: 발송 성공 여부
        """
        if not recipients:
            print("수신자 이메일이 없습니다.")
            return False

        subject = f"[CGV 알림] {movie_title} 예매 오픈!"

        # 이메일 본문
        body = f"""
안녕하세요,

CGV 용산 IMAX에서 다음 영화의 예매가 오픈되었습니다!

🎬 영화: {movie_title}
📍 극장: CGV 용산 IMAX
🎫 예매 링크: {booking_url}

지금 바로 예매하세요!

---
CGV 예매 알림 시스템
감지 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        try:
            # MIME 메시지 생성
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject

            # 본문 추가
            message.attach(MIMEText(body, 'plain', 'utf-8'))

            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # TLS 보안 연결
                server.login(sender_email, sender_password)
                server.send_message(message)

            print(f"이메일 발송 성공: {recipients}")
            return True

        except Exception as e:
            print(f"이메일 발송 실패: {e}")
            return False

    def send_test_email(
        self,
        sender_email: str,
        sender_password: str,
        recipients: List[str]
    ) -> bool:
        """
        테스트 이메일 발송

        Args:
            sender_email: 발신자 이메일
            sender_password: 발신자 앱 비밀번호
            recipients: 수신자 이메일 리스트

        Returns:
            bool: 발송 성공 여부
        """
        if not recipients:
            print("수신자 이메일이 없습니다.")
            return False

        subject = "[CGV 알림] 테스트 이메일"

        body = f"""
안녕하세요,

CGV 예매 알림 시스템 테스트 이메일입니다.

이메일 설정이 정상적으로 작동하고 있습니다.

---
CGV 예매 알림 시스템
테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

        try:
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject

            message.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)

            print(f"테스트 이메일 발송 성공: {recipients}")
            return True

        except Exception as e:
            print(f"테스트 이메일 발송 실패: {e}")
            return False
