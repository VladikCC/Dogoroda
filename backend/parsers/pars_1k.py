import json
from pathlib import Path
import hashlib

import requests
from bs4 import BeautifulSoup

from backend.database.db_config import init_db, save_product

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


def parse_1k(search_name: str):
    saved_products = []
    
    search_name = search_name.strip()

    if not search_name:
        raise ValueError(
            "Название товара не может быть пустым"
        )

    url = (
        "https://1k.by/products/search?s_keywords="
        f"{requests.utils.quote(search_name)}"
    )

    print(f"Searching: {search_name}")
    print(f"URL: {url}")

    soup = get_soup(url)

    products = soup.find_all(
        "div",
        {"class": "prod prod--toggle"},
    )

    print(products,  len(products))

    if not products:
        raise RuntimeError(
            "Not found"
        )

    for product in products:
        title = product.find_all("a", {"class": "prod__link"})[0].text
        if not title:
            print(
                "Пропускаем товар: "
                "нет названия"
            )
            continue

        if search_name.casefold() not in title.casefold():
            print(f"Пропускаем {title}: нет '{search_name}' в названии")
            continue

        price = product.find("span", {"class": "money__val"}).text

        if price is None:
            print(
                f"Пропускаем {title}: "
                "нет цены"
            )
            continue

        price = price.split(" – ")[0]

        product_url = product.find("a")["href"]
        img_url = product.find("img")["src"]
        shop_id = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()

        product = save_product(
            shop_product_id=shop_id,
            title=title,
            price=price,
            product_url=product_url,
            img_url=img_url,
            shop_name="1k",
            currency="BYN",
        )

        saved_products.append(product)

        print()
        print("SAVED:")
        print(
            f"Название: "
            f"{product.title}"
        )
        print(
            f"Цена: "
            f"{product.price} "
            f"{product.currency}"
        )
        print(
            f"Товар: "
            f"{product.product_url}"
        )
        print(
            f"Фото: "
            f"{product.img_url}"
        )

    return saved_products


if __name__ == "__main__":

    init_db()

    name = input("name: ")

    products = parse_1k(name)
    print(
        f"\nSaved to database: "
        f"{len(products)} products"
    )
