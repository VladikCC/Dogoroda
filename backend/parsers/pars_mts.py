import re
from urllib.parse import urljoin

import requests
from rapidfuzz import fuzz

from database.db_config import save_product


def parse_mts(search_name: str):
    query = search_name.strip()
    if not query:
        raise ValueError('[МТС] Название товара не может быть пустым')
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
        search_re = re.sub(r'[^a-zA-Z0-9/ ]', '', query.lower())
        title_re = re.sub(r'[^a-zA-Z0-9/ ]', '', (item['name']).lower())
        fuzziness = fuzz.token_set_ratio(search_re, title_re.strip())

        if search_re not in title_re and fuzziness < 90:
            continue
        if re.fullmatch(r'[+-]?0+(?:[.,]0+)?', str(price).strip().replace(' ', '')):
            continue

        products.append(save_product(shop_product_id=str(item['id']), title=item['name'], price=str(price), product_url=urljoin('https://shop.mts.by/', item['link']), img_url=api + '/media/' + str(media[0]) if media else None, shop_name='mts', currency='BYN'))
    return products
