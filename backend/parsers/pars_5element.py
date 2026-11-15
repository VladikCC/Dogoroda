from urllib.parse import urljoin

import requests

from database.db_config import save_product


def parse_5element(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('Название товара не может быть пустым')
    response = requests.get('https://sort.diginetica.net/search', params={'apiKey': '08IE0509XQ', 'st': query, 'strategy': 'advanced_xname', 'fullData': 'true', 'size': 20}, timeout=30)
    response.raise_for_status()
    data = response.json()
    products = []
    for item in data['products']:
        if not item.get('id') or not item.get('name') or not item.get('link_url') or item.get('price') is None:
            continue
        products.append(save_product(shop_product_id=str(item['id']), title=item['name'], price=str(item['price']), product_url=urljoin('https://5element.by', item['link_url']), img_url=item.get('image_url'), shop_name='5element', currency='BYN'))
    return products
