import requests
from bs4 import BeautifulSoup

PRODUCT_URL = "https://www.amazon.com/dp/B07FZ8S74R"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

TARGET_PRICE = 900

response = requests.get(PRODUCT_URL, headers=HEADERS)
soup = BeautifulSoup(response.text, "html.parser")

title = soup.find(id="productTitle").get_text(strip=True)
price_tag = soup.find("span", class_="a-offscreen")
price_text = price_tag.get_text(strip=True)

price = float(price_text.replace("$", "").replace(",", ""))

print("Product:", title)
print("Current price:", price)

if price < TARGET_PRICE:
    print("less than goal")
else:
    print("greater than goal")
