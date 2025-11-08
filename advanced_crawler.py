"""
향상된 CGV 크롤러
실제 CGV API와 웹사이트를 크롤링하여 영화 정보 및 예매 상태 확인
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedCGVCrawler:
    """향상된 CGV 크롤러"""

    def __init__(self):
        self.base_url = "http://www.cgv.co.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'http://www.cgv.co.kr/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_theaters(self) -> List[Dict]:
        """
        CGV 극장 목록 조회

        Returns:
            List[Dict]: 극장 정보 리스트
        """
        try:
            # CGV 극장 목록 API 또는 페이지
            url = f"{self.base_url}/theaters/"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            theaters = []

            # 용산 IMAX 극장 정보 (하드코딩, 실제로는 파싱 필요)
            theaters.append({
                'id': '0013',
                'name': '용산아이파크몰',
                'location': '서울',
                'theater_type': 'IMAX',
                'area_code': '01'
            })

            # 추가 극장들...
            logger.info(f"극장 {len(theaters)}개 발견")
            return theaters

        except Exception as e:
            logger.error(f"극장 목록 조회 실패: {e}")
            return []

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

            url = f"{self.base_url}/common/showtimes/iframeTheater.aspx?areacode=01&theatercode={theater_id}&date={datetime.now().strftime('%Y%m%d')}"

            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            movies = []

            # 영화 정보 파싱 (실제 CGV 구조에 맞춰 조정 필요)
            movie_items = soup.select('.sect-showtimes')

            for item in movie_items:
                try:
                    title_elem = item.select_one('.info-movie strong')
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()

                    # 영화 정보 추출
                    info = self._extract_movie_info(item)

                    movie_data = {
                        'title': title,
                        'cgv_movie_id': info.get('movie_id', ''),
                        'poster_url': info.get('poster_url', ''),
                        'rating': info.get('rating', ''),
                        'genre': info.get('genre', ''),
                        'runtime': info.get('runtime', 0),
                        'director': info.get('director', ''),
                        'release_date': info.get('release_date')
                    }

                    movies.append(movie_data)

                except Exception as e:
                    logger.error(f"영화 정보 파싱 오류: {e}")
                    continue

            logger.info(f"영화 {len(movies)}개 발견")
            return movies

        except Exception as e:
            logger.error(f"영화 목록 조회 실패: {e}")
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

    def check_booking_available(self, movie_title: str, theater_id: str = "0013") -> Optional[Dict]:
        """
        특정 영화의 예매 가능 여부 확인

        Args:
            movie_title: 영화 제목
            theater_id: 극장 ID

        Returns:
            Optional[Dict]: 예매 가능 시 정보 반환
        """
        try:
            # 상영시간표에서 예매 가능 여부 확인
            url = f"{self.base_url}/common/showtimes/iframeTheater.aspx"

            params = {
                'areacode': '01',
                'theatercode': theater_id,
                'date': datetime.now().strftime('%Y%m%d')
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 영화 찾기
            movie_sections = soup.select('.sect-showtimes')

            for section in movie_sections:
                title_elem = section.select_one('.info-movie strong')
                if not title_elem:
                    continue

                current_title = title_elem.text.strip()

                if movie_title in current_title or current_title in movie_title:
                    # 예매 버튼 찾기
                    booking_buttons = section.select('.col-time a')

                    for button in booking_buttons:
                        # 예매 가능 버튼인지 확인
                        if 'disabled' not in button.get('class', []):
                            # 예매 가능!
                            booking_url = button.get('href', '')

                            if not booking_url.startswith('http'):
                                booking_url = self.base_url + booking_url

                            logger.info(f"예매 오픈 감지: {movie_title}")

                            # 상영시간 정보 추출
                            time_elem = button.select_one('.txt-time')
                            showtime = time_elem.text.strip() if time_elem else ''

                            return {
                                'available': True,
                                'url': booking_url,
                                'movie_title': current_title,
                                'showtime': showtime,
                                'theater': '용산아이파크몰 IMAX'
                            }

            # 예매 불가능
            logger.info(f"예매 아직 미오픈: {movie_title}")
            return None

        except Exception as e:
            logger.error(f"예매 확인 실패: {e}")
            return None

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

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            detail = {}

            # 제목
            title_elem = soup.select_one('.title')
            if title_elem:
                detail['title'] = title_elem.text.strip()

            # 포스터
            poster_elem = soup.select_one('.poster img')
            if poster_elem:
                detail['poster_url'] = poster_elem.get('src', '')

            # 개봉일
            date_elem = soup.select_one('.spec dd')
            if date_elem:
                date_text = date_elem.text.strip()
                date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', date_text)
                if date_match:
                    detail['release_date'] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"

            # 감독
            director_elem = soup.select_one('.spec .director')
            if director_elem:
                detail['director'] = director_elem.text.strip()

            return detail

        except Exception as e:
            logger.error(f"영화 상세 정보 조회 실패: {e}")
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
