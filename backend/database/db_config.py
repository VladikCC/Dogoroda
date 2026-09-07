import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

#this for loc test todo server test
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://vladik_admin:BpVh9rokOXGEUDKwo5OsJX4rqw75xa@localhost:5432/dogoroda_base"
)

#FIXED
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#structure table data
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True) # ID in db
    
    #string for parsing
    shop_product_id = Column(String, index=True, nullable=True) # ID items
    title = Column(String, nullable=False)            # Full name
    model_name = Column(String, nullable=True)        # Model item
    price = Column(Float, nullable=False)              # price for items, use float type
    delivery_price = Column(Float, default=0.0)       # price delivery
    
    product_url = Column(String, unique=True, nullable=False) # url for item
    img_url = Column(String, nullable=True)           # URL-pictures
    shop_name = Column(String, nullable=False)        # name shop
    
    # service string(DevOps/Backend):
    # FIXED: changed deprecated utcnow to modern datetime.now
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now) # time for last parsing price

def init_db():
    """Эта функция автоматически создаст таблицы в вашей PostgreSQL, если их там ещё нет"""
    Base.metadata.create_all(bind=engine)
