import re
from urllib.parse import urljoin

import requests
from rapidfuzz import fuzz
from bs4 import BeautifulSoup

from database.db_config import save_product


def parse_foxstore(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('[Foxstore] Название товара не может быть пустым')
    base = 'https://foxstore.by'
    response = requests.post(base + '/', data={'ajax_call': 'y', 'INPUT_ID': 'title-search-input_fixed', 'q': query, 'l': 2}, headers={'User-Agent': 'Mozilla/5.0', 'X-Requested-With': 'XMLHttpRequest'}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    for link in soup.select('a.bx_item_block[href]'):
        name = link.select_one('.bx_item_element > span')
        price = link.select_one('.title-search-price .price')
        if not name or not price:
            continue
        value = re.sub(r'[^\d.,]', '', price.get_text('', strip=True)).replace(',', '.').rstrip('.')
        if not value:
            continue
        url = urljoin(base, link['href'])
        image = link.select_one('img')
        image_url = (image.get('data-src') or image.get('src')) if image else None
        search_re = re.sub(r'[^a-zA-Z0-9/ ]', '', query.lower())
        title_re = re.sub(r'[^a-zA-Z0-9/ ]', '', (name.get_text(' ', strip=True)).lower())
        fuzziness = fuzz.token_set_ratio(search_re, title_re.strip())

        if search_re not in title_re and fuzziness < 90:
            continue
        if re.fullmatch(r'[+-]?0+(?:[.,]0+)?', str(value).strip().replace(' ', '')):
            continue

        products.append(save_product(shop_product_id=url.rstrip('/').split('/')[-1], title=name.get_text(' ', strip=True), price=value, product_url=url, img_url=urljoin(base, image_url) if image_url else None, shop_name='foxstore', currency='BYN'))
    return products
