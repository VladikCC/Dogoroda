import re
from urllib.parse import quote, urljoin

import requests
from rapidfuzz import fuzz
from bs4 import BeautifulSoup

from database.db_config import save_product


def parse_silaby(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('[Sila.by] Название товара не может быть пустым')
    base = 'https://sila.by'
    response = requests.get(base + '/search/' + quote(query.replace(' ', '_'), safe=''), headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    for card in soup.select('.tov_prew_search'):
        link = card.select_one('a[href]:has(img)')
        price = card.select_one('.price')
        if not link or not price:
            continue
        image = link.select_one('img')
        value = re.sub(r'[^\d.,]', '', price.get_text('', strip=True)).replace(',', '.')
        if not value:
            continue
        url = urljoin(base, link['href'])
        search_re = re.sub(r'[^a-zA-Z0-9/ ]', '', query.lower())
        title_re = re.sub(r'[^a-zA-Z0-9/ ]', '', (image.get('alt') or link.get_text(' ', strip=True)).lower())
        fuzziness = fuzz.token_set_ratio(search_re, title_re.strip())

        if search_re not in title_re and fuzziness < 90:
            continue
        if re.fullmatch(r'[+-]?0+(?:[.,]0+)?', str(value).strip().replace(' ', '')):
            continue

        products.append(save_product(shop_product_id=card.get('data-idabc') or url, title=image.get('alt') or link.get_text(' ', strip=True), price=value, product_url=url, img_url=urljoin(base, image.get('src')) if image.get('src') else None, shop_name='sila.by', currency='BYN'))
    return products
