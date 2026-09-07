import requests
from bs4 import BeautifulSoup
from database.db_config import SessionLocal, Product, init_db

#Automatically create tables in Postgres
init_db()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
}

def get_soup(url: str):
    """Universal function to download HTML and return BeautifulSoup object"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "lxml")
        print(f"[Core] Error downloading {url}: Status code {response.status_code}")
        return None
    except Exception as e:
        print(f"[Core] Request exception for {url}: {e}")
        return None

def save_or_update_product(product_data: dict):
    """Saves item to DB or updates its price if product_url already exists (UPSERT)"""
    db = SessionLocal()
    try:
        #Check if the product already exists
        existing = db.query(Product).filter(Product.product_url == product_data["product_url"]).first()
        
        if existing:
            #Update data that could have changed
            existing.price = float(product_data["price"])
            existing.delivery_price = float(product_data.get("delivery_price", 0.0))
            existing.title = product_data["title"]
            existing.img_url = product_data.get("img_url")
            print(f"[DB] Updated price for: {product_data['title']} -> {product_data['price']} BYN")
        else:
            #Insert a completely new item
            new_prod = Product(
                shop_product_id=product_data.get("shop_product_id"),
                title=product_data["title"],
                model_name=product_data.get("model_name"),
                price=float(product_data["price"]),
                delivery_price=float(product_data.get("delivery_price", 0.0)),
                product_url=product_data["product_url"],
                img_url=product_data.get("img_url"),
                shop_name=product_data["shop_name"]
            )
            db.add(new_prod)
            print(f"[DB] Added new item: {product_data['title']}")
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] Error saving item to database: {e}")
    finally:
        db.close()
