# 🚀 Vercel 배포 완전 가이드

**CGV IMAX 예매 알림 시스템을 Vercel에 배포하는 완전한 가이드**

처음 Vercel을 사용하시는 분들을 위한 단계별 상세 가이드입니다.

---

## 📋 목차

1. [사전 준비](#-사전-준비)
2. [Supabase 데이터베이스 설정](#-supabase-데이터베이스-설정)
3. [Vercel 계정 생성 및 설정](#-vercel-계정-생성-및-설정)
4. [GitHub 저장소 연동](#-github-저장소-연동)
5. [환경변수 설정](#-환경변수-설정)
6. [배포 및 확인](#-배포-및-확인)
7. [초기 세팅 (데이터베이스 초기화)](#-초기-세팅)
8. [모니터링 시작하기](#-모니터링-시작하기)
9. [문제 해결](#-문제-해결)

---

## 🎯 사전 준비

### 필요한 것들

- [x] GitHub 계정
- [x] 이 저장소가 GitHub에 업로드되어 있어야 함
- [x] Gmail 계정 (알림용)
- [x] 인터넷 연결

### 예상 소요 시간

- **전체 과정**: 약 15-20분
- **Vercel 설정**: 5분
- **Supabase 설정**: 5분
- **환경변수 입력**: 5분
- **테스트**: 5분

---

## 📊 Supabase 데이터베이스 설정

Vercel은 서버리스 플랫폼이므로 SQLite를 사용할 수 없습니다.
무료 PostgreSQL 데이터베이스인 Supabase를 사용합니다.

### Step 1: Supabase 계정 생성

1. **Supabase 웹사이트 접속**
   - https://supabase.com 접속
   - 우측 상단 "Start your project" 클릭

2. **GitHub으로 로그인**
   - "Continue with GitHub" 클릭
   - GitHub 계정으로 로그인 (이미 로그인되어 있다면 자동 진행)

### Step 2: 새 프로젝트 생성

1. **New Project 클릭**
   - Dashboard에서 "New Project" 버튼 클릭

2. **프로젝트 정보 입력**
   ```
   Name: cgv-imax-alert (또는 원하는 이름)
   Database Password: 강력한 비밀번호 입력 (꼭 저장하세요!)
   Region: Northeast Asia (Seoul) - 한국과 가장 가까운 리전
   Pricing Plan: Free (무료)
   ```

3. **Create new project 클릭**
   - 프로젝트 생성까지 약 2분 소요

### Step 3: 데이터베이스 연결 URL 복사

1. **프로젝트 설정 열기**
   - 왼쪽 메뉴에서 ⚙️ "Project Settings" 클릭
   - "Database" 탭 클릭

2. **Connection Pooling URL 복사**
   - "Connection Pooling" 섹션 찾기
   - **Mode: Transaction** 선택
   - Connection string 복사 (아래와 비슷한 형태)
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
   ```

3. **⚠️ 중요: 이 URL을 메모장에 저장하세요!**
   - 나중에 Vercel 환경변수로 사용합니다

---

## 🌐 Vercel 계정 생성 및 설정

### Step 1: Vercel 계정 생성

1. **Vercel 웹사이트 접속**
   - https://vercel.com 접속
   - 우측 상단 "Sign Up" 클릭

2. **GitHub으로 로그인**
   - "Continue with GitHub" 클릭
   - GitHub 계정으로 로그인
   - Vercel의 GitHub 접근 권한 승인

3. **계정 정보 입력** (필요시)
   - 이름 입력
   - 사용 목적 선택 (Personal 선택)
   - Continue 클릭

---

## 🔗 GitHub 저장소 연동

### Step 1: 새 프로젝트 생성

1. **Vercel Dashboard에서**
   - "Add New..." 버튼 클릭
   - "Project" 선택

2. **Import Git Repository**
   - GitHub 저장소 목록이 표시됩니다
   - `CGV_IMAX_cj` 저장소 찾기
   - "Import" 버튼 클릭

### Step 2: 프로젝트 설정

1. **Configure Project 화면에서:**
   ```
   Project Name: cgv-imax-alert (또는 원하는 이름)
   Framework Preset: Other (자동 선택됨)
   Root Directory: ./ (기본값)
   Build Command: (비워두기)
   Output Directory: (비워두기)
   Install Command: pip install -r requirements.txt
   ```

2. **아직 Deploy 버튼을 누르지 마세요!**
   - 먼저 환경변수를 설정해야 합니다

---

## 🔐 환경변수 설정

**가장 중요한 단계입니다!**

### Step 1: Environment Variables 섹션 펼치기

- "Configure Project" 화면에서
- "Environment Variables" 섹션 클릭하여 펼치기

### Step 2: 환경변수 하나씩 추가

아래의 환경변수들을 **하나씩** 추가합니다:

#### 필수 환경변수

| Key (이름) | Value (값) | 설명 |
|-----------|-----------|------|
| `FLASK_SECRET_KEY` | 랜덤 문자열 (최소 32자) | Flask 세션 암호화 키 |
| `DATABASE_URL` | Supabase에서 복사한 URL | PostgreSQL 연결 URL |
| `SENDER_EMAIL` | your-email@gmail.com | Gmail 주소 |
| `SENDER_PASSWORD` | Gmail 앱 비밀번호 | Gmail 앱 비밀번호 (16자리) |
| `ADMIN_PASSWORD` | 강력한 비밀번호 | 관리자 로그인 비밀번호 |
| `USE_MOCK_CRAWLER` | `False` | 실제 CGV 크롤링 사용 |
| `CRON_SECRET` | 랜덤 문자열 (32자) | Cron Job 보안 키 |

#### 환경변수 생성 도구

**FLASK_SECRET_KEY 생성** (터미널에서 실행):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**CRON_SECRET 생성** (터미널에서 실행):
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Gmail 앱 비밀번호 생성 방법

1. **Google 계정 설정 접속**
   - https://myaccount.google.com/security

2. **2단계 인증 활성화**
   - "2단계 인증" 클릭
   - 화면 지시에 따라 활성화

3. **앱 비밀번호 생성**
   - "앱 비밀번호" 검색 또는 찾기
   - "앱 선택": 메일
   - "기기 선택": 기타 (맞춤 이름 - "CGV Alert" 입력)
   - "생성" 클릭
   - **16자리 비밀번호 복사** (공백 없이)

4. **Vercel 환경변수로 사용**
   - `SENDER_PASSWORD`에 16자리 비밀번호 입력

#### 선택사항 환경변수 (나중에 추가 가능)

| Key | Value | 설명 |
|-----|-------|------|
| `TELEGRAM_BOT_TOKEN` | Bot Token | 텔레그램 봇 토큰 |
| `TELEGRAM_CHAT_ID` | Chat ID | 텔레그램 채팅 ID |
| `DISCORD_WEBHOOK_URL` | Webhook URL | 디스코드 웹훅 URL |

### Step 3: 환경변수 입력 방법

1. **각 환경변수를 다음과 같이 입력:**
   - Name (이름): 위 표의 Key 입력
   - Value (값): 해당하는 값 입력
   - Environment: **Production, Preview, Development 모두 체크**
   - "Add" 버튼 클릭

2. **모든 필수 환경변수 입력 완료 후**
   - 입력한 환경변수 목록 확인
   - 오타가 없는지 재확인

### 환경변수 입력 예시

```
Name: FLASK_SECRET_KEY
Value: AbCdEf1234567890XyZaBcDeFgHiJkLmNoPqRsTuVwXyZ
Environments: ✅ Production ✅ Preview ✅ Development
```

---

## 🚀 배포 및 확인

### Step 1: 배포 시작

1. **Deploy 버튼 클릭**
   - 모든 환경변수 입력 완료 후
   - 하단의 "Deploy" 버튼 클릭

2. **배포 진행 상황 확인**
   - 빌드 로그가 실시간으로 표시됩니다
   - 약 2-3분 소요

### Step 2: 배포 성공 확인

1. **배포 완료 메시지**
   - "Congratulations! Your project has been deployed."
   - 배포된 URL 확인 (예: `https://cgv-imax-alert.vercel.app`)

2. **도메인 URL 복사**
   - 메모장에 저장해두기

### Step 3: 사이트 접속 테스트

1. **배포된 URL 접속**
   - 브라우저에서 URL 열기
   - 로딩이 조금 걸릴 수 있습니다 (첫 접속 시)

2. **Health Check 확인**
   - `https://your-app.vercel.app/health` 접속
   - 아래와 비슷한 응답이 나오면 성공:
   ```json
   {
     "status": "healthy",
     "service": "CGV IMAX Alert v2.0 (Vercel)",
     "database": "connected",
     "platform": "Vercel Serverless"
   }
   ```

---

## 🔧 초기 세팅

배포 성공 후 데이터베이스 초기화가 필요합니다.

### 방법 1: 자동 초기화 (권장)

1. **메인 페이지 접속**
   - `https://your-app.vercel.app` 접속
   - 첫 접속 시 자동으로 데이터베이스 테이블 생성

2. **로그인 페이지로 이동**
   - `/login` 경로로 이동
   - 기본 관리자 계정으로 로그인 시도

3. **기본 로그인 정보**
   ```
   Username: admin
   Password: (환경변수에서 설정한 ADMIN_PASSWORD)
   ```

### 방법 2: 수동 초기화 (문제 발생 시)

1. **Vercel Dashboard에서**
   - Functions 탭 클릭
   - `api/index.py` 함수 찾기
   - "View Logs" 클릭

2. **로그 확인**
   - 데이터베이스 초기화 로그 확인
   - 에러 메시지가 있다면 문제 해결 섹션 참조

---

## 🎬 모니터링 시작하기

### Step 1: 로그인

1. **로그인 페이지 접속**
   - `https://your-app.vercel.app/login`

2. **로그인**
   ```
   Username: admin
   Password: (설정한 ADMIN_PASSWORD)
   ```

### Step 2: 설정 페이지에서 이메일 설정

1. **설정 페이지 이동**
   - 상단 메뉴에서 "Settings" 클릭
   - 또는 `/settings` 접속

2. **이메일 주소 추가**
   - "알림 받을 이메일 주소" 입력 필드에 이메일 입력
   - "추가" 버튼 클릭
   - 여러 이메일 추가 가능

3. **테스트 이메일 발송**
   - "테스트 이메일 발송" 버튼 클릭
   - 이메일 수신 확인 (스팸 폴더도 확인)

### Step 3: 영화 선택 및 모니터링 시작

1. **메인 페이지로 이동**
   - 홈 아이콘 클릭 또는 `/` 접속

2. **영화 목록 새로고침**
   - "영화 목록 새로고침" 버튼 클릭
   - CGV 용산 IMAX 상영 영화 목록 표시

3. **감시할 영화 선택**
   - 원하는 영화의 "감시 시작" 버튼 클릭
   - 여러 영화 선택 가능

4. **모니터링 시작**
   - 상단의 "모니터링 시작" 버튼 클릭
   - 성공 메시지 확인

### Step 4: Vercel Cron Job 확인

Vercel Cron Job이 자동으로 3분마다 영화 예매 상태를 확인합니다.

1. **Vercel Dashboard에서**
   - 프로젝트 선택
   - "Settings" 탭
   - "Cron Jobs" 메뉴 (왼쪽)

2. **Cron Job 확인**
   ```
   Path: /api/cron/monitor
   Schedule: */3 * * * * (3분마다)
   Status: Active
   ```

3. **수동 테스트**
   - 브라우저에서 `/api/cron/monitor` 접속
   - 인증 에러가 나오면 정상 (보안 설정)
   - Vercel에서만 자동 실행됩니다

---

## ❌ 문제 해결

### 1. 배포 실패: "Build failed"

**원인**: Python 패키지 설치 실패

**해결**:
1. Vercel Dashboard → 프로젝트 → Settings → General
2. "Build & Development Settings" 확인
3. Install Command: `pip install -r requirements.txt`
4. Redeploy

### 2. "Database connection failed"

**원인**: DATABASE_URL 오류

**해결**:
1. Supabase에서 Connection Pooling URL 다시 복사
2. Vercel → Settings → Environment Variables
3. DATABASE_URL 값 확인 및 수정
4. Redeploy

### 3. "Login failed" 또는 404 에러

**원인**: 데이터베이스 테이블 미생성

**해결**:
1. `/health` 엔드포인트 접속하여 DB 상태 확인
2. Supabase Dashboard → Table Editor에서 테이블 확인
3. 테이블이 없다면:
   - Vercel → Functions → Logs에서 에러 확인
   - 수동으로 Supabase에서 테이블 생성 (SQL 스크립트 제공 가능)

### 4. 이메일 발송 실패

**원인**: Gmail 앱 비밀번호 오류

**해결**:
1. Gmail 앱 비밀번호 재생성
2. 공백 없이 16자리 입력했는지 확인
3. Vercel 환경변수 `SENDER_PASSWORD` 업데이트
4. Redeploy

### 5. Vercel Cron이 작동하지 않음

**원인**: CRON_SECRET 미설정 또는 오류

**해결**:
1. Vercel → Settings → Environment Variables
2. `CRON_SECRET` 확인
3. 없다면 추가:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
4. Redeploy

### 6. "Too Many Requests" 에러

**원인**: CGV 웹사이트의 Rate Limiting

**해결**:
1. `USE_MOCK_CRAWLER=True`로 변경 (테스트용)
2. 실제 사용 시 크롤링 간격 조정
3. Settings에서 체크 간격 늘리기 (5분 이상 권장)

### 7. Vercel Function Timeout

**원인**: Serverless Function 실행 시간 초과

**해결**:
1. Vercel Free Plan은 10초 제한
2. 크롤링 대상 영화 수 줄이기
3. 또는 Vercel Pro Plan 업그레이드 고려

---

## 🔄 재배포 방법

코드 수정 후 재배포:

### 자동 배포 (권장)

1. **GitHub에 Push**
   ```bash
   git add .
   git commit -m "Update configuration"
   git push origin main
   ```

2. **Vercel이 자동으로 배포**
   - GitHub Push 감지 후 자동 빌드 및 배포
   - 약 2-3분 소요

### 수동 배포

1. **Vercel Dashboard에서**
   - 프로젝트 선택
   - "Deployments" 탭
   - 최신 배포의 "..." 메뉴
   - "Redeploy" 클릭

---

## 📊 모니터링 및 로그 확인

### Vercel Dashboard에서 로그 보기

1. **프로젝트 선택**
2. **"Functions" 탭 클릭**
3. **함수 선택** (`api/index.py`)
4. **"View Logs" 클릭**

### 실시간 로그 확인

```bash
# Vercel CLI 설치 (선택사항)
npm install -g vercel

# 프로젝트 디렉토리에서
vercel logs --follow
```

---

## 🎉 완료!

축하합니다! CGV IMAX 예매 알림 시스템이 Vercel에 성공적으로 배포되었습니다!

### 다음 단계

1. ✅ 실제 영화 선택 및 모니터링 시작
2. ✅ 이메일 알림 테스트
3. ✅ Dashboard에서 통계 확인
4. ✅ 필요시 Telegram/Discord 알림 추가

### 유용한 링크

- **배포된 앱**: `https://your-app.vercel.app`
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Dashboard**: https://supabase.com/dashboard
- **GitHub Repository**: https://github.com/your-username/CGV_IMAX_cj

---

## 💡 추가 정보

### Vercel 무료 플랜 제한사항

- ✅ 100GB 대역폭/월
- ✅ Serverless Function: 10초 제한
- ✅ Cron Jobs: 지원 (제한 있음)
- ✅ 환경변수: 무제한
- ✅ 자동 HTTPS
- ✅ 무제한 배포

### 비용

- **Vercel**: 무료 (Hobby Plan)
- **Supabase**: 무료 (최대 500MB DB, 2GB 전송)
- **Gmail**: 무료

### 보안 권장사항

1. ✅ 강력한 비밀번호 사용
2. ✅ 환경변수로 모든 민감 정보 관리
3. ✅ `.env` 파일을 GitHub에 절대 올리지 않기
4. ✅ 정기적으로 비밀번호 변경
5. ✅ Supabase Row Level Security (RLS) 설정 고려

---

## 📞 도움이 필요하신가요?

- **GitHub Issues**: 저장소의 Issues 탭에서 문제 보고
- **Vercel 문서**: https://vercel.com/docs
- **Supabase 문서**: https://supabase.com/docs

---

**버전**: 1.0.0
**최종 업데이트**: 2025-11-17
**작성자**: CGV IMAX Alert Team

**이제 CGV IMAX 영화 예매를 놓치지 마세요! 🎬**
