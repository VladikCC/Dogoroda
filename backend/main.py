from fastapi import FastAPI, Query
from database.db_config import SessionLocal, Product, init_db

from parsers.pars_onliner import parse_onliner
from parsers.pars_21vek import parse_21vek

init_db()

app = FastAPI(title="Dogoroda.store API")

@app.get("/")
async def home():
    return {"status": "working", "message": "Welcome to Dogoroda.store Backend API!"}

@app.get("/search/{search}")
async def find_stuff(search: str):
    results = [
        parse_onliner(search),
        parse_21vek(search)
    ]

    result = {"status": "searching"}

    for shop in results:
        for res in shop:
            id = res.id
            result[f"{id}_title"] = res.title
            result[f"{id}_price"] = res.price
            result[f"{id}_img"] = res.img_url
            result[f"{id}_url"] = res.product_url
            result[f"{id}_shop"] = res.shop_name

    return result


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
