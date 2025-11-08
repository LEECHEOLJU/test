# API 문서

CGV IMAX 예매 알림 시스템 REST API v2.0

## Base URL
```
http://localhost:5000/api/v2
```

## 인증
현재 버전은 인증이 필요 없습니다 (단일 사용자용)

---

## 영화 관리

### GET /movies
영화 목록 조회

**Query Parameters:**
- `theater_id` (optional): 극장 ID (default: 0013)

**Response:**
```json
{
  "success": true,
  "movies": [
    {
      "id": 1,
      "cgv_movie_id": "M001",
      "title": "듄: 파트 2",
      "poster_url": "https://...",
      "rating": "12세이상관람가",
      "genre": "SF, 액션",
      "runtime": 166,
      "director": "드니 빌뇌브",
      "release_date": "2024-02-28",
      "is_monitoring": false
    }
  ],
  "count": 10
}
```

### POST /movies/{movie_id}/monitor
영화 모니터링 토글

**Response:**
```json
{
  "success": true,
  "movie": { ... }
}
```

---

## 모니터링

### POST /monitoring/start
모니터링 시작

**Response:**
```json
{
  "success": true,
  "message": "모니터링 시작됨"
}
```

### POST /monitoring/stop
모니터링 중지

**Response:**
```json
{
  "success": true,
  "message": "모니터링 중지됨"
}
```

### GET /monitoring/status
모니터링 상태 조회

**Response:**
```json
{
  "success": true,
  "active": true,
  "monitored_movies": [...],
  "count": 3
}
```

---

## 알림 히스토리

### GET /notifications
알림 히스토리 조회

**Query Parameters:**
- `page` (optional): 페이지 번호 (default: 1)
- `per_page` (optional): 페이지당 항목 수 (default: 20)

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "movie_title": "듄: 파트 2",
      "notification_type": "email",
      "booking_url": "https://...",
      "sent_at": "2024-11-08T10:30:00",
      "success": true
    }
  ],
  "total": 50,
  "pages": 3,
  "current_page": 1
}
```

---

## 통계

### GET /stats
통계 정보 조회

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_movies": 25,
    "monitored_movies": 5,
    "total_notifications": 100,
    "success_rate": 98.5,
    "recent_logs": [...]
  }
}
```

---

## 사용자 설정

### GET /preferences
사용자 설정 조회

**Response:**
```json
{
  "success": true,
  "preferences": {
    "theme": "dark",
    "notification_channels": ["email", "telegram"],
    "email_addresses": ["user@example.com"],
    "check_interval": 180
  }
}
```

### PUT /preferences
사용자 설정 업데이트

**Request Body:**
```json
{
  "theme": "dark",
  "notification_channels": ["email", "discord"],
  "email_addresses": ["user@example.com", "friend@example.com"],
  "check_interval": 300
}
```

**Response:**
```json
{
  "success": true,
  "preferences": { ... }
}
```

---

## 에러 응답

모든 에러는 다음 형식으로 반환됩니다:

```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### HTTP 상태 코드
- `200 OK`: 성공
- `400 Bad Request`: 잘못된 요청
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 오류

---

## 예제

### cURL
```bash
# 영화 목록 조회
curl http://localhost:5000/api/v2/movies

# 영화 모니터링 시작
curl -X POST http://localhost:5000/api/v2/movies/1/monitor

# 모니터링 시작
curl -X POST http://localhost:5000/api/v2/monitoring/start
```

### JavaScript (Fetch)
```javascript
// 영화 목록 조회
const response = await fetch('/api/v2/movies');
const data = await response.json();

// 설정 업데이트
await fetch('/api/v2/preferences', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    theme: 'dark',
    email_addresses: ['user@example.com']
  })
});
```

### Python (requests)
```python
import requests

# 영화 목록
r = requests.get('http://localhost:5000/api/v2/movies')
movies = r.json()['movies']

# 모니터링 시작
requests.post('http://localhost:5000/api/v2/monitoring/start')
```
