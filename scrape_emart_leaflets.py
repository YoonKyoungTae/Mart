import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import shutil
import re

def organize_existing_files():
    """기존 파일들을 날짜별 폴더로 정리하는 함수"""
    base_folder = "leaflets"
    
    if not os.path.exists(base_folder):
        return
    
    print("📁 기존 파일들을 날짜별 폴더로 정리 중...")
    
    # leaflets 폴더 내의 모든 파일 검색
    for filename in os.listdir(base_folder):
        if filename.endswith('.jpg') and filename.startswith('emart_leaflet_'):
            # 파일명에서 날짜 추출 (예: emart_leaflet_20250724_01.jpg)
            date_match = re.search(r'emart_leaflet_(\d{8})_\d{2}\.jpg', filename)
            if date_match:
                date_str = date_match.group(1)  # 20250724
                # 날짜 형식 변환 (20250724 -> 2025-07-24)
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                
                # 날짜별 폴더 생성
                date_folder = os.path.join(base_folder, formatted_date)
                os.makedirs(date_folder, exist_ok=True)
                
                # 파일 이동
                old_path = os.path.join(base_folder, filename)
                # 새 파일명에서 날짜 부분 제거 (emart_leaflet_20250724_01.jpg -> emart_leaflet_01.jpg)
                new_filename = re.sub(r'emart_leaflet_\d{8}_', 'emart_leaflet_', filename)
                new_path = os.path.join(date_folder, new_filename)
                
                if os.path.exists(old_path) and not os.path.exists(new_path):
                    shutil.move(old_path, new_path)
                    print(f"✅ {filename} -> {formatted_date}/{new_filename}")

def scrape_emart_leaflets():
    # 기본 저장 폴더 생성
    base_folder = "leaflets"
    os.makedirs(base_folder, exist_ok=True)
    
    # 오늘 날짜로 하위 폴더 생성
    today = datetime.now().strftime("%Y-%m-%d")
    today_folder = os.path.join(base_folder, today)
    os.makedirs(today_folder, exist_ok=True)
    
    url = "https://emartapp.emart.com/leaflet/leafletView_EL.do?&image_pop=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        print("🔍 이마트 전단지 페이지에 접속 중...")
        res = requests.get(url, headers=headers, timeout=30)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # HTML 저장 (디버깅용)
        with open("emart.html", "w", encoding="utf-8") as f:
            f.write(res.text)
        print("📄 HTML 페이지 저장 완료 (emart.html)")
        
        # data-src 속성을 가진 이미지 태그 찾기
        img_tags = soup.select("div.img_detail img[data-src]")
        
        if not img_tags:
            print("❌ 전단지 이미지를 찾을 수 없습니다.")
            return
        
        print(f"✅ {len(img_tags)}개의 전단지 이미지를 발견했습니다.")
        
        success_count = 0
        for i, img in enumerate(img_tags, 1):
            img_url = img.get("data-src")
            alt_text = img.get("alt", f"전단지 {i}면")
            
            if not img_url:
                print(f"⚠️ {i}번째 이미지의 URL을 찾을 수 없습니다.")
                continue
            
            # 상대 경로를 절대 경로로 변환
            if img_url.startswith("/"):
                img_url = "https://stimg.emart.com" + img_url
            
            try:
                print(f"📥 {i}번째 이미지 다운로드 중... ({alt_text})")
                img_response = requests.get(img_url, headers=headers, timeout=30)
                img_response.raise_for_status()
                
                # 파일명 생성 (날짜별 폴더 구조)
                filename = os.path.join(today_folder, f"emart_leaflet_{i:02d}.jpg")
                
                with open(filename, "wb") as f:
                    f.write(img_response.content)
                
                file_size = len(img_response.content) / 1024  # KB
                print(f"✅ {filename} 저장 완료 ({file_size:.1f}KB)")
                success_count += 1
                
                # 서버 부하 방지를 위한 딜레이
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"❌ {i}번째 이미지 다운로드 실패: {e}")
            except Exception as e:
                print(f"❌ {i}번째 이미지 저장 실패: {e}")
        
        print(f"\n🎉 크롤링 완료! 총 {success_count}개의 이미지가 성공적으로 저장되었습니다.")
        print(f"📁 저장 위치: ./{today_folder}/")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 웹페이지 접속 실패: {e}")
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")

if __name__ == "__main__":
    # 기존 파일들을 날짜별 폴더로 정리
    organize_existing_files()
    
    # 새로운 전단지 크롤링 실행
    scrape_emart_leaflets()
