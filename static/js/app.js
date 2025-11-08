// CGV IMAX 예매 알림 시스템 - 프론트엔드 JavaScript

const API_BASE_URL = '';  // 같은 도메인에서 실행

// 전역 변수
let emailList = [];
let selectedMovie = '';
let statusCheckInterval = null;

// ============================================================================
// 초기화
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('CGV IMAX 예매 알림 시스템 시작');

    // 현재 시간 표시
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);

    // 초기 데이터 로드
    loadMovies();
    loadSettings();
    loadMonitoringStatus();

    // 주기적으로 상태 확인 (10초마다)
    statusCheckInterval = setInterval(loadMonitoringStatus, 10000);
});

// ============================================================================
// 유틸리티 함수
// ============================================================================

function updateCurrentTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeStr;
}

function showToast(message, type = 'info') {
    const toastEl = document.getElementById('toast');
    const toastBody = document.getElementById('toast-body');

    toastBody.textContent = message;

    // 색상 설정
    toastEl.className = 'toast';
    if (type === 'success') {
        toastEl.classList.add('bg-success', 'text-white');
    } else if (type === 'error') {
        toastEl.classList.add('bg-danger', 'text-white');
    } else if (type === 'warning') {
        toastEl.classList.add('bg-warning');
    }

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// ============================================================================
// 영화 관리
// ============================================================================

async function loadMovies() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/movies`);
        const data = await response.json();

        if (data.success) {
            displayMovies(data.movies);
        } else {
            showToast('영화 목록 로드 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('영화 목록 로드 오류:', error);
        showToast('영화 목록 로드 중 오류 발생', 'error');
    }
}

function displayMovies(movies) {
    const moviesList = document.getElementById('movies-list');

    if (movies.length === 0) {
        moviesList.innerHTML = '<p class="text-muted">상영 예정 영화가 없습니다.</p>';
        return;
    }

    let html = '<div class="list-group">';
    movies.forEach(movie => {
        const isChecked = movie.title === selectedMovie ? 'checked' : '';
        html += `
            <label class="list-group-item list-group-item-action">
                <input class="form-check-input me-2" type="radio" name="movie" value="${movie.title}" ${isChecked}>
                ${movie.title}
            </label>
        `;
    });
    html += '</div>';

    moviesList.innerHTML = html;
}

async function selectMovie() {
    const selectedRadio = document.querySelector('input[name="movie"]:checked');

    if (!selectedRadio) {
        showToast('영화를 선택해주세요.', 'warning');
        return;
    }

    const movieTitle = selectedRadio.value;

    try {
        const response = await fetch(`${API_BASE_URL}/api/movies/select`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ movie_title: movieTitle })
        });

        const data = await response.json();

        if (data.success) {
            selectedMovie = movieTitle;
            showToast(data.message, 'success');
            loadMonitoringStatus();
        } else {
            showToast('영화 선택 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('영화 선택 오류:', error);
        showToast('영화 선택 중 오류 발생', 'error');
    }
}

// ============================================================================
// 모니터링 제어
// ============================================================================

async function loadMonitoringStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/monitoring/status`);
        const data = await response.json();

        if (data.success) {
            updateMonitoringUI(data.status, data.last_notification);
        }
    } catch (error) {
        console.error('상태 조회 오류:', error);
    }
}

function updateMonitoringUI(status, lastNotification) {
    // 영화 정보 업데이트
    const movieEl = document.getElementById('monitoring-movie');
    movieEl.textContent = status.movie_title || '없음';
    selectedMovie = status.movie_title;

    // 상태 배지 업데이트
    const statusEl = document.getElementById('monitoring-status');
    if (status.is_running) {
        statusEl.textContent = '감시 중';
        statusEl.className = 'badge bg-success';
    } else {
        statusEl.textContent = '중지됨';
        statusEl.className = 'badge bg-secondary';
    }

    // 마지막 체크 시간
    const lastCheckEl = document.getElementById('last-check-time');
    lastCheckEl.textContent = status.last_check_time || '-';

    // 버튼 상태 업데이트
    const startBtn = document.getElementById('btn-start-monitoring');
    const stopBtn = document.getElementById('btn-stop-monitoring');

    if (status.is_running) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    // 최근 알림 표시
    if (lastNotification) {
        displayNotification(lastNotification);
    }
}

async function startMonitoring() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/monitoring/start`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            loadMonitoringStatus();
        } else {
            showToast('감시 시작 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('감시 시작 오류:', error);
        showToast('감시 시작 중 오류 발생', 'error');
    }
}

async function stopMonitoring() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/monitoring/stop`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            loadMonitoringStatus();
        } else {
            showToast('감시 중지 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('감시 중지 오류:', error);
        showToast('감시 중지 중 오류 발생', 'error');
    }
}

function displayNotification(notification) {
    const card = document.getElementById('notification-card');
    const content = document.getElementById('notification-content');
    const link = document.getElementById('booking-link');

    // notification이 문자열인 경우 파싱
    let notificationData;
    if (typeof notification === 'string') {
        try {
            // Python dict 형식을 JSON으로 변환
            const jsonStr = notification.replace(/'/g, '"');
            notificationData = JSON.parse(jsonStr);
        } catch (e) {
            console.error('알림 파싱 오류:', e);
            return;
        }
    } else {
        notificationData = notification;
    }

    if (notificationData && notificationData.booking_url) {
        content.innerHTML = `
            <p class="mb-2"><strong>🎉 예매 오픈!</strong></p>
            <p>영화: ${notificationData.movie_title}</p>
            <p>시간: ${notificationData.time}</p>
        `;
        link.href = notificationData.booking_url;
        card.style.display = 'block';
    }
}

// ============================================================================
// 이메일 설정
// ============================================================================

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`);
        const data = await response.json();

        if (data.success) {
            emailList = data.config.email.recipients || [];
            updateEmailListUI();
        }
    } catch (error) {
        console.error('설정 로드 오류:', error);
    }
}

function addEmail() {
    const emailInput = document.getElementById('email-input');
    const email = emailInput.value.trim();

    if (!email) {
        showToast('이메일 주소를 입력해주세요.', 'warning');
        return;
    }

    // 이메일 형식 검증
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast('올바른 이메일 형식이 아닙니다.', 'warning');
        return;
    }

    if (emailList.includes(email)) {
        showToast('이미 등록된 이메일입니다.', 'warning');
        return;
    }

    emailList.push(email);
    updateEmailListUI();
    emailInput.value = '';
    showToast('이메일이 추가되었습니다. 저장 버튼을 눌러주세요.', 'info');
}

function removeEmail(email) {
    emailList = emailList.filter(e => e !== email);
    updateEmailListUI();
    showToast('이메일이 삭제되었습니다. 저장 버튼을 눌러주세요.', 'info');
}

function updateEmailListUI() {
    const emailListDiv = document.getElementById('email-list');

    if (emailList.length === 0) {
        emailListDiv.innerHTML = '<p class="text-muted mb-0">등록된 이메일이 없습니다.</p>';
        return;
    }

    let html = '<div class="d-flex flex-wrap gap-2">';
    emailList.forEach(email => {
        html += `
            <span class="badge bg-primary d-flex align-items-center">
                ${email}
                <button class="btn-close btn-close-white ms-2" onclick="removeEmail('${email}')" aria-label="삭제" style="font-size: 0.7rem;"></button>
            </span>
        `;
    });
    html += '</div>';

    emailListDiv.innerHTML = html;
}

async function saveEmails() {
    if (emailList.length === 0) {
        showToast('최소 1개 이상의 이메일을 추가해주세요.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/settings/email`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recipients: emailList })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast('이메일 저장 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('이메일 저장 오류:', error);
        showToast('이메일 저장 중 오류 발생', 'error');
    }
}

async function sendTestEmail() {
    if (emailList.length === 0) {
        showToast('먼저 이메일을 추가하고 저장해주세요.', 'warning');
        return;
    }

    try {
        showToast('테스트 이메일을 발송하는 중...', 'info');

        const response = await fetch(`${API_BASE_URL}/api/settings/email/test`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast('테스트 이메일 발송 실패: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('테스트 이메일 발송 오류:', error);
        showToast('테스트 이메일 발송 중 오류 발생', 'error');
    }
}
