# 배포 가이드

## 목차
- [Render 배포](#render-배포)
- [Vercel 배포](#vercel-배포)
- [Docker 배포](#docker-배포)
- [환경변수 설정](#환경변수-설정)

## Render 배포

### 1. Render 계정 생성
[render.com](https://render.com) 에서 계정 생성

### 2. 새 Web Service 생성
1. Dashboard → New → Web Service
2. GitHub 저장소 연결
3. `render.yaml` 자동 감지

### 3. 환경변수 설정
Render 대시보드에서 Environment 섹션:

```
FLASK_SECRET_KEY=your-secret-key-here
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
USE_MOCK_CRAWLER=False
```

### 4. 데이터베이스 연결
- Render PostgreSQL 무료 플랜 생성
- `DATABASE_URL` 자동 설정됨

### 5. 배포
- `master` 브랜치에 푸시하면 자동 배포

## Docker 배포

### 로컬에서 Docker 실행

```bash
# 이미지 빌드
docker build -t cgv-alert .

# 컨테이너 실행
docker run -p 5000:5000 --env-file .env cgv-alert
```

### Docker Compose 사용

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

## 환경변수 설정

### 필수 환경변수

```env
# Flask
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=production

# 데이터베이스
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 이메일 (Gmail)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# 크롤러
USE_MOCK_CRAWLER=False

# 텔레그램 (선택)
TELEGRAM_BOT_TOKEN=your-bot-token

# 디스코드 (선택)
DISCORD_WEBHOOK_URL=your-webhook-url
```

### Gmail 앱 비밀번호 생성

1. Google 계정 → 보안
2. 2단계 인증 활성화
3. 앱 비밀번호 생성
4. 생성된 16자리 비밀번호 사용

## 프로덕션 체크리스트

- [ ] 환경변수 모두 설정
- [ ] 데이터베이스 연결 확인
- [ ] 이메일 테스트 발송
- [ ] HTTPS 설정 (Render 자동)
- [ ] 도메인 연결 (선택)
- [ ] 백업 설정
- [ ] 모니터링 설정

## 트러블슈팅

### 데이터베이스 연결 오류
```bash
# PostgreSQL 설치 확인
pip install psycopg2-binary

# 연결 문자열 확인
echo $DATABASE_URL
```

### Gunicorn 타임아웃
```bash
# timeout 늘리기
gunicorn --timeout 120 app_v2:app
```

## 성능 최적화

- Worker 수: CPU 코어 x 2 + 1
- Thread 수: 2-4
- 메모리: 최소 512MB 권장
- PostgreSQL: 최소 256MB
