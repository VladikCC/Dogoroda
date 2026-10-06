from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database.db_config import SessionLocal, Product, init_db

from parsers.pars_onliner import parse_onliner
from parsers.pars_21vek import parse_21vek

init_db()

app = FastAPI(title="Dogoroda.store API")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://127.0.0.1:3006"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

class Response:
    def __init__(self, status, items):
        self.status = status
        self.items = items

class Item:
    title: str
    price: str
    img: str
    url: str
    shop: str


@app.get("/")
async def home():
    return {"status": "working", "message": "Welcome to Dogoroda.store Backend API!"}

@app.get("/search/{search}")
async def find_stuff(search: str):
    results = [
        parse_onliner(search),
        parse_21vek(search)
    ]

    result = []

    for shop in results:
        item = Item()
        for res in shop:
            item.title = res.title
            item.price = res.price
            item.img = res.img_url
            item.url = res.product_url
            item.shop = res.shop_name
            result.append(item)

    return Response("done", result)


# @app.get("/search/{search}")
# async def search_products(query: str = Query(None, min_length=2)):
#     db = SessionLocal()
#     try:
#         if not query:
#             return []
#         results = db.query(Product).filter(
#             Product.title.ilike(f"%{query}%")
#         ).order_by(Product.price.asc()).all()
        
#         return results
#     except Exception as e:
#         return {"error": f"Database search failed: {e}"}
#     finally:
#         db.close()
