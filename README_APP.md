# CGV 용산 IMAX 예매 알림 시스템

CGV 용산 IMAX 상영관의 특정 영화 예매 오픈을 자동으로 감지하여 이메일로 알림을 보내는 웹 기반 모니터링 시스템입니다.

## 주요 기능

- 🎬 CGV 용산 IMAX 상영 예정 영화 목록 조회
- 👁️ 선택한 영화의 예매 오픈 자동 감시
- 📧 예매 오픈 시 이메일 알림 발송 (여러 수신자 지원)
- 🌐 웹 UI를 통한 간편한 관리
- ⏰ 주기적 자동 확인 (3분 간격)

## 기술 스택

### 백엔드
- Python 3.10+
- Flask (웹 프레임워크)
- BeautifulSoup4 (웹 크롤링)
- APScheduler (백그라운드 작업)
- Gmail SMTP (이메일 발송)

### 프론트엔드
- HTML5
- Bootstrap 5
- Vanilla JavaScript

## 설치 방법

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd test
```

### 2. Python 가상환경 생성 (권장)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# Gmail SMTP 설정
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Flask 설정
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 크롤러 설정 (개발 시 Mock 사용)
USE_MOCK_CRAWLER=True
```

**중요: Gmail 앱 비밀번호 생성**

Gmail에서 2단계 인증이 활성화되어 있어야 합니다.
1. Google 계정 설정 → 보안 → 2단계 인증
2. 앱 비밀번호 생성
3. 생성된 16자리 비밀번호를 `SENDER_PASSWORD`에 입력

### 5. config.json 업데이트

`config.json` 파일을 열어 발신자 이메일 정보를 입력하세요:

```json
{
  "email": {
    "sender_email": "your-email@gmail.com",
    "sender_password": "your-app-password"
  }
}
```

## 실행 방법

### 개발 모드

```bash
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000`으로 접속하세요.

### 프로덕션 모드

```bash
# Gunicorn 설치
pip install gunicorn

# Gunicorn으로 실행
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 사용 방법

### 1. 이메일 설정

1. **이메일 설정** 섹션에서 알림을 받을 이메일 주소 입력
2. **추가** 버튼 클릭 (여러 개 추가 가능)
3. **저장** 버튼 클릭
4. **테스트 이메일 발송** 버튼으로 설정 확인

### 2. 영화 선택

1. **영화 목록 새로고침** 버튼 클릭
2. 감시할 영화 선택 (라디오 버튼)
3. **선택 저장** 버튼 클릭

### 3. 감시 시작

1. **감시 시작** 버튼 클릭
2. 시스템이 자동으로 3분마다 예매 오픈 여부 확인
3. 예매 오픈 감지 시 자동으로 이메일 발송

### 4. 감시 중지

1. **감시 중지** 버튼 클릭하여 모니터링 종료

## 프로젝트 구조

```
test/
├── app.py                 # Flask 메인 서버
├── config_manager.py      # 설정 관리
├── crawler.py             # CGV 크롤러
├── email_sender.py        # 이메일 발송
├── scheduler.py           # 모니터링 스케줄러
├── requirements.txt       # Python 의존성
├── config.json            # 설정 파일
├── .env                   # 환경변수 (생성 필요)
├── static/
│   ├── css/
│   │   └── style.css     # 스타일시트
│   └── js/
│       └── app.js        # 프론트엔드 로직
├── templates/
│   └── index.html        # 메인 페이지
└── README_APP.md         # 이 문서
```

## API 엔드포인트

### 영화 관리
- `GET /api/movies` - 영화 목록 조회
- `POST /api/movies/select` - 영화 선택

### 모니터링 제어
- `GET /api/monitoring/status` - 상태 조회
- `POST /api/monitoring/start` - 감시 시작
- `POST /api/monitoring/stop` - 감시 중지

### 설정
- `GET /api/settings` - 설정 조회
- `PUT /api/settings/email` - 이메일 업데이트
- `POST /api/settings/email/test` - 테스트 이메일 발송

## 개발 모드 vs 프로덕션 모드

### 개발 모드 (Mock 크롤러)
- `USE_MOCK_CRAWLER=True` 설정
- 실제 CGV 웹사이트에 접근하지 않음
- 테스트용 가상 데이터 사용
- 빠른 개발 및 테스트 가능

### 프로덕션 모드 (실제 크롤러)
- `USE_MOCK_CRAWLER=False` 설정
- 실제 CGV 웹사이트 크롤링
- CGV 웹사이트 구조에 맞춰 `crawler.py` 수정 필요

## 주의사항

### 법적/윤리적 고려사항
- CGV 이용약관 및 robots.txt 준수
- 과도한 크롤링으로 인한 서버 부하 방지
- **개인 사용 목적으로만 사용**
- 상업적 이용 금지

### 기술적 제약
- CGV 웹사이트 구조 변경 시 크롤러 수정 필요
- IP 차단 위험 (적절한 간격 유지 필요)
- Gmail 일일 발송 제한 존재

### 보안
- `.env` 파일과 `config.json`은 절대 공개 저장소에 업로드 금지
- `.gitignore`에 이미 포함되어 있음

## 트러블슈팅

### 이메일 발송 실패
1. Gmail 2단계 인증 활성화 확인
2. 앱 비밀번호 정확한지 확인
3. `.env` 파일의 `SENDER_EMAIL`과 `SENDER_PASSWORD` 확인
4. Gmail에서 "보안 수준이 낮은 앱" 설정 확인

### 크롤러 오류
1. 개발 중에는 `USE_MOCK_CRAWLER=True` 사용 권장
2. 실제 크롤러 사용 시 CGV 웹사이트 구조 확인
3. `crawler.py`의 URL과 선택자 수정 필요

### 포트 충돌
```bash
# 다른 포트 사용
PORT=8000 python app.py
```

## 향후 계획

### Phase 2 (배포)
- [ ] 에러 핸들링 강화
- [ ] 로깅 시스템 추가
- [ ] 웹서버 배포 (Gunicorn + Nginx)
- [ ] Systemd 프로세스 관리

### Phase 3 (추가 기능)
- [ ] 알림 히스토리 (SQLite DB)
- [ ] 영화 포스터 및 상세 정보
- [ ] 다중 영화 감시
- [ ] 다른 극장 지원

## 라이선스

개인 사용 목적

## 문의

이슈나 개선 사항이 있으면 GitHub Issues에 등록해주세요.

---

**버전**: 1.0.0 (MVP)
**최종 수정**: 2025-11-08
