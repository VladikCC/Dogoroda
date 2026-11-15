from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from database.db_config import save_product


def parse_shopby(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('Название товара не может быть пустым')
    base = 'https://shop.by'
    response = requests.get(base + '/find/', params={'findtext': query}, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    products = []
    for card in soup.select('.ModelList__DescModelBlock'):
        link = card.select_one('a.ShopItemList__ViewProduct[href]')
        price = card.select_one('.PriceBlock__PriceFirst span')
        if not link or not price:
            continue
        href = urljoin(base, link['href'])
        url = parse_qs(urlparse(href).query).get('url', [href])[0]
        image = card.find_parent(class_='ModelList__Item')
        image = image.select_one('img') if image else None
        image_url = (image.get('data-src') or image.get('src')) if image else None
        products.append(save_product(shop_product_id=link.get('data-id') or url, title=link.get_text(' ', strip=True), price=price.get_text(strip=True).replace(' ', '').replace(',', '.'), product_url=url, img_url=urljoin(base, image_url) if image_url else None, shop_name='shop.by', currency='BYN'))
    return products
