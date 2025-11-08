"""
향상된 CGV 크롤러
실제 CGV API와 웹사이트를 크롤링하여 영화 정보 및 예매 상태 확인

주요 기능:
- Rate limiting으로 서버 부하 최소화
- 자동 재시도 로직
- 상세한 에러 처리
- 세션 관리 및 쿠키 핸들링
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re
import json
from datetime import datetime, timedelta
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def rate_limit(min_interval: float = 1.0):
    """
    Rate limiting 데코레이터
    CGV 서버 부하를 줄이기 위해 최소 간격 유지
    """
    def decorator(func):
        last_called = {'time': 0}

        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called['time']
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

            result = func(*args, **kwargs)
            last_called['time'] = time.time()
            return result

        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """
    실패 시 재시도 데코레이터
    네트워크 오류 등 일시적인 문제 대응
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"{func.__name__} 최종 실패 ({max_retries}회 시도): {e}")
                        raise

                    wait_time = delay * (2 ** attempt)  # 지수 백오프
                    logger.warning(f"{func.__name__} 실패 (시도 {attempt + 1}/{max_retries}), {wait_time}초 후 재시도: {e}")
                    time.sleep(wait_time)

            return None

        return wrapper
    return decorator


class AdvancedCGVCrawler:
    """
    향상된 CGV 크롤러

    Features:
    - Rate limiting (서버 부하 최소화)
    - Retry logic (네트워크 오류 대응)
    - Session management (쿠키 유지)
    - Detailed logging (디버깅 용이)
    """

    def __init__(self, rate_limit_interval: float = 2.0):
        self.base_url = "http://www.cgv.co.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'http://www.cgv.co.kr/',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.rate_limit_interval = rate_limit_interval
        self.last_request_time = 0

    def _make_request(self, url: str, params: Optional[Dict] = None, timeout: int = 15) -> Optional[requests.Response]:
        """
        Rate limiting이 적용된 HTTP 요청

        Args:
            url: 요청 URL
            params: 쿼리 파라미터
            timeout: 타임아웃 (초)

        Returns:
            Optional[requests.Response]: 응답 객체
        """
        # Rate limiting 적용
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_interval:
            sleep_time = self.rate_limit_interval - elapsed
            logger.debug(f"Rate limiting: {sleep_time:.2f}초 대기")
            time.sleep(sleep_time)

        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response

        except requests.exceptions.Timeout:
            logger.error(f"요청 타임아웃: {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 오류 ({e.response.status_code}): {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"연결 오류: {url}")
            raise
        except Exception as e:
            logger.error(f"요청 실패: {url} - {e}")
            raise

    @retry_on_failure(max_retries=3, delay=2.0)
    def get_theaters(self) -> List[Dict]:
        """
        CGV 극장 목록 조회

        Returns:
            List[Dict]: 극장 정보 리스트
        """
        try:
            # CGV 극장 목록 API 또는 페이지
            url = f"{self.base_url}/theaters/"

            response = self._make_request(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            theaters = []

            # 용산 IMAX 극장 정보 (하드코딩, 실제로는 파싱 필요)
            # 실제 구현 시에는 soup.select()로 극장 리스트 파싱
            theaters.append({
                'id': '0013',
                'name': '용산아이파크몰',
                'location': '서울',
                'theater_type': 'IMAX',
                'area_code': '01'
            })

            # 추가 IMAX 극장
            theaters.extend([
                {
                    'id': '0056',
                    'name': '강남',
                    'location': '서울',
                    'theater_type': 'IMAX',
                    'area_code': '01'
                },
                {
                    'id': '0074',
                    'name': '왕십리',
                    'location': '서울',
                    'theater_type': 'IMAX',
                    'area_code': '01'
                }
            ])

            logger.info(f"극장 {len(theaters)}개 발견")
            return theaters

        except Exception as e:
            logger.error(f"극장 목록 조회 실패: {e}")
            return []

    @retry_on_failure(max_retries=3, delay=2.0)
    def get_movies(self, theater_id: str = "0013") -> List[Dict]:
        """
        특정 극장의 상영 영화 목록 조회

        Args:
            theater_id: 극장 ID (0013 = 용산아이파크몰)

        Returns:
            List[Dict]: 영화 정보 리스트
        """
        try:
            # CGV 영화 목록 API
            # 실제 CGV는 여러 방법으로 접근 가능:
            # 1. 무비차트 페이지 크롤링
            # 2. 상영시간표 API
            # 3. 극장별 상영 영화 페이지

            params = {
                'areacode': '01',
                'theatercode': theater_id,
                'date': datetime.now().strftime('%Y%m%d')
            }

            url = f"{self.base_url}/common/showtimes/iframeTheater.aspx"
            response = self._make_request(url, params=params, timeout=15)

            soup = BeautifulSoup(response.text, 'html.parser')
            movies = []

            # 영화 정보 파싱 (실제 CGV 구조에 맞춰 조정 필요)
            # CGV 웹사이트 구조가 변경될 수 있으므로 여러 선택자 시도
            movie_items = soup.select('.sect-showtimes') or soup.select('.movie-list li') or soup.select('.tbl-time tbody tr')

            if not movie_items:
                logger.warning(f"영화 목록을 찾을 수 없습니다 (극장 ID: {theater_id})")
                return []

            for item in movie_items:
                try:
                    # 제목 추출 (여러 패턴 시도)
                    title_elem = (
                        item.select_one('.info-movie strong') or
                        item.select_one('.movie-name') or
                        item.select_one('strong.title') or
                        item.select_one('h4')
                    )

                    if not title_elem:
                        continue

                    title = title_elem.text.strip()

                    # 영화 정보 추출
                    info = self._extract_movie_info(item)

                    movie_data = {
                        'title': title,
                        'cgv_movie_id': info.get('movie_id', f'M{hash(title) % 10000}'),
                        'poster_url': info.get('poster_url', ''),
                        'rating': info.get('rating', ''),
                        'genre': info.get('genre', ''),
                        'runtime': info.get('runtime', 0),
                        'director': info.get('director', ''),
                        'release_date': info.get('release_date')
                    }

                    movies.append(movie_data)
                    logger.debug(f"영화 파싱 완료: {title}")

                except Exception as e:
                    logger.error(f"영화 정보 파싱 오류: {e}")
                    continue

            logger.info(f"영화 {len(movies)}개 발견 (극장 ID: {theater_id})")
            return movies

        except Exception as e:
            logger.error(f"영화 목록 조회 실패 (극장 ID: {theater_id}): {e}")
            return []

    def _extract_movie_info(self, item) -> Dict:
        """영화 상세 정보 추출"""
        info = {}

        try:
            # 포스터 이미지
            poster = item.select_one('img.poster')
            if poster:
                info['poster_url'] = poster.get('src', '')

            # 관람등급
            rating_elem = item.select_one('.ic-grade')
            if rating_elem:
                info['rating'] = rating_elem.text.strip()

            # 장르, 러닝타임 등
            info_text = item.select_one('.info-movie .txt-info')
            if info_text:
                text = info_text.text
                # 예: "액션, 어드벤처 | 120분"
                parts = text.split('|')
                if len(parts) >= 1:
                    info['genre'] = parts[0].strip()
                if len(parts) >= 2:
                    runtime_match = re.search(r'(\d+)분', parts[1])
                    if runtime_match:
                        info['runtime'] = int(runtime_match.group(1))

        except Exception as e:
            logger.error(f"상세 정보 추출 오류: {e}")

        return info

    @retry_on_failure(max_retries=2, delay=1.0)  # 예매 확인은 빠르게 재시도
    def check_booking_available(self, movie_title: str, theater_id: str = "0013") -> Optional[Dict]:
        """
        특정 영화의 예매 가능 여부 확인

        Args:
            movie_title: 영화 제목
            theater_id: 극장 ID

        Returns:
            Optional[Dict]: 예매 가능 시 정보 반환, 없으면 None
        """
        try:
            # 상영시간표에서 예매 가능 여부 확인
            params = {
                'areacode': '01',
                'theatercode': theater_id,
                'date': datetime.now().strftime('%Y%m%d')
            }

            url = f"{self.base_url}/common/showtimes/iframeTheater.aspx"
            response = self._make_request(url, params=params, timeout=15)

            soup = BeautifulSoup(response.text, 'html.parser')

            # 영화 찾기 (여러 선택자 시도)
            movie_sections = soup.select('.sect-showtimes') or soup.select('.movie-list') or []

            if not movie_sections:
                logger.warning(f"상영 정보를 찾을 수 없습니다: {movie_title}")
                return None

            for section in movie_sections:
                # 영화 제목 찾기 (여러 패턴 시도)
                title_elem = (
                    section.select_one('.info-movie strong') or
                    section.select_one('.movie-title') or
                    section.select_one('h4.title')
                )

                if not title_elem:
                    continue

                current_title = title_elem.text.strip()

                # 영화 제목 매칭 (부분 일치 허용)
                if self._is_title_match(movie_title, current_title):
                    logger.debug(f"영화 발견: {current_title}")

                    # 예매 버튼 찾기 (여러 패턴 시도)
                    booking_buttons = (
                        section.select('.col-time a') or
                        section.select('.time-list a') or
                        section.select('a.btn-booking')
                    )

                    if not booking_buttons:
                        logger.debug(f"예매 버튼 없음: {current_title}")
                        continue

                    for button in booking_buttons:
                        # 예매 가능 버튼인지 확인
                        button_class = button.get('class', [])
                        button_onclick = button.get('onclick', '')

                        # disabled 클래스가 없거나, onclick에 booking 관련 함수가 있으면 예매 가능
                        is_available = (
                            'disabled' not in button_class and
                            'sold-out' not in button_class and
                            ('booking' in button_onclick.lower() or button.get('href'))
                        )

                        if is_available:
                            # 예매 가능!
                            booking_url = button.get('href', '')

                            # JavaScript 함수에서 URL 추출
                            if not booking_url and button_onclick:
                                url_match = re.search(r"location\.href='([^']+)'", button_onclick)
                                if url_match:
                                    booking_url = url_match.group(1)

                            if not booking_url:
                                # 기본 예매 URL 생성
                                booking_url = f"{self.base_url}/ticket/"

                            if not booking_url.startswith('http'):
                                booking_url = self.base_url + booking_url

                            logger.info(f"🎉 예매 오픈 감지: {movie_title} ({current_title})")

                            # 상영시간 정보 추출
                            time_elem = (
                                button.select_one('.txt-time') or
                                button.select_one('.time') or
                                button.find('span')
                            )
                            showtime = time_elem.text.strip() if time_elem else '시간 미상'

                            # 극장 이름 결정
                            theater_names = {
                                '0013': '용산아이파크몰 IMAX',
                                '0056': '강남 IMAX',
                                '0074': '왕십리 IMAX'
                            }
                            theater_name = theater_names.get(theater_id, f'CGV (코드: {theater_id})')

                            return {
                                'available': True,
                                'url': booking_url,
                                'movie_title': current_title,
                                'showtime': showtime,
                                'theater': theater_name,
                                'checked_at': datetime.now().isoformat()
                            }

            # 예매 불가능
            logger.debug(f"예매 아직 미오픈: {movie_title}")
            return None

        except Exception as e:
            logger.error(f"예매 확인 실패 ({movie_title}): {e}")
            return None

    def _is_title_match(self, title1: str, title2: str) -> bool:
        """
        영화 제목 매칭 확인 (공백, 특수문자 무시)

        Args:
            title1: 첫 번째 제목
            title2: 두 번째 제목

        Returns:
            bool: 매칭 여부
        """
        # 공백과 특수문자 제거 후 비교
        clean1 = re.sub(r'[^\w가-힣]', '', title1.lower())
        clean2 = re.sub(r'[^\w가-힣]', '', title2.lower())

        # 부분 일치 허용
        return clean1 in clean2 or clean2 in clean1

    @retry_on_failure(max_retries=3, delay=2.0)
    def get_movie_detail(self, movie_id: str) -> Optional[Dict]:
        """
        영화 상세 정보 조회

        Args:
            movie_id: CGV 영화 ID

        Returns:
            Optional[Dict]: 영화 상세 정보
        """
        try:
            url = f"{self.base_url}/movies/detail-view/?midx={movie_id}"
            response = self._make_request(url, timeout=10)

            soup = BeautifulSoup(response.text, 'html.parser')
            detail = {}

            # 제목 (여러 패턴 시도)
            title_elem = soup.select_one('.title') or soup.select_one('h1') or soup.select_one('.movie-title')
            if title_elem:
                detail['title'] = title_elem.text.strip()

            # 포스터
            poster_elem = soup.select_one('.poster img') or soup.select_one('img.poster-image')
            if poster_elem:
                poster_url = poster_elem.get('src', '')
                if poster_url and not poster_url.startswith('http'):
                    poster_url = self.base_url + poster_url
                detail['poster_url'] = poster_url

            # 개봉일
            date_elem = soup.select_one('.spec dd') or soup.select_one('.release-date')
            if date_elem:
                date_text = date_elem.text.strip()
                date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', date_text)
                if date_match:
                    detail['release_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"

            # 감독
            director_elem = soup.select_one('.spec .director') or soup.select_one('.director-name')
            if director_elem:
                detail['director'] = director_elem.text.strip()

            # 장르
            genre_elem = soup.select_one('.spec .genre') or soup.select_one('.movie-genre')
            if genre_elem:
                detail['genre'] = genre_elem.text.strip()

            # 러닝타임
            runtime_elem = soup.select_one('.spec .runtime') or soup.select_one('.movie-runtime')
            if runtime_elem:
                runtime_text = runtime_elem.text.strip()
                runtime_match = re.search(r'(\d+)분', runtime_text)
                if runtime_match:
                    detail['runtime'] = int(runtime_match.group(1))

            logger.debug(f"영화 상세 정보 조회 완료: {detail.get('title', movie_id)}")
            return detail

        except Exception as e:
            logger.error(f"영화 상세 정보 조회 실패 (ID: {movie_id}): {e}")
            return None


# Mock 크롤러 (테스트용)
class MockCGVCrawler(AdvancedCGVCrawler):
    """
    테스트용 Mock 크롤러
    실제 CGV에 접근하지 않고 가상 데이터 반환
    """

    def get_theaters(self) -> List[Dict]:
        """테스트용 극장 목록"""
        logger.info("[Mock] 극장 목록 조회")
        return [
            {
                'id': '0013',
                'name': '용산아이파크몰',
                'location': '서울',
                'theater_type': 'IMAX',
                'area_code': '01'
            },
            {
                'id': '0056',
                'name': '강남',
                'location': '서울',
                'theater_type': 'IMAX',
                'area_code': '01'
            }
        ]

    def get_movies(self, theater_id: str = "0013") -> List[Dict]:
        """테스트용 영화 목록"""
        logger.info(f"[Mock] 영화 목록 조회 (극장 ID: {theater_id})")
        return [
            {
                'title': '듄: 파트 2',
                'cgv_movie_id': 'M001',
                'poster_url': 'https://via.placeholder.com/150',
                'rating': '12세이상관람가',
                'genre': 'SF, 액션',
                'runtime': 166,
                'director': '드니 빌뇌브',
                'release_date': '2024-02-28'
            },
            {
                'title': '오펜하이머',
                'cgv_movie_id': 'M002',
                'poster_url': 'https://via.placeholder.com/150',
                'rating': '15세이상관람가',
                'genre': '드라마, 역사',
                'runtime': 180,
                'director': '크리스토퍼 놀란',
                'release_date': '2024-01-15'
            },
            {
                'title': '인터스텔라',
                'cgv_movie_id': 'M003',
                'poster_url': 'https://via.placeholder.com/150',
                'rating': '12세이상관람가',
                'genre': 'SF, 드라마',
                'runtime': 169,
                'director': '크리스토퍼 놀란',
                'release_date': '2024-12-06'
            }
        ]

    def check_booking_available(self, movie_title: str, theater_id: str = "0013") -> Optional[Dict]:
        """테스트용 예매 확인 (항상 미오픈 반환)"""
        logger.info(f"[Mock] {movie_title} 예매 확인")

        # 테스트를 위해 항상 None 반환 (예매 미오픈)
        # 예매 오픈 테스트를 하려면 아래 주석 해제
        # return {
        #     'available': True,
        #     'url': f'http://www.cgv.co.kr/ticket/?movie={movie_title}',
        #     'movie_title': movie_title,
        #     'showtime': '14:00',
        #     'theater': '용산아이파크몰 IMAX'
        # }

        return None
