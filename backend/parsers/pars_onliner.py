import json
from pathlib import Path
import re
import hashlib

import requests
from bs4 import BeautifulSoup

from rapidfuzz import fuzz

from database.db_config import init_db, save_product

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
}


def get_soup(url: str):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser",
    )


def parse_onliner(search_name: str):
    saved_products = []
    
    search_name = search_name.strip()

    if not search_name:
        raise ValueError(
            "[Onliner] Название товара не может быть пустым"
        )

    url = (
        "https://catalog.onliner.by/search?q="
        f"{requests.utils.quote(search_name)}"
    )

    print("[Onliner]", f"Searching: {search_name}")
    print("[Onliner]", f"URL: {url}")

    soup = get_soup(url)

    products = soup.find_all(
        "div",
        {"class": "catalog-form__offers-item"},
    )

    if not products:
        raise RuntimeError(
            "Not found"
        )

    products = products[:6]

    for product in products:

        title = product.find_all("a", {"class": "catalog-form__link"})[1].text
        if not title:
            print(
            "[Onliner]",
                "Пропускаем товар: "
                "нет названия"
            )
            continue

        search_re = re.sub(r'[^a-zA-Z0-9/ ]', '', search_name.lower())
        title_re = re.sub(r'[^a-zA-Z0-9/ ]', '', title.lower())
        fuzziness = fuzz.token_set_ratio(search_re, title_re.strip())

        if search_re not in title_re and fuzziness < 90:      
            print("[Onliner]", f"Пропускаем {title}: нет '{search_name}' в названии, точность поиска {fuzziness}")
            continue

        price = product.find("a", {"class": "catalog-form__link"}).text

        if price is None:
            print(
            "[Onliner]",
                f"Пропускаем {title}: "
                "нет цены"
            )
            continue

        try:
            price = (
                price
                .replace("от ", "")
                .replace(" ", "")
                .replace(",", ".")
                .replace("ƃ", "")
            )

        except (
            ValueError,
            TypeError,
        ):
            print(
            "[Onliner]",
                f"Не удалось обработать цену: "
                f"{price}"
            )
            continue

        product_url = product.find("a")["href"]
        img_url = product.find("img")["src"]
        shop_id = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()

        if re.fullmatch(r'[+-]?0+(?:[.,]0+)?', str(price).strip().replace(' ', '')):
            continue

        product = save_product(
            shop_product_id=shop_id,
            title=title,
            price=price,
            product_url=product_url,
            img_url=img_url,
            shop_name="onliner",
            currency="BYN",
        )

        saved_products.append(product)

        print()
        print("[Onliner]", "SAVED:")
        print(
            "[Onliner]",
            f"Название: "
            f"{product.title}"
        )
        print(
            "[Onliner]",
            f"Цена: "
            f"{product.price} "
            f"{product.currency}"
        )
        print(
            "[Onliner]",
            f"Товар: "
            f"{product.product_url}"
        )
        print(
            "[Onliner]",
            f"Фото: "
            f"{product.img_url}"
        )

    return saved_products


if __name__ == "__main__":

    init_db()

    name = input("name: ")

    try:

        products = parse_onliner(name)

        print()
        print(
            "[Onliner]",
            f"Saved to database: "
            f"{len(products)} products"
        )

    except Exception as error:

        print(
            "[Onliner]",
            f"Parser error: {error}"
        )
