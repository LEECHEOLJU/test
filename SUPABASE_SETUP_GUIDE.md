# 🗄️ Supabase 설정 완전 가이드

**초보자를 위한 Supabase 무료 데이터베이스 설정 가이드**

CGV IMAX 예매 알림 시스템을 위한 무료 PostgreSQL 데이터베이스 설정 방법입니다.

---

## 📋 목차

1. [Supabase란?](#-supabase란)
2. [왜 Supabase를 사용하나요?](#-왜-supabase를-사용하나요)
3. [계정 생성](#-1-계정-생성)
4. [프로젝트 생성](#-2-프로젝트-생성)
5. [데이터베이스 URL 가져오기](#-3-데이터베이스-url-가져오기)
6. [테이블 자동 생성 확인](#-4-테이블-자동-생성-확인)
7. [문제 해결](#-문제-해결)

---

## 🤔 Supabase란?

**Supabase**는 Firebase의 오픈소스 대안으로, 무료로 PostgreSQL 데이터베이스를 제공하는 서비스입니다.

### 주요 특징:
- ✅ 완전 무료 (Free Tier)
- ✅ PostgreSQL 데이터베이스
- ✅ 500MB 저장 공간
- ✅ 실시간 데이터 동기화
- ✅ API 자동 생성
- ✅ 별도 설치 불필요

---

## 💡 왜 Supabase를 사용하나요?

### Vercel의 제한사항

Vercel은 **Serverless 플랫폼**이므로:
- ❌ 파일 시스템에 데이터 저장 불가 (SQLite 사용 불가)
- ❌ 서버 재시작 시 데이터 소실
- ❌ 영구 저장소 없음

### Supabase의 장점

- ✅ 클라우드 데이터베이스 (언제든지 접근 가능)
- ✅ Vercel과 완벽 호환
- ✅ 무료 (월 500MB, 무제한 API 요청)
- ✅ 백업 자동화
- ✅ 설정 간단 (5분)

---

## 🚀 1. 계정 생성

### Step 1-1: Supabase 웹사이트 접속

브라우저에서 다음 주소로 접속:
```
https://supabase.com
```

### Step 1-2: 회원가입

1. **우측 상단 "Start your project" 클릭**

2. **Sign up 방법 선택**
   - **GitHub으로 로그인** (권장 ⭐)
     - "Continue with GitHub" 클릭
     - GitHub 계정으로 자동 로그인

   - 또는 이메일로 가입
     - 이메일 주소 입력
     - 비밀번호 설정
     - 이메일 인증

3. **로그인 완료**
   - Supabase Dashboard로 이동됩니다

---

## 📁 2. 프로젝트 생성

### Step 2-1: 새 프로젝트 생성

1. **Dashboard에서 "New Project" 클릭**
   - 화면 중앙의 큰 버튼입니다

2. **Organization 선택** (처음이라면 자동 생성됨)
   - Personal workspace 선택

### Step 2-2: 프로젝트 정보 입력

다음 정보를 입력합니다:

| 항목 | 값 | 설명 |
|-----|-----|------|
| **Name** | `cgv-imax-alert` | 프로젝트 이름 (자유롭게 설정) |
| **Database Password** | **강력한 비밀번호** | ⚠️ 꼭 저장하세요! (복구 불가) |
| **Region** | `Northeast Asia (Seoul)` | 한국과 가장 가까운 서버 |
| **Pricing Plan** | **Free** | 무료 플랜 선택 |

#### ⚠️ Database Password 주의사항:

```
비밀번호 예시: MySuper$ecureP@ssw0rd!2024

✅ 영문 대소문자 + 숫자 + 특수문자
✅ 최소 12자 이상
✅ 반드시 메모장에 저장!
✅ 나중에 변경 불가능!
```

### Step 2-3: 프로젝트 생성 시작

1. **"Create new project" 버튼 클릭**

2. **프로젝트 생성 대기**
   - 약 2-3분 소요됩니다
   - "Setting up project..." 메시지가 표시됩니다
   - 기다리는 동안 커피 한 잔 ☕

3. **생성 완료**
   - Dashboard로 자동 이동됩니다

---

## 🔗 3. 데이터베이스 URL 가져오기

**가장 중요한 단계입니다!** 이 URL을 Vercel 환경변수로 사용합니다.

### Step 3-1: Project Settings 열기

1. **왼쪽 사이드바에서 ⚙️ "Project Settings" 클릭**
   - 하단에 있는 톱니바퀴 아이콘입니다

### Step 3-2: Database 설정 페이지

1. **왼쪽 메뉴에서 "Database" 클릭**

2. **"Connection string" 섹션 찾기**
   - 페이지 중간쯤에 있습니다

### Step 3-3: Connection Pooling URL 복사

1. **"Connection Pooling" 탭 클릭** (중요!)
   - **Direct connection이 아닙니다!**
   - **Connection Pooling을 선택해야 합니다!**

2. **Mode 선택: Transaction**
   - Session 아님!
   - **Transaction 선택** ⭐

3. **URL 복사**
   ```
   postgresql://postgres.abcdefghij:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
   ```

4. **[YOUR-PASSWORD] 부분 확인**
   - `[YOUR-PASSWORD]`가 아닌 실제 비밀번호가 표시되어야 합니다
   - 만약 `[YOUR-PASSWORD]`로 표시되면:
     - "Use password from .env" 토글 해제
     - 또는 직접 비밀번호 입력

### Step 3-4: URL 저장

**⚠️ 중요: 이 URL을 안전한 곳에 저장하세요!**

```
메모장이나 암호 관리자에 저장:

DATABASE_URL=postgresql://postgres.abcdefghij:MySuper$ecureP@ssw0rd!2024@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres
```

이 URL은 나중에 Vercel 환경변수로 사용합니다.

---

## ✅ 4. 테이블 자동 생성 확인

CGV IMAX 앱은 첫 실행 시 자동으로 필요한 테이블을 생성합니다.

### 필요한 테이블 목록:

1. **users** - 사용자 정보 (admin 계정 등)
2. **movies** - 영화 정보
3. **theaters** - 극장 정보
4. **notifications** - 알림 히스토리
5. **crawl_logs** - 크롤링 로그
6. **user_preferences** - 사용자 설정

### Vercel 배포 후 자동 생성

1. **Vercel 배포가 완료되면**
   - 첫 번째 요청 시 자동으로 테이블 생성

2. **테이블 생성 확인 방법:**
   - Supabase Dashboard → Table Editor
   - 위의 6개 테이블이 보이면 성공!

### 수동으로 테이블 확인

**Supabase Dashboard에서:**

1. **왼쪽 메뉴에서 "Table Editor" 클릭**

2. **테이블 목록 확인**
   - 배포 후 몇 분 뒤에 확인하세요
   - 6개 테이블이 모두 있어야 합니다

3. **테이블이 없다면?**
   - Vercel 배포 URL에 `/health` 접속
   - 데이터베이스 초기화 트리거

---

## 🎯 완료!

축하합니다! Supabase 설정이 완료되었습니다!

### 다음 단계:

1. ✅ **복사한 DATABASE_URL 저장 확인**
2. ✅ **Vercel 배포 시 환경변수로 사용**
3. ✅ **배포 후 테이블 자동 생성 확인**

---

## ❌ 문제 해결

### 1. "Database Password를 잊어버렸어요"

**해결 방법:**

1. **Supabase Dashboard → Project Settings → Database**
2. **"Reset database password" 클릭**
3. **새 비밀번호 설정**
4. **새 Connection String 복사**
5. **Vercel 환경변수 업데이트**

### 2. "Connection String이 작동하지 않아요"

**확인 사항:**

- [ ] **Connection Pooling** 탭을 선택했나요? (Direct connection 아님!)
- [ ] **Mode가 Transaction**으로 설정되었나요?
- [ ] 비밀번호에 특수문자가 있나요?
  - URL encoding 필요할 수 있음
  - 예: `@` → `%40`, `#` → `%23`

**URL encoding 예시:**
```
원본 비밀번호: Pass@word#123
인코딩 후: Pass%40word%23123
```

### 3. "Vercel에서 데이터베이스 연결 실패"

**해결 순서:**

1. **Supabase URL 재확인**
   ```bash
   # Vercel Dashboard → Settings → Environment Variables
   # DATABASE_URL 값 확인
   ```

2. **URL 형식 확인**
   ```
   ✅ 올바른 형식:
   postgresql://postgres.[ref]:[password]@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres

   ❌ 잘못된 형식:
   postgres://... (postgresql이어야 함)
   ```

3. **Vercel Redeploy**
   - 환경변수 변경 후 반드시 Redeploy

4. **Vercel Logs 확인**
   - Functions → Logs
   - 에러 메시지 확인

### 4. "테이블이 생성되지 않아요"

**해결 방법:**

1. **Vercel 배포 URL 접속**
   ```
   https://your-app.vercel.app/health
   ```

2. **응답 확인**
   ```json
   {
     "status": "healthy",
     "database": "connected"
   }
   ```

3. **"connected" 확인 후**
   - Supabase → Table Editor
   - 테이블 생성 확인

4. **여전히 없다면:**
   - Vercel Functions Logs 확인
   - 에러 메시지 확인
   - GitHub Issue에 보고

### 5. "무료 한도를 초과했어요"

**Supabase Free Tier 제한:**
- 500MB 데이터베이스
- 2GB 데이터 전송/월
- 무제한 API 요청

**해결:**
- 오래된 알림 히스토리 삭제
- 크롤링 로그 정리
- 또는 Supabase Pro Plan 업그레이드 ($25/월)

---

## 📊 Supabase Dashboard 둘러보기

### 유용한 기능:

1. **Table Editor**
   - 데이터 직접 확인 및 수정
   - SQL 쿼리 실행

2. **SQL Editor**
   - 커스텀 SQL 쿼리 실행
   - 데이터 분석

3. **Database**
   - 백업 관리
   - 연결 정보 확인

4. **Logs**
   - 데이터베이스 활동 로그
   - 쿼리 성능 모니터링

---

## 🔐 보안 권장사항

### 1. Row Level Security (RLS) 설정

**고급 사용자용 (선택사항):**

Supabase Dashboard → Authentication → Policies

RLS를 설정하면 API를 통한 직접 접근을 제한할 수 있습니다.

### 2. 비밀번호 관리

- ✅ 비밀번호 관리자 사용 (1Password, Bitwarden 등)
- ✅ 정기적으로 비밀번호 변경
- ✅ 다른 서비스와 다른 비밀번호 사용

### 3. 환경변수 보안

- ✅ DATABASE_URL을 절대 GitHub에 커밋하지 마세요
- ✅ .env 파일을 .gitignore에 포함
- ✅ Vercel 환경변수로만 관리

---

## 💰 비용

### Free Tier (무료)

```
✅ 500MB 데이터베이스
✅ 2GB 데이터 전송/월
✅ 무제한 API 요청
✅ 7일 로그 보관
✅ 1일 백업 보관
```

### Pro Plan ($25/월)

```
✅ 8GB 데이터베이스
✅ 50GB 데이터 전송/월
✅ 30일 로그 보관
✅ 7일 백업 보관
✅ 우선 지원
```

**CGV IMAX 앱은 Free Tier로 충분합니다!**

---

## 📚 추가 리소스

- **Supabase 공식 문서**: https://supabase.com/docs
- **PostgreSQL 튜토리얼**: https://www.postgresqltutorial.com/
- **Supabase Discord**: https://discord.supabase.com/

---

## 🎉 완료!

이제 Supabase 설정이 완료되었습니다!

### 다음 단계:

1. ✅ DATABASE_URL 복사 완료
2. ➡️ **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)로 이동**
3. ➡️ Vercel 배포 시작

**모든 준비가 끝났습니다! 🚀**

---

**작성일**: 2025-11-17
**버전**: 2.0.0
**난이도**: ⭐ 초보자
