from urllib.parse import urljoin

import requests

from database.db_config import save_product


def parse_mts(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('Название товара не может быть пустым')
    api = 'https://api.shop.mts.by/api'
    response = requests.get(api + '/search', params={'query': query}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not payload.get('is_success'):
        raise RuntimeError('MTS search API failed')
    products = []
    for item in payload['data']['products']:
        price = (item.get('payment') or {}).get('price')
        if not item.get('id') or not item.get('name') or not item.get('link') or price is None:
            continue
        media = item.get('media_ids') or []
        products.append(save_product(shop_product_id=str(item['id']), title=item['name'], price=str(price), product_url=urljoin('https://shop.mts.by/', item['link']), img_url=api + '/media/' + str(media[0]) if media else None, shop_name='mts', currency='BYN'))
    return products
