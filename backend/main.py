import logging

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database.db_config import SessionLocal, Product, init_db

from parsers.pars_onliner import parse_onliner
from parsers.pars_21vek import parse_21vek
from parsers.pars_1k import parse_1k
from parsers.pars_shopby import parse_shopby
from parsers.pars_xistore import parse_xistore
from parsers.pars_silaby import parse_silaby
from parsers.pars_5element import parse_5element
from parsers.pars_mts import parse_mts
from parsers.pars_foxstore import parse_foxstore

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
def find_stuff(search: str):
    results = []
    for parser in (parse_onliner, parse_21vek, parse_1k, parse_shopby, parse_xistore, parse_silaby, parse_5element, parse_mts, parse_foxstore):
        try:
            results.append(parser(search))
        except Exception:
            logging.exception("Search failed in %s", parser.__name__)

    result = []

    for shop in results:
        for res in shop:
            item = Item()
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


""" TODO
 first, should implement fuzzy search
  second, need to group all the results. like, the same items from different shops are united into a single group with lowest price shown,
  and different items are separated. reduces clutter and improves readability
   third, search usually gives hundreds of results. that's normal, shops sites work similarly
"""