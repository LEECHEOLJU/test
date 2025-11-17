# ⚙️ 초기 세팅 가이드

**Vercel 배포 후 CGV IMAX 예매 알림 시스템을 처음 사용하는 방법**

---

## 📋 목차

1. [배포 후 첫 접속](#-배포-후-첫-접속)
2. [관리자 로그인](#-관리자-로그인)
3. [이메일 알림 설정](#-이메일-알림-설정)
4. [영화 선택 및 모니터링 시작](#-영화-선택-및-모니터링-시작)
5. [추가 알림 채널 설정 (선택)](#-추가-알림-채널-설정)
6. [CGV 크롤링 설정](#-cgv-크롤링-설정)
7. [테스트 및 확인](#-테스트-및-확인)

---

## 🌐 배포 후 첫 접속

### 1단계: 배포 URL 확인

Vercel 배포가 완료되면 다음과 같은 URL을 받게 됩니다:

```
https://cgv-imax-alert.vercel.app
```

또는

```
https://your-project-name.vercel.app
```

### 2단계: Health Check 확인

배포가 제대로 되었는지 확인:

1. **브라우저에서 Health Check 엔드포인트 접속:**
   ```
   https://your-app.vercel.app/health
   ```

2. **정상 응답 확인:**
   ```json
   {
     "status": "healthy",
     "service": "CGV IMAX Alert v2.0 (Vercel)",
     "timestamp": "2025-11-17T...",
     "database": "connected",
     "monitoring": false,
     "monitored_movies": 0,
     "platform": "Vercel Serverless"
   }
   ```

3. **`database: "connected"` 확인**
   - ✅ connected: 정상
   - ❌ error 또는 다른 값: 데이터베이스 설정 재확인 필요

---

## 🔐 관리자 로그인

### 1단계: 로그인 페이지 접속

```
https://your-app.vercel.app/login
```

### 2단계: 관리자 계정으로 로그인

**기본 로그인 정보:**

```
Username: admin
Password: (Vercel 환경변수에서 설정한 ADMIN_PASSWORD)
```

> ⚠️ **참고**: 환경변수 `ADMIN_PASSWORD`를 설정하지 않았다면 기본값은 `admin123`입니다.
> 보안을 위해 반드시 변경하세요!

### 3단계: 로그인 성공 확인

- 로그인 성공 시 메인 대시보드로 리디렉션
- 상단에 사용자 정보 표시

### 로그인 문제 해결

**"Invalid username or password" 오류 시:**

1. **Vercel Dashboard 확인:**
   - Settings → Environment Variables
   - `ADMIN_PASSWORD` 값 확인

2. **기본 비밀번호로 시도:**
   - Password: `admin123`
   - 로그인 후 비밀번호 변경 권장

3. **데이터베이스 확인:**
   - Supabase Dashboard → Table Editor
   - `users` 테이블에 admin 사용자 존재 확인

---

## 📧 이메일 알림 설정

### 1단계: 설정 페이지 이동

1. **상단 메뉴에서 "Settings" 클릭**
   - 또는 직접 URL 접속:
   ```
   https://your-app.vercel.app/settings
   ```

### 2단계: 알림 채널 선택

1. **"알림 채널" 섹션 찾기**
2. **Email 체크박스 선택**
3. **저장 버튼 클릭**

### 3단계: 이메일 주소 추가

1. **"알림 받을 이메일 주소" 입력 필드**
2. **본인 이메일 주소 입력**
   - 예: `myemail@gmail.com`
3. **"추가" 버튼 클릭**

4. **추가 이메일 주소 입력 (선택)**
   - 가족, 친구 이메일도 추가 가능
   - 여러 개 추가 가능

5. **입력한 이메일 목록 확인**
   - 삭제하려면 X 버튼 클릭

### 4단계: 테스트 이메일 발송

1. **"테스트 이메일 발송" 버튼 클릭**
2. **성공 메시지 확인**
3. **이메일 수신 확인**
   - 받은편지함 확인
   - 스팸 폴더도 확인
   - 발신자: Vercel 환경변수에서 설정한 `SENDER_EMAIL`

### 이메일 발송 문제 해결

**테스트 이메일이 오지 않는 경우:**

1. **Vercel 환경변수 확인:**
   - `SENDER_EMAIL`: Gmail 주소가 정확한지 확인
   - `SENDER_PASSWORD`: Gmail 앱 비밀번호 확인 (16자리, 공백 없음)

2. **Gmail 앱 비밀번호 재생성:**
   - https://myaccount.google.com/security
   - 2단계 인증 → 앱 비밀번호
   - 기존 비밀번호 삭제 후 새로 생성

3. **Vercel Logs 확인:**
   - Vercel Dashboard → Functions → Logs
   - 에러 메시지 확인

---

## 🎬 영화 선택 및 모니터링 시작

### 1단계: 메인 페이지로 이동

```
https://your-app.vercel.app
```

### 2단계: 영화 목록 새로고침

1. **"영화 목록 새로고침" 버튼 클릭**
2. **CGV 용산 IMAX 상영 영화 목록 표시**
   - Mock 모드 (`USE_MOCK_CRAWLER=True`): 가짜 데이터 표시
   - 실제 모드 (`USE_MOCK_CRAWLER=False`): 실제 CGV 데이터

### 3단계: 감시할 영화 선택

1. **원하는 영화 찾기**
   - 예: "인터스텔라", "듄: 파트 2" 등

2. **"감시 시작" 버튼 클릭**
   - 버튼이 "감시 중지"로 변경됨
   - 영화 카드에 "감시 중" 표시

3. **여러 영화 선택 가능**
   - 동시에 여러 영화 감시 가능

### 4단계: 모니터링 시작

1. **상단의 "모니터링 시작" 버튼 클릭**

2. **성공 메시지 확인:**
   ```
   모니터링 시작 (Vercel Cron 사용)
   감시 중인 영화: X개
   체크 간격: 180초 (3분)
   ```

3. **모니터링 상태 확인:**
   - 상단 상태 표시가 "감시 중"으로 변경
   - 마지막 체크 시간 표시

### 5단계: Vercel Cron Job 동작 확인

**Vercel Cron이 자동으로 실행됩니다:**

- **주기**: 3분마다
- **동작**: `/api/cron/monitor` 엔드포인트 호출
- **확인 방법**:
  1. Vercel Dashboard → 프로젝트 선택
  2. Settings → Cron Jobs
  3. 실행 이력 확인

---

## 🔔 추가 알림 채널 설정 (선택)

### Telegram 알림 설정

#### 1. Telegram 봇 생성

1. **Telegram 앱에서 @BotFather 검색**
2. **/newbot 명령어 입력**
3. **봇 이름 입력:**
   - 예: "CGV IMAX Alert"
4. **봇 Username 입력:**
   - 예: "cgv_imax_alert_bot"
5. **Bot Token 복사**
   - 예: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### 2. Chat ID 확인

1. **@userinfobot 검색**
2. **/start 명령어**
3. **Chat ID 복사**
   - 예: `123456789`

#### 3. Vercel 환경변수 추가

1. **Vercel Dashboard → Settings → Environment Variables**
2. **추가:**
   ```
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
3. **Redeploy**

#### 4. 앱 설정에서 Telegram 활성화

1. **Settings 페이지 → 알림 채널**
2. **Telegram 체크**
3. **Telegram Chat ID 입력**
4. **저장**

### Discord Webhook 알림 설정

#### 1. Discord Webhook 생성

1. **Discord 서버 설정 → 연동**
2. **웹후크 → 새 웹후크**
3. **웹후크 이름:** CGV IMAX Alert
4. **채널 선택**
5. **웹후크 URL 복사**
   - 예: `https://discord.com/api/webhooks/...`

#### 2. Vercel 환경변수 추가

1. **Vercel Dashboard → Settings → Environment Variables**
2. **추가:**
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```
3. **Redeploy**

#### 3. 앱 설정에서 Discord 활성화

1. **Settings 페이지 → 알림 채널**
2. **Discord 체크**
3. **저장**

---

## 🌐 CGV 크롤링 설정

### Mock 모드 vs 실제 모드

**Mock 모드 (기본값):**
- `USE_MOCK_CRAWLER=True`
- 가짜 데이터 사용 (테스트용)
- CGV 웹사이트에 요청하지 않음
- 예매 오픈 감지 안 됨

**실제 모드:**
- `USE_MOCK_CRAWLER=False`
- 실제 CGV 웹사이트 크롤링
- 예매 오픈 감지 가능
- ⚠️ CGV 봇 정책 준수 필요

### 실제 CGV 크롤링 활성화

1. **Vercel Dashboard → Settings → Environment Variables**

2. **`USE_MOCK_CRAWLER` 값 변경:**
   ```
   USE_MOCK_CRAWLER=False
   ```

3. **Redeploy**
   - Deployments 탭 → Redeploy

4. **확인:**
   - 메인 페이지에서 "영화 목록 새로고침"
   - 실제 CGV 용산 IMAX 상영 영화 표시

### CGV 크롤링 주의사항

⚠️ **중요: CGV 봇 정책 준수**

- **Rate Limiting**: 요청 간격 최소 2초 (자동 적용됨)
- **User-Agent**: 정상 브라우저처럼 동작 (자동 설정됨)
- **과도한 요청 금지**: 모니터링 간격 3분 이상 권장
- **상업적 이용 금지**: 개인 사용 목적만

**IP 차단 위험:**
- CGV에서 비정상적인 트래픽으로 감지 시 IP 차단 가능
- Vercel IP가 차단될 수 있음 (서비스 중단)
- 적절한 간격 유지 필수

---

## ✅ 테스트 및 확인

### 전체 시스템 테스트 체크리스트

#### 1. 데이터베이스 연결
- [ ] `/health` 접속 → `database: "connected"` 확인

#### 2. 로그인
- [ ] `/login` → admin 계정 로그인 성공

#### 3. 이메일 설정
- [ ] Settings → 이메일 주소 추가
- [ ] 테스트 이메일 발송 → 수신 확인

#### 4. 영화 목록
- [ ] 메인 페이지 → 영화 목록 새로고침
- [ ] 영화 목록 표시 확인

#### 5. 모니터링
- [ ] 영화 선택 → "감시 시작"
- [ ] "모니터링 시작" 버튼 클릭
- [ ] 상태 "감시 중"으로 변경 확인

#### 6. Dashboard
- [ ] Dashboard 페이지 접속
- [ ] 통계 표시 확인
- [ ] 차트 표시 확인

#### 7. Vercel Cron
- [ ] Vercel Dashboard → Cron Jobs
- [ ] 실행 이력 확인 (최소 3분 대기 후)

### 예매 오픈 알림 테스트 (Mock 모드)

1. **app_vercel.py 수정** (로컬에서):
   ```python
   # advanced_crawler.py의 MockCGVCrawler 클래스에서
   # check_booking_available 메서드 주석 해제
   ```

2. **GitHub Push & Redeploy**

3. **알림 수신 확인**
   - 이메일 수신
   - Telegram/Discord 수신 (설정한 경우)

---

## 🎯 다음 단계

### 일일 사용 시나리오

1. **아침:**
   - Dashboard 접속하여 어젯밤 알림 확인

2. **원하는 영화 추가:**
   - 새로운 영화가 개봉하면 감시 목록에 추가

3. **예매 오픈 알림 수신:**
   - 이메일 확인
   - 즉시 예매 링크 클릭하여 예매

4. **예매 완료 후:**
   - 해당 영화 감시 중지

### 고급 설정

1. **모니터링 간격 조정:**
   - Settings → 체크 간격 변경 (분 단위)
   - Vercel Cron 설정도 함께 변경 필요

2. **극장 추가:**
   - 코드 수정 필요
   - `models.py`의 Theater 데이터 추가

3. **알림 템플릿 커스터마이징:**
   - `notification_service.py` 수정

---

## 🔧 문제 해결

### 로그인 안됨

**해결:**
1. Supabase → Table Editor → `users` 테이블 확인
2. admin 사용자 존재 확인
3. 없다면 수동 추가 또는 `/api/init` 엔드포인트 호출 (구현 필요)

### 영화 목록 안 나옴

**해결:**
1. Mock 모드 확인 (`USE_MOCK_CRAWLER=True`)
2. Vercel Logs 확인
3. CGV 웹사이트 접속 확인

### 모니터링 시작 안됨

**해결:**
1. 이메일 주소 설정 확인
2. 감시 중인 영화 확인
3. Vercel Cron 설정 확인

### 알림 안 옴

**해결:**
1. Mock 모드에서는 알림 안 옴 (예매 오픈 감지 안 됨)
2. 실제 모드로 변경 (`USE_MOCK_CRAWLER=False`)
3. Gmail 앱 비밀번호 재확인

---

## 📚 추가 문서

- **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)** - Vercel 배포 가이드
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Supabase 설정 가이드
- **[README.md](README.md)** - 프로젝트 개요
- **[API.md](API.md)** - API 문서

---

## 🎉 완료!

축하합니다! 초기 세팅이 완료되었습니다!

이제 CGV IMAX 영화 예매를 놓치지 않고 알림을 받을 수 있습니다! 🎬

---

**버전**: 1.0.0
**최종 업데이트**: 2025-11-17
**작성자**: CGV IMAX Alert Team
