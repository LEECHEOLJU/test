"""
설정 파일 관리 모듈
config.json 파일을 읽고 쓰는 기능 제공
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class ConfigManager:
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """설정 파일이 없으면 기본 설정으로 생성"""
        if not os.path.exists(self.config_file):
            default_config = {
                "monitoring": {
                    "movie_title": "",
                    "is_running": False,
                    "last_check_time": None,
                    "last_notification": None
                },
                "email": {
                    "recipients": [],
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": ""
                },
                "crawler": {
                    "check_interval_seconds": 180,
                    "theater": "용산아이파크몰",
                    "last_crawl_status": "idle"
                }
            }
            self.save_config(default_config)

    def load_config(self) -> Dict:
        """설정 파일 로드"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            return {}

    def save_config(self, config: Dict):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 파일 저장 실패: {e}")

    # 모니터링 관련
    def get_monitoring_movie(self) -> str:
        """감시 중인 영화 제목 가져오기"""
        config = self.load_config()
        return config.get('monitoring', {}).get('movie_title', '')

    def set_monitoring_movie(self, movie_title: str):
        """감시할 영화 설정"""
        config = self.load_config()
        config['monitoring']['movie_title'] = movie_title
        self.save_config(config)

    def get_monitoring_status(self) -> bool:
        """감시 상태 가져오기"""
        config = self.load_config()
        return config.get('monitoring', {}).get('is_running', False)

    def set_monitoring_status(self, is_running: bool):
        """감시 상태 설정"""
        config = self.load_config()
        config['monitoring']['is_running'] = is_running
        self.save_config(config)

    def update_last_check_time(self):
        """마지막 체크 시간 업데이트"""
        config = self.load_config()
        config['monitoring']['last_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_config(config)

    def get_last_check_time(self) -> Optional[str]:
        """마지막 체크 시간 가져오기"""
        config = self.load_config()
        return config.get('monitoring', {}).get('last_check_time')

    def set_last_notification(self, notification: str):
        """마지막 알림 내용 저장"""
        config = self.load_config()
        config['monitoring']['last_notification'] = notification
        self.save_config(config)

    def get_last_notification(self) -> Optional[str]:
        """마지막 알림 내용 가져오기"""
        config = self.load_config()
        return config.get('monitoring', {}).get('last_notification')

    # 이메일 관련
    def get_email_recipients(self) -> List[str]:
        """이메일 수신자 목록 가져오기"""
        config = self.load_config()
        return config.get('email', {}).get('recipients', [])

    def set_email_recipients(self, recipients: List[str]):
        """이메일 수신자 목록 설정"""
        config = self.load_config()
        config['email']['recipients'] = recipients
        self.save_config(config)

    def add_email_recipient(self, email: str):
        """이메일 수신자 추가"""
        recipients = self.get_email_recipients()
        if email not in recipients:
            recipients.append(email)
            self.set_email_recipients(recipients)

    def remove_email_recipient(self, email: str):
        """이메일 수신자 제거"""
        recipients = self.get_email_recipients()
        if email in recipients:
            recipients.remove(email)
            self.set_email_recipients(recipients)

    def get_email_config(self) -> Dict:
        """이메일 설정 전체 가져오기"""
        config = self.load_config()
        return config.get('email', {})

    def update_email_credentials(self, sender_email: str, sender_password: str):
        """이메일 발신자 정보 업데이트"""
        config = self.load_config()
        config['email']['sender_email'] = sender_email
        config['email']['sender_password'] = sender_password
        self.save_config(config)

    # 크롤러 관련
    def get_crawler_config(self) -> Dict:
        """크롤러 설정 가져오기"""
        config = self.load_config()
        return config.get('crawler', {})

    def get_check_interval(self) -> int:
        """체크 간격(초) 가져오기"""
        config = self.load_config()
        return config.get('crawler', {}).get('check_interval_seconds', 180)

    def get_theater(self) -> str:
        """극장명 가져오기"""
        config = self.load_config()
        return config.get('crawler', {}).get('theater', '용산아이파크몰')

    def update_crawl_status(self, status: str):
        """크롤링 상태 업데이트"""
        config = self.load_config()
        config['crawler']['last_crawl_status'] = status
        self.save_config(config)
