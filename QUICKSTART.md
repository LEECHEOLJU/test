# 🚀 빠른 시작 가이드

**CGV IMAX 예매 알림 시스템을 5분 안에 실행하기**

---

## 📋 사전 준비

- Python 3.9 이상
- pip (Python 패키지 관리자)
- Git

---

## ⚡ 빠른 설치 (5분)

### 1️⃣ 저장소 클론 (이미 했다면 스킵)

```bash
git clone <repository-url>
cd test
```

### 2️⃣ 가상환경 생성 (권장)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ 의존성 설치

```bash
pip install -r requirements.txt
```

### 4️⃣ 환경변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 에디터로 열어서 수정
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

**최소 필수 설정** (나머지는 나중에):
```env
# Flask (필수)
FLASK_SECRET_KEY=my-super-secret-key-12345678901234567890

# 데이터베이스 (기본값 사용 - SQLite)
DATABASE_URL=sqlite:///cgv_alert.db

# 이메일 (선택 - 나중에 설정 가능)
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# 크롤러 (Mock 모드로 시작)
USE_MOCK_CRAWLER=True

# 초기 계정
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
```

### 5️⃣ 데이터베이스 및 사용자 초기화

```bash
python init_user.py
```

출력 예시:
```
✅ 관리자 계정이 성공적으로 생성되었습니다!
사용자명: admin
이메일:   admin@example.com
비밀번호: admin123
```

### 6️⃣ 애플리케이션 실행

```bash
python app.py
```

출력:
```
* Running on http://127.0.0.1:5000
```

### 7️⃣ 브라우저에서 접속

브라우저를 열고 접속:
```
http://localhost:5000
```

로그인:
- **사용자명**: admin
- **비밀번호**: admin123

---

## ✅ 작동 확인

### 1. 홈페이지
- 영화 목록이 표시됨 (Mock 데이터)
- 영화 선택 가능
- 모니터링 시작 버튼 작동

### 2. 대시보드
- 통계 카드 표시
- 차트 표시

### 3. 설정
- 테마 변경 가능
- 이메일 주소 설정 가능

---

## 🎯 다음 단계

### Gmail 이메일 알림 설정하기

1. **Gmail 앱 비밀번호 생성**
   - https://myaccount.google.com/security 접속
   - "2단계 인증" 활성화
   - "앱 비밀번호" 생성
   - 생성된 16자리 비밀번호 복사

2. **.env 파일 업데이트**
   ```env
   SENDER_EMAIL=your-actual-email@gmail.com
   SENDER_PASSWORD=생성한16자리비밀번호
   ```

3. **앱 재시작**
   ```bash
   # Ctrl+C로 중지
   python app.py
   ```

4. **테스트 이메일 발송**
   - http://localhost:5000/settings 접속
   - 이메일 주소 입력
   - "테스트 이메일 발송" 클릭

---

### Supabase 데이터베이스로 전환하기

로컬 SQLite 대신 클라우드 PostgreSQL 사용:

1. **Supabase 프로젝트 생성**
   - [SUPABASE_SETUP.md](SUPABASE_SETUP.md) 참조
   - 5분 안에 완료

2. **.env 파일 업데이트**
   ```env
   DATABASE_URL=postgresql://postgres.[ref]:[password]@...pooler.supabase.com:6543/postgres
   ```

3. **데이터베이스 마이그레이션**
   ```bash
   python init_user.py
   ```

---

### 실제 CGV 크롤링 활성화

⚠️ **주의**: CGV의 봇 정책을 준수하세요!

1. **.env 파일 수정**
   ```env
   USE_MOCK_CRAWLER=False
   ```

2. **재시작**
   ```bash
   python app.py
   ```

3. **확인**
   - 홈페이지에서 실제 CGV 영화 목록 표시

---

## 🐳 Docker로 실행하기

```bash
# Docker Compose 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

접속: http://localhost:5000

---

## 🔧 문제 해결

### 1. 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 다시 시도
pip install -r requirements.txt
```

### 2. 포트 5000이 이미 사용 중

```bash
# app.py 마지막 줄 수정
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # 포트 변경
```

### 3. 데이터베이스 오류

```bash
# 데이터베이스 삭제 후 재생성
rm cgv_alert.db
python init_user.py
```

### 4. 로그인 안됨

```bash
# 사용자 재생성
python init_user.py
# "y" 입력하여 비밀번호 업데이트
```

### 5. 건강 검사 실행

```bash
python health_check.py
```

모든 항목이 ✅이면 정상!

---

## 📚 더 자세한 정보

- [README.md](README.md) - 전체 개요
- [DEPLOYMENT.md](DEPLOYMENT.md) - 프로덕션 배포
- [SUPABASE_SETUP.md](SUPABASE_SETUP.md) - Supabase 연동
- [API.md](API.md) - API 문서
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - 전체 기능

---

## 🆘 도움이 필요하신가요?

### 자주 묻는 질문

**Q: 영화가 안 보여요**
A: USE_MOCK_CRAWLER=True인지 확인. Mock 모드에서는 가짜 데이터 표시.

**Q: 이메일이 안 와요**
A:
1. Gmail 앱 비밀번호를 정확히 입력했는지 확인
2. 2단계 인증이 활성화되어 있는지 확인
3. 설정 페이지에서 "테스트 이메일" 클릭해보기

**Q: 로그인 정보를 잊어버렸어요**
A: `python init_user.py` 실행 후 "y" 입력하여 비밀번호 재설정

**Q: 데이터베이스를 초기화하고 싶어요**
A:
```bash
# SQLite
rm cgv_alert.db
python init_user.py

# PostgreSQL/Supabase
# Supabase Dashboard에서 테이블 삭제 후
python init_user.py
```

---

## ✅ 체크리스트

시작 전 확인:
- [ ] Python 3.9+ 설치됨
- [ ] pip 사용 가능
- [ ] 가상환경 활성화됨 (권장)
- [ ] requirements.txt 설치 완료
- [ ] .env 파일 생성 및 설정
- [ ] `python init_user.py` 실행 완료
- [ ] `python app.py` 실행 중
- [ ] http://localhost:5000 접속 가능
- [ ] 로그인 성공

**모두 체크되었다면 준비 완료! 🎉**

---

**Made with ❤️ for CGV IMAX lovers**
**버전: 2.0.0**
**최종 업데이트: 2025-11-08**
