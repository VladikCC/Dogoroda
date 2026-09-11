import re
import random
import time

from bs4 import BeautifulSoup
import requests

from database.db_config import SessionLocal, Product


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
}


SHOPS_CONFIG = {
    "21vek": {
        "item_selector": "div[data-code], [class*='cr-item'], dl.cr-item",
        "title_selector": (
            "a[href*='mobile_phones'], "
            "a[class*='title'], h3, .j-item-title"
        ),
        "price_selector": (
            "[class*='price'], span[class*='price'], .g-price, b"
        ),
        "img_selector": "img",
        "id_attr": "data-code",
    },
}


def get_soup(url: str):
    """Общий HTML-загрузчик для простых HTML-парсеров."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            return BeautifulSoup(response.text, "lxml")

        print(
            f"[Core] Error downloading {url}: "
            f"Status code {response.status_code}"
        )
        return None

    except Exception as error:
        print(
            f"[Core] Request exception for {url}: {error}"
        )
        return None


def save_or_update_product(product_data: dict):
    """
    Общий слой сохранения товара в PostgreSQL.

    Парсеры сами получают и разбирают данные,
    а сюда передают уже нормализованный product_data.
    """

    db = SessionLocal()

    try:
        existing = (
            db.query(Product)
            .filter(
                Product.product_url
                == product_data["product_url"]
            )
            .first()
        )

        if existing:
            existing.shop_product_id = (
                product_data.get("shop_product_id")
            )
            existing.title = product_data["title"]
            existing.price = float(product_data["price"])
            existing.img_url = product_data.get("img_url")
            existing.shop_name = product_data["shop_name"]

            if hasattr(existing, "currency"):
                existing.currency = product_data.get(
                    "currency",
                    "BYN",
                )

            print(
                f"[DB] Updated: "
                f"{product_data['title']} -> "
                f"{product_data['price']} "
                f"{product_data.get('currency', 'BYN')}"
            )

        else:
            product_kwargs = {
                "shop_product_id": (
                    product_data.get("shop_product_id")
                ),
                "title": product_data["title"],
                "price": float(product_data["price"]),
                "product_url": product_data["product_url"],
                "img_url": product_data.get("img_url"),
                "shop_name": product_data["shop_name"],
            }

            if hasattr(Product, "currency"):
                product_kwargs["currency"] = product_data.get(
                    "currency",
                    "BYN",
                )

            new_product = Product(**product_kwargs)

            db.add(new_product)

            print(
                f"[DB] Added: "
                f"{product_data['title']}"
            )

        db.commit()

    except Exception as error:
        db.rollback()

        print(
            f"[DB] Error saving item to database: "
            f"{error}"
        )

        raise

    finally:
        db.close()


def universal_shop_parser(
    shop_name: str,
    url: str,
    base_domain: str = "",
):
    """
    Универсальный HTML-парсер для магазинов,
    которые можно описать через SHOPS_CONFIG.

    Сложные сайты вроде 21vek могут иметь
    собственный parser и собственный get_soup().
    """

    if shop_name not in SHOPS_CONFIG:
        print(
            f"[Core] Конфигурация для магазина "
            f"{shop_name} не найдена!"
        )
        return

    print(
        f"[Core] Запуск универсального "
        f"парсера для: {shop_name}"
    )

    soup = get_soup(url)

    if not soup:
        return

    cfg = SHOPS_CONFIG[shop_name]

    items = soup.select(
        cfg["item_selector"]
    )

    print(
        f"[Core] Найдено товаров "
        f"на странице {shop_name}: "
        f"{len(items)}"
    )

    for item in items:

        try:
            delay = random.uniform(
                0.3,
                1.5,
            )
            time.sleep(delay)

            title_element = item.select_one(
                cfg["title_selector"]
            )

            if not title_element:
                continue

            title = title_element.text.strip()

            product_url = (
                title_element.get("href")
                or (
                    title_element.find("a")
                    and title_element.find("a").get("href")
                )
            )

            if not product_url:
                product_url = (
                    item.get("href")
                    or (
                        item.find("a")
                        and item.find("a").get("href")
                    )
                )

            if not product_url:
                continue

            if (
                base_domain
                and not product_url.startswith("http")
            ):
                product_url = (
                    base_domain
                    + product_url
                )

            price_element = item.select_one(
                cfg["price_selector"]
            )

            if not price_element:
                continue

            price_raw = price_element.text.strip()

            price_clean = re.sub(
                r"[^\d.,]",
                "",
                price_raw,
            )

            price_clean = (
                "".join(price_clean.split())
                .replace(",", ".")
            )

            if not price_clean:
                continue

            try:
                price = float(price_clean)

            except ValueError:

                price_only_digits = re.sub(
                    r"[^\d]",
                    "",
                    price_raw,
                )

                if len(price_only_digits) > 2:
                    price = float(
                        price_only_digits[:-2]
                        + "."
                        + price_only_digits[-2:]
                    )
                else:
                    continue

            img_element = item.select_one(
                cfg["img_selector"]
            )

            img_url = (
                img_element["src"]
                if img_element
                and img_element.has_attr("src")
                else None
            )

            shop_product_id = (
                item.get(cfg["id_attr"])
                or item.get("id")
            )

            product_data = {
                "shop_product_id": (
                    str(shop_product_id)
                    if shop_product_id
                    else None
                ),
                "title": title,
                "price": price,
                "product_url": product_url,
                "img_url": img_url,
                "shop_name": shop_name,
                "currency": "BYN",
            }

            save_or_update_product(
                product_data
            )

        except Exception as error:

            print(
                f"[Core] КРИТИЧЕСКАЯ ОШИБКА "
                f"в карточке: {error}"
            )

            import traceback

            traceback.print_exc()

            continue
