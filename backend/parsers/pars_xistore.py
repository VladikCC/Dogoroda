import re
from urllib.parse import urljoin

import requests
from rapidfuzz import fuzz
from bs4 import BeautifulSoup

from database.db_config import save_product


def parse_xistore(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('[Xistore] Название товара не может быть пустым')
    base = 'https://xistore.by'
    response = requests.get(base + '/search/', params={'q': query}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    for card in soup.select('.search__page_item'):
        link = card.select_one('a.search__page_item-name[href]')
        price = card.select_one('.search__page_item-price .price')
        if not link or not price:
            continue
        image = card.select_one('.search__page_item-img img')
        image_url = image.get('data-src') or image.get('src') if image else None
        url = urljoin(base, link['href']).split('?')[0]
        search_re = re.sub(r'[^a-zA-Z0-9/ ]', '', query.lower())
        title_re = re.sub(r'[^a-zA-Z0-9/ ]', '', (link.get_text(' ', strip=True)).lower())
        fuzziness = fuzz.token_set_ratio(search_re, title_re.strip())

        if search_re not in title_re and fuzziness < 90:
            continue
        if re.fullmatch(r'[+-]?0+(?:[.,]0+)?', str(price.get_text('', strip=True)).strip().replace(' ', '')):
            continue

        products.append(save_product(shop_product_id=link.get('data-id_product') or url, title=link.get_text(' ', strip=True), price=price.get_text('', strip=True), product_url=url, img_url=urljoin(base, image_url) if image_url else None, shop_name='xistore', currency='BYN'))
    return products
