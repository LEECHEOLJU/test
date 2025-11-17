# 🎉 완벽한 Vercel 배포 시스템 구축 완료!

**CGV IMAX 예매 알림 시스템 - 최종 완성본**

---

## ✅ 완성된 시스템

### 🌟 **Vercel만으로 100% 실행 가능!**

- ✅ **Vercel**: 무료 호스팅 (Serverless Functions + Cron Jobs)
- ✅ **Supabase**: 무료 데이터베이스 (PostgreSQL 500MB)
- ✅ **Gmail**: 무료 이메일 발송
- ❌ **추가 인프라 불필요!**

---

## 📊 환경변수 완벽 정리

### 필수 환경변수 (6개만!)

| 번호 | 이름 | 용도 | 설명 |
|-----|------|------|------|
| 1 | `FLASK_SECRET_KEY` | 로그인 세션 암호화 | Flask 사용자 로그인 필수 |
| 2 | `DATABASE_URL` | 데이터베이스 | Supabase PostgreSQL URL |
| 3 | `SENDER_EMAIL` | 이메일 발송 | Gmail 주소 |
| 4 | `SENDER_PASSWORD` | 이메일 인증 | Gmail 앱 비밀번호 (16자) |
| 5 | `ADMIN_PASSWORD` | 웹 로그인 | 관리자 비밀번호 |
| 6 | `USE_MOCK_CRAWLER` | CGV 크롤링 모드 | True=테스트, False=실제 |

### 권장 환경변수 (1개)

| 번호 | 이름 | 용도 | 필요성 |
|-----|------|------|--------|
| 7 | `CRON_SECRET` | Cron Job 보안 | 권장 (외부 호출 방지) |

### 선택 환경변수 (2개)

| 번호 | 이름 | 용도 | 필요성 |
|-----|------|------|--------|
| 8 | `TELEGRAM_BOT_TOKEN` | 텔레그램 알림 | 선택 (이메일로 충분) |
| 9 | `DISCORD_WEBHOOK_URL` | 디스코드 알림 | 선택 (이메일로 충분) |

---

## 📚 완벽한 문서 세트

### 1. 배포 가이드

#### 📘 [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)
**Vercel 배포 완전 가이드 (15-20분)**
- Vercel 계정 생성부터 배포까지 전 과정
- 환경변수 입력 방법 상세 설명
- 문제 해결 섹션 포함

#### 📗 [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)
**Supabase 무료 데이터베이스 설정 (5분)**
- 계정 생성부터 URL 복사까지
- Connection Pooling 설정 방법
- 비밀번호 분실 시 복구 방법
- 초보자도 쉽게 따라할 수 있는 가이드

#### 📕 [INITIAL_SETUP_GUIDE.md](INITIAL_SETUP_GUIDE.md)
**배포 후 초기 세팅 가이드**
- 첫 접속 및 로그인
- 이메일 알림 설정
- 영화 선택 및 모니터링 시작

### 2. 운영 및 관리

#### 🛠️ [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md)
**유지보수 및 운영 완전 가이드**
- 일상/주간/월간 운영 체크리스트
- 사용자 관리 방법
- 코드 수정 및 배포
- 모니터링 및 로그 확인
- 문제 해결
- 백업 및 복구
- 보안 관리

### 3. 환경설정

#### ⚙️ [.env.example](.env.example)
**환경변수 설정 완전 가이드**
- 필수/권장/선택 환경변수 명확 구분
- 각 변수의 용도 상세 설명
- Gmail 앱 비밀번호 생성 방법
- Supabase URL 형식 예시

---

## 🛠️ 관리 도구

### 1. 이메일 테스트 도구

```bash
python test_email.py
```

**기능:**
- ✅ Gmail 설정 자동 검증
- ✅ SMTP 연결 테스트
- ✅ 앱 비밀번호 형식 확인
- ✅ 테스트 이메일 발송
- ✅ 상세한 문제 해결 가이드

### 2. 사용자 관리 스크립트

```bash
python manage_users.py
```

**기능:**
- ✅ 사용자 목록 조회
- ✅ 새 사용자 추가
- ✅ 비밀번호 변경
- ✅ 사용자 삭제
- ✅ 관리자 권한 토글

---

## 🚀 배포 프로세스 (단 3단계!)

### 1단계: Supabase 설정 (5분)

```
1. https://supabase.com 접속
2. GitHub으로 로그인
3. New Project 생성
4. Database URL 복사
```

👉 **[SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) 참조**

### 2단계: Vercel 배포 (5분)

```
1. https://vercel.com 접속
2. GitHub 저장소 Import
3. 환경변수 6개 입력
4. Deploy 클릭!
```

👉 **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md) 참조**

### 3단계: 초기 세팅 (5분)

```
1. 배포된 URL 접속
2. admin 로그인
3. 이메일 설정
4. 영화 선택 및 모니터링 시작
```

👉 **[INITIAL_SETUP_GUIDE.md](INITIAL_SETUP_GUIDE.md) 참조**

**전체 소요 시간: 약 15분!**

---

## 💰 비용 (완전 무료!)

### Vercel Free Plan
- ✅ 100GB 대역폭/월
- ✅ Serverless Functions 무제한
- ✅ Cron Jobs 지원
- ✅ 자동 HTTPS
- **비용: $0**

### Supabase Free Plan
- ✅ 500MB 데이터베이스
- ✅ 2GB 전송량/월
- ✅ 무제한 API 요청
- ✅ 자동 백업 (1일)
- **비용: $0**

### Gmail
- ✅ 이메일 발송 무료
- (일일 발송 제한 있지만 충분)
- **비용: $0**

**총 비용: $0 / 월** 🎉

---

## 🔐 보안

### 적용된 보안 조치

- ✅ 환경변수로 모든 민감 정보 관리
- ✅ `.env` 파일 GitHub 제외 (.gitignore)
- ✅ CRON_SECRET으로 Cron Job 보호
- ✅ Flask SECRET_KEY 암호화
- ✅ Password Hashing (werkzeug)
- ✅ SQL Injection 방지 (SQLAlchemy)
- ✅ HTTPS 자동 적용 (Vercel)

### 보안 권장사항

- 🔒 강력한 비밀번호 사용
- 🔒 정기적으로 비밀번호 변경 (월 1회)
- 🔒 Gmail 2단계 인증 활성화
- 🔒 CRON_SECRET 설정 (외부 호출 방지)

---

## 📖 사용자 관리

### 새 사용자 추가

#### 방법 1: 관리 스크립트 (권장)

```bash
python manage_users.py
# 메뉴에서 2 선택
```

#### 방법 2: Supabase에서 직접

```sql
-- Supabase Dashboard → SQL Editor
INSERT INTO users (username, email, password_hash, is_admin)
VALUES ('newuser', 'email@example.com', 'hash...', false);
```

### 비밀번호 변경

```bash
python manage_users.py
# 메뉴에서 3 선택
```

### 사용자 삭제

```bash
python manage_users.py
# 메뉴에서 4 선택
```

---

## 🎬 CGV 크롤링 설정

### Mock 모드 vs 실제 모드

| 모드 | USE_MOCK_CRAWLER | 설명 |
|-----|-----------------|------|
| **Mock** | `True` | 가짜 데이터 (테스트용) |
| **실제** | `False` | 실제 CGV 크롤링 |

### 크롤링 주기

- **기본**: 3분마다 (Vercel Cron)
- **변경 가능**: vercel.json 수정 후 재배포

### 지원 극장

- ✅ CGV 용산아이파크몰 IMAX (기본)
- ✅ CGV 강남 IMAX
- ✅ CGV 왕십리 IMAX

### ⚠️ 주의사항

- CGV 봇 정책 준수 필수
- Rate Limiting 자동 적용 (2초 간격)
- 과도한 요청 시 IP 차단 위험
- 개인 사용 목적만 허용

---

## 🔧 문제 해결

### 이메일이 안 와요

```bash
# 1. 이메일 설정 테스트
python test_email.py

# 2. Gmail 앱 비밀번호 재생성
https://myaccount.google.com/security

# 3. Vercel 환경변수 업데이트
SENDER_PASSWORD=(새 앱 비밀번호)
```

### 데이터베이스 연결 실패

```bash
# 1. Supabase URL 확인
Supabase → Settings → Database → Connection Pooling

# 2. Transaction 모드 확인

# 3. Vercel 환경변수 업데이트
DATABASE_URL=(새 URL)
```

### 영화 목록이 안 나와요

```bash
# 1. Mock 모드 확인
USE_MOCK_CRAWLER=True (테스트) or False (실제)

# 2. Vercel Logs 확인
Vercel Dashboard → Functions → Logs

# 3. CGV 웹사이트 접속 확인
http://www.cgv.co.kr/theaters/
```

---

## 📝 환경변수 설정 예시

### Vercel Dashboard에서 입력

```
Name: FLASK_SECRET_KEY
Value: AbCdEf1234567890XyZaBcDeFgHiJkLmNoPqRsTuVwXyZ
Environment: ✅ Production ✅ Preview ✅ Development

Name: DATABASE_URL
Value: postgresql://postgres.abc123:MyPassword@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
Environment: ✅ Production ✅ Preview ✅ Development

Name: SENDER_EMAIL
Value: myemail@gmail.com
Environment: ✅ Production ✅ Preview ✅ Development

Name: SENDER_PASSWORD
Value: abcdefghijklmnop
Environment: ✅ Production ✅ Preview ✅ Development

Name: ADMIN_PASSWORD
Value: MySecureP@ssw0rd!2024
Environment: ✅ Production ✅ Preview ✅ Development

Name: USE_MOCK_CRAWLER
Value: False
Environment: ✅ Production ✅ Preview ✅ Development

Name: CRON_SECRET
Value: aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE
Environment: ✅ Production ✅ Preview ✅ Development
```

---

## 🎯 핵심 포인트

### ✅ 환경변수 설명

1. **FLASK_SECRET_KEY**: 꼭 필요합니다!
   - Flask-Login 사용 (사용자 로그인 기능)
   - 세션 암호화에 필수

2. **CRON_SECRET**: 권장하지만 필수는 아닙니다
   - 설정하면: Vercel Cron만 호출 가능 (보안 강화)
   - 설정 안 하면: 누구나 `/api/cron/monitor` 호출 가능

3. **DATABASE_URL**: Supabase가 유일한 선택
   - Vercel은 SQLite 사용 불가
   - Supabase 무료 (500MB)
   - SUPABASE_SETUP_GUIDE.md 참조

### ✅ 필요한 계정

- Vercel (무료)
- Supabase (무료)
- Gmail (무료, 2단계 인증 + 앱 비밀번호)
- GitHub (이미 있음)

### ✅ 추가 인프라

**필요 없습니다!** Vercel + Supabase + Gmail로 완전히 작동합니다.

---

## 📞 도움이 필요하면

### GitHub Issues
```
https://github.com/LEECHEOLJU/CGV_IMAX_cj/issues
```

### 문서 참조
- 배포: VERCEL_DEPLOYMENT_GUIDE.md
- Supabase: SUPABASE_SETUP_GUIDE.md
- 세팅: INITIAL_SETUP_GUIDE.md
- 운영: MAINTENANCE_GUIDE.md

---

## 🎉 완성!

**이제 정말로 완벽한 프로덕션 시스템입니다!**

### 특징:
- ✅ Vercel만으로 100% 실행
- ✅ 완전 무료
- ✅ 이메일 알림 완벽 작동
- ✅ 사용자 관리 시스템 완비
- ✅ 초보자도 쉽게 배포 가능
- ✅ 유지보수 가이드 완비

### 다음 단계:

1. **[SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md) 열기**
2. **Supabase 계정 생성 및 URL 복사**
3. **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md) 열기**
4. **Vercel 배포 시작**
5. **15분 후 완료!**

**CGV IMAX 영화 예매를 절대 놓치지 마세요! 🎬🍿**

---

**작성일**: 2025-11-17
**버전**: 2.0.0 Final
**상태**: ✅ 프로덕션 준비 완료
