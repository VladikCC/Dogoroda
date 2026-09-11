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


BASE_DIR = Path(__file__).resolve().parent

COOKIES_FILE = (
    BASE_DIR
    / "cookies"
    / "cookies-21vek-by.txt"
)


def parse_cookies(cookies_file: Path):
    
    cookies = {}

    if not cookies_file.exists():
        print(
            f"Cookies file not found: {cookies_file}"
        )
        return cookies

    with open(
        cookies_file,
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if not line.strip():
                continue

            if line.startswith("#"):
                continue

            fields = line.strip().split("\t")

            if len(fields) >= 7:
                cookies[fields[5]] = fields[6]

    return cookies


def get_soup(url: str):

    cookies = parse_cookies(COOKIES_FILE)

    response = requests.get(
        url,
        headers=HEADERS,
        cookies=cookies,
        timeout=30,
    )

    response.raise_for_status()

    return BeautifulSoup(
        response.text,
        "html.parser",
    )


def parse_21vek(search_name: str):
   
    search_name = search_name.strip()

    if not search_name:
        raise ValueError(
            "Название товара не может быть пустым"
        )

    url = (
        "https://21vek.by/search/"
        f"?sa=&term="
        f"{requests.utils.quote(search_name)}"
    )

    print(f"Searching: {search_name}")
    print(f"URL: {url}")

    soup = get_soup(url)

    script = soup.find(
        "script",
        {"id": "__NEXT_DATA__"},
    )

    if not script:
        raise RuntimeError(
            "__NEXT_DATA__ not found"
        )

    data = json.loads(
        script.string
    )

    inner = json.loads(
        data["props"]["pageProps"]["initialState"]
    )

    products = (
        inner
        .get("searchResult", {})
        .get("products", {})
        .get("all", [])
    )

    if not products:
        print("Products not found")
        return []

    saved_products = []

    for item in products:

        shop_product_id = (
            item.get("id")
            or item.get("productId")
        )

        if shop_product_id is None:
            print(
                "Пропускаем товар: "
                "нет ID"
            )
            continue

        shop_product_id = str(
            shop_product_id
        )

        title = item.get("name")

        if not title:
            print(
                "Пропускаем товар: "
                "нет названия"
            )
            continue

        if search_name.casefold() not in title.casefold():
            print(f"Пропускаем {title}: нет '{search_name}' в названии")
            continue

        price = (
            item.get("salePrice")
            or item.get("price")
        )

        if price is None:
            print(
                f"Пропускаем {title}: "
                "нет цены"
            )
            continue

        if isinstance(price, str):
            price = (
                price
                .replace(" ", "")
                .replace(",", ".")
            )

        try:
            price = float(price)

        except (
            ValueError,
            TypeError,
        ):
            print(
                f"Не удалось обработать цену: "
                f"{price}"
            )
            continue

        product_url = (
            item.get("link")
            or item.get("url")
            or item.get("productUrl")
        )

        if not product_url:
            print(
                f"Пропускаем {title}: "
                "нет URL товара"
            )
            continue

        if product_url.startswith("/"):
            product_url = (
                "https://21vek.by"
                + product_url
            )

        img_url = (
            item.get("image")
            or item.get("imageUrl")
        )

        if img_url and img_url.startswith("/"):
            img_url = (
                "https://21vek.by"
                + img_url
            )

        product = save_product(
            shop_product_id=shop_product_id,
            title=title,
            price=price,
            product_url=product_url,
            img_url=img_url,
            shop_name="21vek",
            currency="BYN",
        )

        saved_products.append(product)

        print()
        print("SAVED:")
        print(
            f"ID сайта: "
            f"{product.shop_product_id}"
        )
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

        products = parse_21vek(name)

        print()
        print(
            f"Saved to database: "
            f"{len(products)} products"
        )

    except Exception as error:

        print(
            f"Parser error: {error}"
        )