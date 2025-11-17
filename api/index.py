"""
Vercel Serverless Function용 Flask 앱 엔트리포인트
이 파일이 Vercel에서 모든 요청을 처리합니다
"""
import sys
import os

# 프로젝트 루트를 Python path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Flask 앱 import
from app_vercel import app

# Vercel은 이 app 객체를 자동으로 감지하고 실행합니다
# 추가 handler 함수는 필요 없습니다
