# from core import get_soup
import requests
from bs4 import BeautifulSoup
from time import sleep
import json, re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}

def parseCookies(cookies_file):
    cookies = {}
    with open(cookies_file, 'r') as c:
        for line in c:
            if not re.match(r'^\#', line):
                lineFields = line.strip().split('\t')
                cookies[lineFields[5]] = lineFields[6]
    return cookies

def get_soup(url: str):
    cookies = parseCookies("f/backend/parsers/cookies/cookies-21vek-by.txt")
    response = requests.get(url, headers=HEADERS, cookies=cookies)
    return BeautifulSoup(response.text, "html.parser")

name = input("name: ").replace(' ', '+')
url = "https://21vek.by/search/?sa=&term=" + name

soup = get_soup(url)
script = soup.find("script", {"id": "__NEXT_DATA__"})
if script:
    data = json.loads(script.string)
else:
    print("json not found")

inner = json.loads(data["props"]["pageProps"]["initialState"])

print(inner["searchResult"]["products"]["all"][0]["name"],
    inner["searchResult"]["products"]["all"][0]["price"],
    inner["searchResult"]["products"]["all"][0]["salePrice"]
)