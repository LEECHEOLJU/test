# 🎬 CGV IMAX 예매 알림 시스템 v2.0

CGV 용산 IMAX 상영관의 영화 예매 오픈을 자동으로 감지하여 실시간 알림을 보내는 프로덕션 레벨 웹 애플리케이션

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

## ✨ 주요 기능

- 🎬 **다중 영화 모니터링** - 여러 영화 동시 감시
- 📧 **다중 알림 채널** - 이메일/텔레그램/디스코드
- 📊 **실시간 대시보드** - 통계 및 히스토리
- 🌙 **다크모드** - 라이트/다크 테마
- 📱 **PWA 지원** - 모바일 앱처럼 설치
- 🗄️ **데이터베이스** - PostgreSQL/SQLite

## 🚀 빠른 시작

**5분 안에 실행하기!** 👉 [QUICKSTART.md](QUICKSTART.md)

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 설정 수정

# 3. 데이터베이스 및 사용자 초기화
python init_user.py

# 4. 에셋 파일 생성 (선택)
python setup_assets.py

# 5. 실행
python app.py

# 6. 브라우저에서 접속
# http://localhost:5000
```

**기본 로그인 정보**: admin / admin123

## 📚 문서

- **[QUICKSTART.md](QUICKSTART.md)** - ⚡ 5분 빠른 시작 가이드
- [DEPLOYMENT.md](DEPLOYMENT.md) - 배포 가이드
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Supabase 연동 가이드
- [API.md](API.md) - API 문서
- [PRD.md](PRD.md) - 프로젝트 요구사항
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 프로젝트 개요
- [COMPLETION_SUMMARY.md](COMPLETION_SUMMARY.md) - 완성 요약

## 🐳 Docker

```bash
docker-compose up -d
```

## ⚙️ 환경변수

```env
FLASK_SECRET_KEY=your-key
DATABASE_URL=postgresql://...
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

---

**버전**: 2.0.0 | Made with ❤️ for movie lovers