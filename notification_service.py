"""
통합 알림 서비스
이메일, 텔레그램, 디스코드 등 다양한 채널로 알림 발송
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import os
import asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed

# Telegram은 선택적으로 import (설치 안 되어도 작동)
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class NotificationService:
    """통합 알림 서비스"""

    def __init__(self):
        self.email_sender = EmailNotifier()
        if TELEGRAM_AVAILABLE:
            self.telegram_sender = TelegramNotifier()
        else:
            self.telegram_sender = None
        self.discord_sender = DiscordNotifier()

    async def send_notification(
        self,
        channels: List[str],
        movie_title: str,
        booking_url: str,
        theater: str,
        config: Dict
    ) -> Dict[str, bool]:
        """
        여러 채널로 알림 발송

        Args:
            channels: 알림 채널 리스트 ['email', 'telegram', 'discord']
            movie_title: 영화 제목
            booking_url: 예매 URL
            theater: 극장명
            config: 설정 정보

        Returns:
            Dict[str, bool]: 각 채널별 발송 성공 여부
        """
        results = {}

        for channel in channels:
            if channel == 'email':
                success = self.email_sender.send(
                    sender_email=config.get('sender_email'),
                    sender_password=config.get('sender_password'),
                    recipients=config.get('email_addresses', []),
                    movie_title=movie_title,
                    booking_url=booking_url,
                    theater=theater
                )
                results['email'] = success

            elif channel == 'telegram' and self.telegram_sender:
                success = await self.telegram_sender.send(
                    bot_token=config.get('telegram_bot_token'),
                    chat_id=config.get('telegram_chat_id'),
                    movie_title=movie_title,
                    booking_url=booking_url,
                    theater=theater
                )
                results['telegram'] = success

            elif channel == 'discord':
                success = self.discord_sender.send(
                    webhook_url=config.get('discord_webhook_url'),
                    movie_title=movie_title,
                    booking_url=booking_url,
                    theater=theater
                )
                results['discord'] = success

        return results


class EmailNotifier:
    """이메일 알림"""

    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send(
        self,
        sender_email: str,
        sender_password: str,
        recipients: List[str],
        movie_title: str,
        booking_url: str,
        theater: str = "CGV 용산 IMAX"
    ) -> bool:
        """이메일 발송"""
        if not recipients or not sender_email or not sender_password:
            print("이메일 설정이 없습니다.")
            return False

        subject = f"🎬 [{theater}] {movie_title} 예매 오픈!"

        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background-color: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .movie-title {{ font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px; }}
        .info {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
        .button {{ display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 예매 오픈 알림</h1>
        </div>
        <div class="content">
            <div class="movie-title">🎬 {movie_title}</div>
            <div class="info">
                <strong>📍 극장:</strong> {theater}
            </div>
            <div class="info">
                <strong>⏰ 감지 시간:</strong> {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
            </div>
            <div style="text-align: center;">
                <a href="{booking_url}" class="button">지금 바로 예매하기 🎫</a>
            </div>
        </div>
        <div class="footer">
            CGV IMAX 예매 알림 시스템<br>
            좋은 자리로 예매하세요!
        </div>
    </div>
</body>
</html>
        """.strip()

        try:
            message = MIMEMultipart('alternative')
            message['From'] = sender_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject

            html_part = MIMEText(body, 'html', 'utf-8')
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)

            print(f"✅ 이메일 발송 성공: {recipients}")
            return True

        except Exception as e:
            print(f"❌ 이메일 발송 실패: {e}")
            return False

    def send_test(self, sender_email: str, sender_password: str, recipients: List[str]) -> bool:
        """테스트 이메일"""
        if not recipients or not sender_email or not sender_password:
            return False

        subject = "✅ CGV 알림 시스템 테스트"

        body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background-color: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2 10px rgba(0,0,0,0.1); }}
        .success {{ color: #28a745; font-size: 24px; text-align: center; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success">✅ 테스트 성공!</div>
        <p>이메일 설정이 정상적으로 작동하고 있습니다.</p>
        <p>테스트 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</p>
    </div>
</body>
</html>
        """.strip()

        try:
            message = MIMEMultipart('alternative')
            message['From'] = sender_email
            message['To'] = ', '.join(recipients)
            message['Subject'] = subject

            html_part = MIMEText(body, 'html', 'utf-8')
            message.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)

            print(f"✅ 테스트 이메일 발송 성공: {recipients}")
            return True

        except Exception as e:
            print(f"❌ 테스트 이메일 발송 실패: {e}")
            return False


class TelegramNotifier:
    """텔레그램 알림"""

    async def send(
        self,
        bot_token: str,
        chat_id: str,
        movie_title: str,
        booking_url: str,
        theater: str = "CGV 용산 IMAX"
    ) -> bool:
        """텔레그램 메시지 발송"""
        if not bot_token or not chat_id:
            print("텔레그램 설정이 없습니다.")
            return False

        try:
            bot = Bot(token=bot_token)

            message = f"""
🎉 *예매 오픈 알림*

🎬 영화: *{movie_title}*
📍 극장: {theater}
⏰ 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[지금 바로 예매하기]({booking_url})
            """.strip()

            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )

            print(f"✅ 텔레그램 발송 성공")
            return True

        except Exception as e:
            print(f"❌ 텔레그램 발송 실패: {e}")
            return False


class DiscordNotifier:
    """디스코드 웹훅 알림"""

    def send(
        self,
        webhook_url: str,
        movie_title: str,
        booking_url: str,
        theater: str = "CGV 용산 IMAX"
    ) -> bool:
        """디스코드 웹훅 발송"""
        if not webhook_url:
            print("디스코드 웹훅 설정이 없습니다.")
            return False

        try:
            webhook = DiscordWebhook(url=webhook_url)

            embed = DiscordEmbed(
                title="🎉 예매 오픈 알림",
                description=f"**{movie_title}** 예매가 오픈되었습니다!",
                color=0x764ba2
            )

            embed.add_embed_field(name="🎬 영화", value=movie_title, inline=False)
            embed.add_embed_field(name="📍 극장", value=theater, inline=True)
            embed.add_embed_field(
                name="⏰ 시간",
                value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                inline=True
            )
            embed.add_embed_field(
                name="🎫 예매 링크",
                value=f"[지금 바로 예매하기]({booking_url})",
                inline=False
            )

            embed.set_footer(text="CGV IMAX 예매 알림 시스템")
            embed.set_timestamp()

            webhook.add_embed(embed)
            response = webhook.execute()

            print(f"✅ 디스코드 웹훅 발송 성공")
            return True

        except Exception as e:
            print(f"❌ 디스코드 웹훅 발송 실패: {e}")
            return False
