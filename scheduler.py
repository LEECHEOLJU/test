"""
모니터링 스케줄러
APScheduler를 사용하여 주기적으로 CGV 크롤링 및 알림 발송
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Optional

from config_manager import ConfigManager
from crawler import CGVCrawler, MockCGVCrawler
from email_sender import EmailSender


class MovieMonitor:
    def __init__(self, use_mock: bool = True):
        self.config_manager = ConfigManager()
        self.email_sender = EmailSender()
        self.crawler = MockCGVCrawler() if use_mock else CGVCrawler()
        self.scheduler = BackgroundScheduler()
        self.notification_sent = False  # 중복 알림 방지

    def start_monitoring(self):
        """모니터링 시작"""
        if self.scheduler.running:
            print("이미 모니터링이 실행 중입니다.")
            return False

        movie_title = self.config_manager.get_monitoring_movie()
        if not movie_title:
            print("감시할 영화가 설정되지 않았습니다.")
            return False

        # 체크 간격 가져오기
        interval_seconds = self.config_manager.get_check_interval()

        # 스케줄러에 작업 추가
        self.scheduler.add_job(
            func=self.check_movie_booking,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id='movie_monitor',
            name='CGV 영화 예매 모니터링',
            replace_existing=True
        )

        # 스케줄러 시작
        self.scheduler.start()

        # 상태 업데이트
        self.config_manager.set_monitoring_status(True)
        self.notification_sent = False  # 리셋

        print(f"모니터링 시작: {movie_title} ({interval_seconds}초 간격)")
        return True

    def stop_monitoring(self):
        """모니터링 중지"""
        if not self.scheduler.running:
            print("모니터링이 실행 중이 아닙니다.")
            return False

        self.scheduler.shutdown(wait=False)
        self.config_manager.set_monitoring_status(False)
        self.notification_sent = False  # 리셋

        print("모니터링 중지")
        return True

    def check_movie_booking(self):
        """
        영화 예매 가능 여부 체크 (스케줄러 작업)
        """
        try:
            movie_title = self.config_manager.get_monitoring_movie()
            theater = self.config_manager.get_theater()

            if not movie_title:
                print("감시할 영화가 없습니다.")
                return

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {movie_title} 예매 확인 중...")

            # 예매 가능 여부 확인
            result = self.crawler.check_booking_available(movie_title, theater)

            # 마지막 체크 시간 업데이트
            self.config_manager.update_last_check_time()
            self.config_manager.update_crawl_status('success')

            # 예매 가능 & 아직 알림 안 보냄
            if result and result.get('available') and not self.notification_sent:
                booking_url = result.get('url', '')
                print(f"🎉 예매 오픈 감지! {movie_title}")

                # 이메일 발송
                self.send_notification(movie_title, booking_url)

                # 중복 알림 방지
                self.notification_sent = True

                # 마지막 알림 정보 저장
                notification_info = {
                    'movie_title': movie_title,
                    'booking_url': booking_url,
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.config_manager.set_last_notification(str(notification_info))

            elif result and result.get('available'):
                print("이미 알림을 발송했습니다.")
            else:
                print("아직 예매 오픈되지 않았습니다.")

        except Exception as e:
            print(f"모니터링 중 오류 발생: {e}")
            self.config_manager.update_crawl_status(f'error: {str(e)}')

    def send_notification(self, movie_title: str, booking_url: str):
        """
        알림 발송

        Args:
            movie_title: 영화 제목
            booking_url: 예매 URL
        """
        try:
            email_config = self.config_manager.get_email_config()
            recipients = email_config.get('recipients', [])

            if not recipients:
                print("수신자 이메일이 설정되지 않았습니다.")
                return

            sender_email = email_config.get('sender_email', '')
            sender_password = email_config.get('sender_password', '')

            if not sender_email or not sender_password:
                print("발신자 이메일 정보가 설정되지 않았습니다.")
                return

            # 이메일 발송
            success = self.email_sender.send_notification(
                sender_email=sender_email,
                sender_password=sender_password,
                recipients=recipients,
                movie_title=movie_title,
                booking_url=booking_url
            )

            if success:
                print(f"✅ 알림 이메일 발송 성공: {recipients}")
            else:
                print("❌ 알림 이메일 발송 실패")

        except Exception as e:
            print(f"알림 발송 중 오류: {e}")

    def is_running(self) -> bool:
        """모니터링 실행 상태 확인"""
        return self.scheduler.running

    def get_status(self) -> dict:
        """현재 모니터링 상태 조회"""
        return {
            'is_running': self.is_running(),
            'movie_title': self.config_manager.get_monitoring_movie(),
            'last_check_time': self.config_manager.get_last_check_time(),
            'check_interval': self.config_manager.get_check_interval(),
            'notification_sent': self.notification_sent
        }
