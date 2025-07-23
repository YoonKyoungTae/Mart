import os
import requests
from bs4 import BeautifulSoup

# 저장 폴더 생성
os.makedirs("leaflets", exist_ok=True)

# 전단지 페이지 URL
url = "https://emartapp.emart.com/leaflet/leafletView_EL.do?&image_pop=true"

# 페이지 요청 및 파싱
res = requests.get(url)
res.encoding = 'utf-8'
soup = BeautifulSoup(res.text, 'html.parser')

# 이미지 태그 선택 (전단지 이미지 영역)
img_tags = soup.select("div.pop_cont img")

if not img_tags:
    print("No images found on page.")

# 이미지 다운로드 및 저장
for i, img in enumerate(img_tags):
    img_url = img.get("src")
    if img_url.startswith("/"):
        img_url = "https://emartapp.emart.com" + img_url
    try:
        img_data = requests.get(img_url).content
        filename = f"leaflets/leaflet_{i+1}.jpg"
        with open(filename, "wb") as f:
            f.write(img_data)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Failed to save image {img_url}: {e}")
