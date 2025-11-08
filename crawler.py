"""
CGV 웹사이트 크롤러
용산 IMAX 상영관의 영화 목록 및 예매 정보 수집
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time


class CGVCrawler:
    def __init__(self):
        self.base_url = "http://www.cgv.co.kr"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_imax_movies(self, theater_name: str = "용산아이파크몰") -> List[Dict]:
        """
        CGV 용산 IMAX 상영 예정 영화 목록 조회

        Args:
            theater_name: 극장명

        Returns:
            List[Dict]: 영화 목록 [{"title": "영화명", "code": "영화코드"}, ...]
        """
        try:
            # CGV 영화 목록 페이지
            # 실제 URL은 CGV 웹사이트 구조에 따라 조정 필요
            url = f"{self.base_url}/movies/"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 영화 목록 파싱 (실제 CGV 웹사이트 구조에 맞춰 조정 필요)
            movies = []

            # 예시: 영화 목록 파싱 로직
            # 실제 구현 시 CGV 웹사이트의 실제 HTML 구조를 분석하여 수정 필요
            movie_list = soup.select('.movie-list .movie-item')

            for movie in movie_list:
                try:
                    title_elem = movie.select_one('.title')
                    if title_elem:
                        title = title_elem.text.strip()
                        # 영화 코드나 ID 추출 (링크에서)
                        link = movie.select_one('a')
                        code = link.get('href', '').split('=')[-1] if link else ''

                        movies.append({
                            'title': title,
                            'code': code
                        })
                except Exception as e:
                    print(f"영화 파싱 중 오류: {e}")
                    continue

            print(f"총 {len(movies)}개 영화 발견")
            return movies

        except requests.RequestException as e:
            print(f"영화 목록 조회 실패: {e}")
            return []
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return []

    def check_booking_available(self, movie_title: str, theater_name: str = "용산아이파크몰") -> Optional[Dict]:
        """
        특정 영화의 예매 가능 여부 확인

        Args:
            movie_title: 영화 제목
            theater_name: 극장명

        Returns:
            Optional[Dict]: 예매 가능 시 {"available": True, "url": "예매URL"}, 불가능 시 None
        """
        try:
            # CGV 극장별 상영 시간표 페이지
            # 실제 URL은 CGV API나 웹사이트 구조에 따라 조정 필요

            # 방법 1: 영화 상세 페이지에서 확인
            # 방법 2: 극장별 시간표 페이지에서 확인
            # 방법 3: CGV API 사용 (존재한다면)

            # 예시: 영화 상세/예매 페이지 확인
            # 실제로는 CGV 웹사이트 구조를 분석하여 적절한 URL과 파싱 로직 필요

            search_url = f"{self.base_url}/movies/"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 영화 찾기
            # 실제 구현 시 CGV 웹사이트의 구조에 맞춰 수정
            movie_items = soup.select('.movie-item')

            for item in movie_items:
                title_elem = item.select_one('.title')
                if title_elem and movie_title in title_elem.text:
                    # 예매 버튼이나 링크 찾기
                    booking_btn = item.select_one('.btn-booking, .reserve')

                    if booking_btn:
                        # 예매 가능
                        booking_url = booking_btn.get('href', '')
                        if not booking_url.startswith('http'):
                            booking_url = self.base_url + booking_url

                        print(f"예매 오픈 감지: {movie_title}")
                        return {
                            'available': True,
                            'url': booking_url,
                            'movie_title': movie_title,
                            'theater': theater_name
                        }

            # 예매 불가능
            return None

        except requests.RequestException as e:
            print(f"예매 확인 실패: {e}")
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return None

    def get_movie_detail(self, movie_code: str) -> Optional[Dict]:
        """
        영화 상세 정보 조회 (나중에 구현)

        Args:
            movie_code: 영화 코드

        Returns:
            Optional[Dict]: 영화 상세 정보
        """
        # TODO: 영화 상세 정보 크롤링 구현
        pass


# 테스트용 Mock 크롤러 (개발 중)
class MockCGVCrawler(CGVCrawler):
    """
    테스트용 Mock 크롤러
    실제 CGV 웹사이트에 접근하지 않고 가상 데이터 반환
    """

    def get_imax_movies(self, theater_name: str = "용산아이파크몰") -> List[Dict]:
        """테스트용 영화 목록 반환"""
        print("[Mock] 영화 목록 조회")
        return [
            {"title": "듄: 파트 2", "code": "001"},
            {"title": "오펜하이머", "code": "002"},
            {"title": "인터스텔라", "code": "003"},
            {"title": "아바타: 물의 길", "code": "004"},
        ]

    def check_booking_available(self, movie_title: str, theater_name: str = "용산아이파크몰") -> Optional[Dict]:
        """
        테스트용 예매 확인
        NOTE: 실제 테스트를 위해 항상 None 반환 (예매 불가)
        예매 오픈 테스트를 하려면 주석을 수정하세요
        """
        print(f"[Mock] {movie_title} 예매 확인")

        # 테스트: 예매 불가능 상태 시뮬레이션
        return None

        # 예매 가능 상태를 테스트하려면 아래 주석 해제
        # return {
        #     'available': True,
        #     'url': f'http://www.cgv.co.kr/ticket/?movie={movie_title}',
        #     'movie_title': movie_title,
        #     'theater': theater_name
        # }
