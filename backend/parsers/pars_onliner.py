import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

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
            "Название товара не может быть пустым"
        )

    url = (
        "https://catalog.onliner.by/search?q="
        f"{requests.utils.quote(search_name)}"
    )

    print(f"Searching: {search_name}")
    print(f"URL: {url}")

    soup = get_soup(url)

    products = soup.find_all(
        "div",
        {"class": "catalog-form__offers-item"},
    )

    if not products:
        raise RuntimeError(
            "Not found"
        )

    for product in products:

        title = product.find_all("a", {"class": "catalog-form__link"})[1].text
        if not title:
            print(
                "Пропускаем товар: "
                "нет названия"
            )
            continue

        if search_name.casefold() not in title.casefold():
            print(f"Пропускаем {title}: нет '{search_name}' в названии")
            continue

        price = product.find("a", {"class": "catalog-form__link"}).text

        if price is None:
            print(
                f"Пропускаем {title}: "
                "нет цены"
            )
            continue

        if isinstance(price, str):
            price = (
                price
                .replace("от ", "")
                .replace(" ", "")
                .replace(",", ".")
                .replace("ƃ", "")
            )

        try:
            price = float(price.replace("от ", "").replace("ƃ", ""))

        except (
            ValueError,
            TypeError,
        ):
            print(
                f"Не удалось обработать цену: "
                f"{price}"
            )
            continue

        img_url = product.find("img")["src"]

        product = save_product(
            shop_product_id='',
            title=title,
            price=price,
            product_url=url,
            img_url=img_url,
            shop_name="onliner",
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

    try:

        products = parse_onliner(name)

        print()
        print(
            f"Saved to database: "
            f"{len(products)} products"
        )

    except Exception as error:

        print(
            f"Parser error: {error}"
        )
