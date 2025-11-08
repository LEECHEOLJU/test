# 🐘 Supabase PostgreSQL 연동 가이드

CGV IMAX 예매 알림 시스템을 Supabase PostgreSQL 데이터베이스와 연동하는 방법을 설명합니다.

---

## 📋 목차

1. [Supabase란?](#supabase란)
2. [프로젝트 생성](#프로젝트-생성)
3. [데이터베이스 연결](#데이터베이스-연결)
4. [환경변수 설정](#환경변수-설정)
5. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
6. [테스트](#테스트)
7. [트러블슈팅](#트러블슈팅)

---

## 🎯 Supabase란?

**Supabase**는 Firebase의 오픈소스 대안으로, PostgreSQL 기반의 Backend-as-a-Service (BaaS)입니다.

### 주요 특징
- ✅ PostgreSQL 15+ 지원
- ✅ 무료 티어 제공 (최대 500MB)
- ✅ 자동 백업
- ✅ RESTful API 자동 생성
- ✅ 실시간 데이터베이스
- ✅ 전 세계 리전 지원

---

## 🚀 프로젝트 생성

### 1. Supabase 계정 생성

1. [supabase.com](https://supabase.com) 접속
2. **Start your project** 클릭
3. GitHub/Google 계정으로 로그인

### 2. 새 프로젝트 생성

1. Dashboard → **New Project** 클릭
2. 프로젝트 정보 입력:
   ```
   Name: cgv-imax-alert
   Database Password: [강력한 비밀번호 생성]
   Region: Northeast Asia (Seoul) - 권장
   Pricing Plan: Free
   ```
3. **Create new project** 클릭 (1-2분 소요)

---

## 🔌 데이터베이스 연결

### 1. 연결 정보 확인

1. 프로젝트 Dashboard → **Settings** → **Database**
2. **Connection string** 섹션에서 확인:

   ```
   URI (for SQLAlchemy):
   postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
   ```

### 2. 연결 문자열 형식

Supabase는 두 가지 연결 방식 제공:

#### Direct Connection (직접 연결)
```
postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
```
- Port: 5432
- 용도: 마이그레이션, 관리 작업

#### Connection Pooling (연결 풀링) - **권장**
```
postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```
- Port: 6543
- 용도: 프로덕션 애플리케이션
- 장점: 더 많은 동시 연결 지원

---

## ⚙️ 환경변수 설정

### 1. 로컬 개발 (.env)

`.env` 파일 생성:

```env
# Flask
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development

# Supabase PostgreSQL (Connection Pooling)
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres

# 이메일 (Gmail)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password

# 크롤러
USE_MOCK_CRAWLER=True

# 선택 사항
TELEGRAM_BOT_TOKEN=your-telegram-token
DISCORD_WEBHOOK_URL=your-discord-webhook
```

### 2. Render 배포

Render Dashboard에서 Environment Variables 설정:

```
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
FLASK_SECRET_KEY=production-secret-key
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
USE_MOCK_CRAWLER=False
```

### 3. Docker Compose

`docker-compose.yml` 수정:

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
      - FLASK_SECRET_KEY=your-secret-key
    # db 서비스 제거 (Supabase 사용)
```

---

## 🗄️ 데이터베이스 마이그레이션

### 방법 1: Python 스크립트 (권장)

프로젝트 루트에서 실행:

```bash
# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 테이블 생성
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ 데이터베이스 테이블 생성 완료')"
```

### 방법 2: Supabase SQL Editor

1. Supabase Dashboard → **SQL Editor**
2. 아래 SQL 실행:

```sql
-- 극장 테이블
CREATE TABLE IF NOT EXISTS theaters (
    id SERIAL PRIMARY KEY,
    theater_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(100),
    theater_type VARCHAR(50),
    area_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 영화 테이블
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    cgv_movie_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    poster_url TEXT,
    rating VARCHAR(50),
    genre VARCHAR(200),
    runtime INTEGER,
    director VARCHAR(200),
    release_date DATE,
    is_monitoring BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 알림 테이블
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id),
    movie_title VARCHAR(200) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    recipient VARCHAR(200),
    booking_url TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- 크롤링 로그 테이블
CREATE TABLE IF NOT EXISTS crawl_logs (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER REFERENCES movies(id),
    movie_title VARCHAR(200),
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- 사용자 설정 테이블
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    theme VARCHAR(20) DEFAULT 'auto',
    notification_channels TEXT,
    email_addresses TEXT,
    check_interval INTEGER DEFAULT 180,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 테이블 (인증용)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_movies_monitoring ON movies(is_monitoring);
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_crawl_logs_checked_at ON crawl_logs(checked_at DESC);

-- 업데이트 트리거 (updated_at 자동 갱신)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 완료 메시지
SELECT '✅ 데이터베이스 테이블 생성 완료' as status;
```

---

## 🧪 테스트

### 연결 테스트

```python
# test_supabase.py
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# postgres:// → postgresql:// 변환
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# 연결 테스트
try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✅ Supabase 연결 성공!")
        print(f"📊 PostgreSQL 버전: {version}")

        # 테이블 확인
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        print(f"📋 테이블 목록: {', '.join(tables)}")

except Exception as e:
    print(f"❌ 연결 실패: {e}")
```

실행:
```bash
python test_supabase.py
```

### 애플리케이션 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속하여 확인

---

## 🔍 트러블슈팅

### 1. 연결 오류 (Connection Refused)

**증상:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결:**
1. 연결 문자열 확인:
   ```bash
   echo $DATABASE_URL
   ```
2. Pooler URL 사용 확인 (Port 6543)
3. 방화벽/VPN 확인

### 2. SSL 오류

**증상:**
```
SSL SYSCALL error: EOF detected
```

**해결:**
`DATABASE_URL`에 SSL 파라미터 추가:
```
postgresql://...?sslmode=require
```

또는 SQLAlchemy 설정:
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={'sslmode': 'require'}
)
```

### 3. Too Many Connections

**증상:**
```
FATAL: remaining connection slots are reserved
```

**해결:**
1. Connection Pooling URL 사용 (6543 포트)
2. SQLAlchemy pool 설정:
   ```python
   engine = create_engine(
       DATABASE_URL,
       pool_size=5,
       max_overflow=10,
       pool_recycle=300,
       pool_pre_ping=True
   )
   ```

### 4. 비밀번호 특수문자 이슈

**증상:**
```
Invalid connection string
```

**해결:**
비밀번호에 특수문자가 있으면 URL 인코딩:
```python
from urllib.parse import quote_plus
password = quote_plus("your-password@123")
DATABASE_URL = f"postgresql://user:{password}@host:port/db"
```

### 5. 마이그레이션 실패

**증상:**
```
Table already exists
```

**해결:**
```python
# 테이블 삭제 후 재생성 (주의: 데이터 손실)
from app import app, db
with app.app_context():
    db.drop_all()  # 모든 테이블 삭제
    db.create_all()  # 재생성
```

---

## 📊 Supabase Dashboard 활용

### 1. Table Editor
- 테이블 데이터 직접 확인/수정
- CRUD 작업 GUI로 수행

### 2. SQL Editor
- 커스텀 쿼리 실행
- 데이터 분석

### 3. Database Backups
- Settings → Database → Backups
- 매일 자동 백업 (7일 보관)

### 4. Logs
- Logs → Database
- 쿼리 성능 모니터링

---

## 🔐 보안 권장사항

1. **비밀번호 관리**
   - `.env` 파일은 `.gitignore`에 추가
   - 프로덕션용 강력한 비밀번호 사용
   - 주기적으로 비밀번호 변경

2. **Row Level Security (RLS)**
   ```sql
   -- 테이블 RLS 활성화
   ALTER TABLE movies ENABLE ROW LEVEL SECURITY;

   -- 모든 사용자 읽기 허용
   CREATE POLICY "Allow all read" ON movies
       FOR SELECT USING (true);
   ```

3. **SSL 연결 강제**
   ```python
   DATABASE_URL += "?sslmode=require"
   ```

4. **IP 화이트리스트** (유료 플랜)
   - Settings → Database → Connection pooling
   - 특정 IP만 접근 허용

---

## 📈 성능 최적화

### 1. Connection Pooling

```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,          # 동시 연결 수
    'max_overflow': 20,       # 초과 연결 수
    'pool_recycle': 300,      # 5분마다 연결 재사용
    'pool_pre_ping': True,    # 연결 상태 확인
}
```

### 2. 인덱스 최적화

```sql
-- 자주 검색하는 컬럼에 인덱스
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_notifications_movie_id ON notifications(movie_id);
```

### 3. 쿼리 최적화

```python
# Bad: N+1 쿼리
movies = Movie.query.all()
for movie in movies:
    print(movie.notifications)  # 매번 쿼리 실행

# Good: JOIN 사용
movies = Movie.query.options(
    joinedload(Movie.notifications)
).all()
```

---

## 🌍 프로덕션 배포

### Render + Supabase

1. Render에서 Web Service 생성
2. Environment Variables 설정:
   ```
   DATABASE_URL=postgresql://...pooler.supabase.com:6543/...
   ```
3. 자동 배포!

### Docker + Supabase

```yaml
# docker-compose.prod.yml
services:
  web:
    image: ghcr.io/your-username/cgv-alert:latest
    environment:
      - DATABASE_URL=${SUPABASE_DB_URL}
      - FLASK_ENV=production
```

---

## 📚 추가 리소스

- [Supabase 공식 문서](https://supabase.com/docs)
- [PostgreSQL 튜토리얼](https://www.postgresqltutorial.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy 가이드](https://flask-sqlalchemy.palletsprojects.com/)

---

## ✅ 체크리스트

배포 전 확인사항:

- [ ] Supabase 프로젝트 생성
- [ ] DATABASE_URL 환경변수 설정
- [ ] 데이터베이스 테이블 마이그레이션
- [ ] 연결 테스트 성공
- [ ] SSL 연결 확인
- [ ] 백업 설정 확인
- [ ] RLS 정책 설정 (선택)
- [ ] 인덱스 생성
- [ ] 프로덕션 환경변수 설정
- [ ] 모니터링 설정

---

**Made with ❤️ for CGV IMAX lovers**
**Version: 1.0.0**
**Last Updated: 2025-11-08**
