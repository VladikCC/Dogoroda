import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep



url = "https://catalog.onliner.by/"
model = input("Введите название модели для поиска (например, Google Pixel 10 или CMF Buds Pro):\n→ ")

service = FirefoxService(GeckoDriverManager().install())
browser = webdriver.Firefox(service=service)
browser.get(url)
# .get() is considered as executed only when the page is fully loaded


# useragent to pretend im human, headers to send data in request
# requests part is kinda useless, probably gonna remove it
st_accept = "text/html"
st_useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
headers = {
    "Accept": st_accept,
    "User-Agent": st_useragent
}

request = requests.get(url, headers)
# site's source code
src = request.text


# opening search and pasting text
open_search = browser.find_element(By.CLASS_NAME, "fast-search__input")
open_search.click()
try:
    search = browser.find_element(By.CLASS_NAME, "search__input")
except NoSuchElementException:
    search = open_search

search.send_keys(model)
sleep(0.7)
# sleep is for results loading


# getting the price
soup = BeautifulSoup(browser.page_source, "lxml")
price_link = soup.find('a', {"class": "product__price-value"})
price = price_link.find_all(recursive = False)[0].text # TODO: remove "от " part from price

print(f"Цена на {model} на onliner.by: {price}")

# TODO: parsing from other sites (different classes in every site will take some time, actually...)