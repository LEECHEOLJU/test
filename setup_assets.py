"""
에셋 파일 자동 생성 스크립트
기본 이미지 및 아이콘 다운로드
"""
import os
import urllib.request
from pathlib import Path

def download_file(url, filepath):
    """파일 다운로드"""
    try:
        print(f"📥 다운로드 중: {filepath}")
        urllib.request.urlretrieve(url, filepath)
        print(f"   ✅ 완료")
        return True
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        return False

def create_placeholder_svg(filepath, width, height, text):
    """SVG placeholder 생성"""
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#667eea"/>
  <text x="50%" y="50%" font-family="Arial" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">
    {text}
  </text>
</svg>'''

    with open(filepath, 'w') as f:
        f.write(svg_content)
    print(f"✅ 생성됨: {filepath}")

def setup_assets():
    """모든 에셋 설정"""

    print("=" * 60)
    print("🎨 에셋 파일 설정")
    print("=" * 60)
    print()

    # 디렉토리 생성
    static_dir = Path("static")
    icons_dir = static_dir / "icons"

    static_dir.mkdir(exist_ok=True)
    icons_dir.mkdir(exist_ok=True)

    print("📁 디렉토리 생성 완료")
    print()

    # 1. default-poster.png (SVG placeholder)
    print("1️⃣ 기본 포스터 이미지")
    poster_path = static_dir / "default-poster.svg"
    create_placeholder_svg(
        poster_path,
        width=300,
        height=450,
        text="CGV IMAX"
    )
    print()

    # 2. PWA 아이콘들 (SVG placeholder)
    print("2️⃣ PWA 아이콘")
    icon_sizes = [192, 512]

    for size in icon_sizes:
        icon_path = icons_dir / f"icon-{size}.svg"
        create_placeholder_svg(
            icon_path,
            width=size,
            height=size,
            text="🎬"
        )

    print()

    # 3. favicon (SVG)
    print("3️⃣ Favicon")
    favicon_path = static_dir / "favicon.svg"
    create_placeholder_svg(
        favicon_path,
        width=32,
        height=32,
        text="🎬"
    )
    print()

    # 4. manifest.json 확인
    print("4️⃣ manifest.json 확인")
    manifest_path = static_dir / "manifest.json"
    if manifest_path.exists():
        print("   ✅ 이미 존재함")
    else:
        print("   ⚠️  manifest.json이 없습니다")
        print("   💡 다음 명령으로 생성:")
        print("      (manifest.json은 이미 생성되어 있어야 함)")

    print()
    print("=" * 60)
    print("✅ 에셋 설정 완료!")
    print("=" * 60)
    print()
    print("📋 생성된 파일:")
    print(f"   - {poster_path}")
    print(f"   - {favicon_path}")
    for size in icon_sizes:
        print(f"   - {icons_dir}/icon-{size}.svg")
    print()
    print("💡 참고:")
    print("   - SVG 파일은 모든 브라우저에서 작동합니다")
    print("   - 원하는 이미지로 교체 가능합니다")
    print("   - PNG로 변환하려면 온라인 도구 사용:")
    print("     https://cloudconvert.com/svg-to-png")
    print()

if __name__ == '__main__':
    try:
        setup_assets()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        exit(1)
