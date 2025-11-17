# 🛠️ 유지보수 및 운영 가이드

**CGV IMAX 예매 알림 시스템 완전 운영 매뉴얼**

---

## 📋 목차

1. [일상 운영](#-일상-운영)
2. [사용자 관리](#-사용자-관리)
3. [코드 수정 및 배포](#-코드-수정-및-배포)
4. [모니터링 및 로그 확인](#-모니터링-및-로그-확인)
5. [문제 해결](#-문제-해결)
6. [백업 및 복구](#-백업-및-복구)
7. [보안 관리](#-보안-관리)

---

## 📅 일상 운영

### 매일 해야 할 일

#### 1. 대시보드 확인

**접속:**
```
https://your-app.vercel.app/dashboard
```

**확인 사항:**
- ✅ 감시 중인 영화 개수
- ✅ 최근 알림 발송 이력
- ✅ 크롤링 성공률
- ✅ 시스템 정상 작동 여부

#### 2. 이메일 확인

- ✅ 테스트 이메일 정상 수신 확인
- ✅ 스팸 폴더에 알림이 가지 않는지 확인

### 주간 점검

#### 1. Vercel Logs 확인

**접속:**
```
Vercel Dashboard → 프로젝트 → Functions → Logs
```

**확인 사항:**
- ✅ 에러 로그 없는지 확인
- ✅ Cron Job 정상 실행 확인
- ✅ 데이터베이스 연결 정상 확인

#### 2. Supabase 사용량 확인

**접속:**
```
Supabase Dashboard → 프로젝트 → Settings → Usage
```

**확인 사항:**
- ✅ 데이터베이스 용량 (500MB 이하)
- ✅ API 요청 수
- ✅ 데이터 전송량 (2GB/월 이하)

### 월간 점검

#### 1. 오래된 데이터 정리

**Supabase Dashboard에서:**
```sql
-- 30일 이상 된 알림 히스토리 삭제
DELETE FROM notifications
WHERE sent_at < NOW() - INTERVAL '30 days';

-- 30일 이상 된 크롤링 로그 삭제
DELETE FROM crawl_logs
WHERE created_at < NOW() - INTERVAL '30 days';
```

#### 2. 비밀번호 변경

- ✅ 관리자 비밀번호 변경
- ✅ Gmail 앱 비밀번호 재생성 (선택)

---

## 👥 사용자 관리

### 사용자 관리 스크립트 사용

**로컬에서 실행:**

```bash
python manage_users.py
```

### 1. 사용자 목록 조회

```bash
# manage_users.py 실행 후 메뉴에서 1 선택
```

**출력 예시:**
```
ID    Username             Email                          Admin      Created
------------------------------------------------------------------------------------
1     admin                admin@example.com              ✅ 관리자   2025-11-17 10:00
2     john                 john@example.com               일반       2025-11-17 11:00
```

### 2. 새 사용자 추가

**방법 1: 관리 스크립트 사용** (권장)

```bash
python manage_users.py
# 메뉴에서 2 선택
```

**입력:**
```
Username: newuser
Email: newuser@example.com
비밀번호: SecureP@ssw0rd!
비밀번호 확인: SecureP@ssw0rd!
관리자 권한 부여? (y/n): n
```

**방법 2: Supabase에서 직접 추가** (고급)

```sql
-- Supabase Dashboard → SQL Editor

-- 비밀번호 해시 생성 (Python 필요)
-- python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"

INSERT INTO users (username, email, password_hash, is_admin, created_at)
VALUES ('newuser', 'newuser@example.com', 'pbkdf2:sha256:...', false, NOW());
```

### 3. 비밀번호 변경

```bash
python manage_users.py
# 메뉴에서 3 선택

Username: admin
새 비밀번호: NewP@ssw0rd!2025
새 비밀번호 확인: NewP@ssw0rd!2025
```

### 4. 사용자 삭제

```bash
python manage_users.py
# 메뉴에서 4 선택

삭제할 Username: olduser
정말 삭제하시겠습니까? (yes 입력): yes
```

### 5. 관리자 권한 변경

```bash
python manage_users.py
# 메뉴에서 5 선택

Username: john
# 일반 → 관리자 또는 관리자 → 일반
```

---

## 💻 코드 수정 및 배포

### 로컬에서 코드 수정 후 배포

#### 1. 로컬에서 수정

```bash
# 코드 수정
nano app_vercel.py

# 로컬 테스트 (선택)
python app.py
```

#### 2. GitHub에 Push

```bash
git add .
git commit -m "기능 추가: 설명"
git push origin main
```

#### 3. 자동 배포

- ✅ Vercel이 자동으로 감지
- ✅ 자동 빌드 및 배포
- ✅ 약 2-3분 소요

#### 4. 배포 확인

```
Vercel Dashboard → Deployments
→ 최신 배포 상태 확인
```

### 환경변수 변경

#### 1. Vercel Dashboard 접속

```
Vercel Dashboard → 프로젝트 → Settings → Environment Variables
```

#### 2. 변수 수정

- 수정할 변수 찾기
- "Edit" 클릭
- 새 값 입력
- "Save" 클릭

#### 3. Redeploy

```
Vercel Dashboard → Deployments
→ 최신 배포의 "..." 메뉴
→ "Redeploy" 클릭
```

### Vercel Cron 주기 변경

#### vercel.json 수정:

```json
{
  "crons": [
    {
      "path": "/api/cron/monitor",
      "schedule": "*/5 * * * *"  // 5분마다 (기존 3분에서 변경)
    }
  ]
}
```

#### GitHub Push:

```bash
git add vercel.json
git commit -m "Cron 주기 변경: 3분 → 5분"
git push origin main
```

---

## 📊 모니터링 및 로그 확인

### Vercel Logs

#### 실시간 로그 확인

```
Vercel Dashboard → 프로젝트 → Functions → api/index.py → View Logs
```

#### 로그 필터링

```
# 에러만 보기
ERROR

# 특정 영화 검색
영화제목

# 시간대 필터
2025-11-17
```

### Supabase 로그

#### 데이터베이스 활동 로그

```
Supabase Dashboard → 프로젝트 → Logs → Database
```

#### SQL 쿼리로 로그 확인

```sql
-- 최근 알림 10개
SELECT * FROM notifications
ORDER BY sent_at DESC
LIMIT 10;

-- 최근 크롤링 로그 10개
SELECT * FROM crawl_logs
ORDER BY created_at DESC
LIMIT 10;

-- 오늘 발송된 알림 개수
SELECT COUNT(*) FROM notifications
WHERE DATE(sent_at) = CURRENT_DATE;
```

### 시스템 Health Check

```bash
curl https://your-app.vercel.app/health
```

**정상 응답:**
```json
{
  "status": "healthy",
  "service": "CGV IMAX Alert v2.0 (Vercel)",
  "database": "connected",
  "monitoring": true,
  "monitored_movies": 3
}
```

---

## ❌ 문제 해결

### 이메일이 발송되지 않음

#### 진단:

```bash
# 로컬에서 테스트
python test_email.py
```

#### 해결:

1. **Gmail 앱 비밀번호 재생성**
   ```
   https://myaccount.google.com/security
   → 앱 비밀번호 → 기존 삭제 → 새로 생성
   ```

2. **Vercel 환경변수 업데이트**
   ```
   SENDER_PASSWORD=(새 앱 비밀번호)
   → Redeploy
   ```

3. **SMTP 연결 확인**
   ```python
   python test_email.py
   ```

### Cron Job이 실행되지 않음

#### 진단:

```
Vercel Dashboard → Settings → Cron Jobs
→ 실행 이력 확인
```

#### 해결:

1. **Cron 설정 확인**
   ```json
   // vercel.json
   {
     "crons": [
       {
         "path": "/api/cron/monitor",
         "schedule": "*/3 * * * *"
       }
     ]
   }
   ```

2. **CRON_SECRET 확인**
   ```
   Vercel → Environment Variables → CRON_SECRET 확인
   ```

3. **수동 트리거 테스트**
   ```bash
   curl https://your-app.vercel.app/api/cron/monitor
   # 401 Unauthorized = 정상 (CRON_SECRET 필요)
   ```

### 데이터베이스 연결 실패

#### 진단:

```bash
curl https://your-app.vercel.app/health
```

#### 해결:

1. **Supabase 상태 확인**
   ```
   Supabase Dashboard → 프로젝트 상태 확인
   ```

2. **DATABASE_URL 재확인**
   ```
   Supabase → Settings → Database → Connection Pooling
   → Transaction 모드 URL 복사
   → Vercel 환경변수 업데이트
   ```

3. **Redeploy**

### 영화 목록이 표시되지 않음

#### 진단:

1. **Mock 모드 확인**
   ```
   Vercel → Environment Variables → USE_MOCK_CRAWLER
   → True = Mock 데이터 (테스트용)
   → False = 실제 CGV 데이터
   ```

2. **Vercel Logs 확인**
   ```
   Functions → Logs → 에러 메시지 확인
   ```

#### 해결:

1. **CGV 웹사이트 접속 확인**
   ```
   http://www.cgv.co.kr/theaters/
   → 정상 작동 확인
   ```

2. **Rate Limiting 확인**
   ```
   너무 자주 요청하면 CGV에서 차단 가능
   → 모니터링 간격 늘리기 (5분 이상)
   ```

---

## 💾 백업 및 복구

### Supabase 자동 백업

**Free Tier:**
- ✅ 1일 자동 백업 (최근 1일분만 보관)

**백업 확인:**
```
Supabase Dashboard → 프로젝트 → Database → Backups
```

### 수동 백업

#### 1. 데이터베이스 전체 Export

```
Supabase Dashboard → Table Editor
→ 각 테이블 → Export → CSV
```

#### 2. SQL Dump

```bash
# PostgreSQL 도구 필요
pg_dump "postgresql://postgres...pooler.supabase.com:6543/postgres" > backup.sql
```

### 복구

#### 1. CSV에서 복구

```
Supabase Dashboard → Table Editor
→ 테이블 선택 → Import → CSV 파일 업로드
```

#### 2. SQL에서 복구

```bash
psql "postgresql://postgres...pooler.supabase.com:6543/postgres" < backup.sql
```

---

## 🔐 보안 관리

### 정기 보안 점검 (월 1회)

#### 1. 비밀번호 변경

```bash
# 관리자 비밀번호
python manage_users.py → 3 선택

# Gmail 앱 비밀번호 재생성
https://myaccount.google.com/security
```

#### 2. 환경변수 보안

```
✅ FLASK_SECRET_KEY 재생성
✅ CRON_SECRET 재생성
✅ .env 파일이 GitHub에 없는지 확인
```

#### 3. Supabase 보안

```
Supabase Dashboard → Settings → API
→ Service Role Key 재생성 (필요시)
```

### GitHub 보안

#### .gitignore 확인

```bash
cat .gitignore | grep .env
# .env가 포함되어 있어야 함
```

#### 이미 커밋된 .env 제거

```bash
git rm --cached .env
git commit -m "Remove .env from git"
git push origin main
```

### Vercel 보안

#### Environment Variables 접근 제한

```
Vercel Dashboard → 프로젝트 → Settings
→ General → "Deployment Protection"
→ 활성화 (선택)
```

---

## 📈 성능 최적화

### 데이터베이스 최적화

#### 인덱스 확인 및 생성

```sql
-- Supabase SQL Editor

-- 자주 조회하는 컬럼에 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_movies_is_monitoring
ON movies(is_monitoring);

CREATE INDEX IF NOT EXISTS idx_notifications_sent_at
ON notifications(sent_at DESC);
```

#### 오래된 데이터 자동 삭제

```sql
-- 90일 이상 된 알림 히스토리 삭제
DELETE FROM notifications
WHERE sent_at < NOW() - INTERVAL '90 days';
```

### Vercel 성능 모니터링

```
Vercel Dashboard → Analytics
→ 페이지 로딩 속도 확인
→ Function 실행 시간 확인
```

---

## 📞 문제 발생 시 연락처

### GitHub Issues

```
https://github.com/your-username/CGV_IMAX_cj/issues
```

### Vercel Support

```
https://vercel.com/support
```

### Supabase Support

```
https://supabase.com/support
Discord: https://discord.supabase.com/
```

---

## 📚 추가 리소스

- **[README.md](README.md)** - 프로젝트 개요
- **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)** - 배포 가이드
- **[INITIAL_SETUP_GUIDE.md](INITIAL_SETUP_GUIDE.md)** - 초기 설정
- **[SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)** - Supabase 설정

---

## ✅ 유지보수 체크리스트

### 일일

- [ ] 대시보드 확인
- [ ] 알림 발송 확인

### 주간

- [ ] Vercel Logs 확인
- [ ] Supabase 사용량 확인
- [ ] 테스트 이메일 발송

### 월간

- [ ] 오래된 데이터 정리
- [ ] 비밀번호 변경
- [ ] 백업 확인
- [ ] 보안 점검

### 분기

- [ ] 전체 시스템 점검
- [ ] 코드 업데이트 확인
- [ ] 의존성 패키지 업데이트

---

**작성일**: 2025-11-17
**버전**: 1.0.0
**작성자**: CGV IMAX Alert Team
