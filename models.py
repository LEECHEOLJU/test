"""
데이터베이스 모델
SQLAlchemy를 사용한 데이터베이스 스키마 정의
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Movie(db.Model):
    """영화 정보"""
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    cgv_movie_id = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    poster_url = db.Column(db.Text)
    release_date = db.Column(db.Date)
    rating = db.Column(db.String(20))  # 관람등급
    genre = db.Column(db.String(100))
    runtime = db.Column(db.Integer)  # 상영시간(분)
    director = db.Column(db.String(200))
    is_monitoring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    notifications = db.relationship('Notification', backref='movie', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'cgv_movie_id': self.cgv_movie_id,
            'title': self.title,
            'poster_url': self.poster_url,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'rating': self.rating,
            'genre': self.genre,
            'runtime': self.runtime,
            'director': self.director,
            'is_monitoring': self.is_monitoring,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Theater(db.Model):
    """극장 정보"""
    __tablename__ = 'theaters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    theater_type = db.Column(db.String(50))  # IMAX, 4DX, SCREENX 등
    cgv_theater_id = db.Column(db.String(50), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'theater_type': self.theater_type,
            'cgv_theater_id': self.cgv_theater_id,
            'is_active': self.is_active
        }


class Notification(db.Model):
    """알림 히스토리"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    notification_type = db.Column(db.String(20))  # email, telegram, discord, web
    booking_url = db.Column(db.Text)
    showtime_info = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    recipients = db.Column(JSON)  # 수신자 목록

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'movie_title': self.movie.title if self.movie else None,
            'notification_type': self.notification_type,
            'booking_url': self.booking_url,
            'showtime_info': self.showtime_info,
            'sent_at': self.sent_at.isoformat(),
            'success': self.success,
            'error_message': self.error_message,
            'recipients': self.recipients
        }


class CrawlLog(db.Model):
    """크롤링 로그"""
    __tablename__ = 'crawl_logs'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20))  # success, error, timeout
    message = db.Column(db.Text)
    movies_found = db.Column(db.Integer, default=0)
    duration = db.Column(db.Float)  # 실행 시간(초)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'message': self.message,
            'movies_found': self.movies_found,
            'duration': self.duration,
            'created_at': self.created_at.isoformat()
        }


class Settings(db.Model):
    """시스템 설정"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }


class UserPreference(db.Model):
    """사용자 설정"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    notification_channels = db.Column(JSON)  # ['email', 'telegram']
    email_addresses = db.Column(JSON)  # 이메일 주소 목록
    telegram_chat_id = db.Column(db.String(100))
    discord_webhook_url = db.Column(db.Text)
    check_interval = db.Column(db.Integer, default=180)  # 초
    language = db.Column(db.String(10), default='ko')
    timezone = db.Column(db.String(50), default='Asia/Seoul')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'theme': self.theme,
            'notification_channels': self.notification_channels or [],
            'email_addresses': self.email_addresses or [],
            'telegram_chat_id': self.telegram_chat_id,
            'discord_webhook_url': self.discord_webhook_url,
            'check_interval': self.check_interval,
            'language': self.language,
            'timezone': self.timezone,
            'updated_at': self.updated_at.isoformat()
        }
