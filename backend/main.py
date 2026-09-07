from fastapi import FastAPI, Query
from database.db_config import SessionLocal, Product

app = FastAPI(title="Dogoroda.store API")

@app.get("/")
async def home():
    return {"status": "working", "message": "Welcome to Dogoroda.store Backend API!"}

@app.get("/api/search")
async def search_products(query: str = Query(None, min_length=2)):
    """Search endpoint for frontend. Fetches cached items from Postgres"""
    db = SessionLocal()
    try:
        if not query:
            return []
            
        #SQL equivalent
        results = db.query(Product).filter(
            Product.title.ilike(f"%{query}%")
        ).order_by(Product.price.asc()).all()
        
        return results
    except Exception as e:
        return {"error": f"Database search failed: {e}"}
    finally:
        db.close()
