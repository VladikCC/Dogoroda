import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://vladik_admin:YOUR_PASSWORD@localhost:5432/dogoroda_base"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    shop_product_id = Column(
        String,
        index=True,
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    price = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String,
        nullable=False,
        default="BYN",
    )

    product_url = Column(
        String,
        unique=True,
        nullable=False,
    )

    img_url = Column(
        String,
        nullable=True,
    )

    shop_name = Column(
        String,
        nullable=False,
        default="21vek",
    )

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def save_product(
    *,
    shop_product_id: str,
    title: str,
    price: float,
    product_url: str,
    img_url: str | None = None,
    shop_name: str = "21vek",
    currency: str = "BYN",
):
    db = SessionLocal()

    try:
        existing_product = (
            db.query(Product)
            .filter(
                Product.product_url == product_url
            )
            .first()
        )

        if existing_product:

            #update product
            existing_product.shop_product_id = shop_product_id
            existing_product.title = title
            existing_product.price = price
            existing_product.currency = currency
            existing_product.img_url = img_url
            existing_product.shop_name = shop_name
            existing_product.updated_at = datetime.now()

            product = existing_product

        else:

            product = Product(
                shop_product_id=shop_product_id,
                title=title,
                price=price,
                currency=currency,
                product_url=product_url,
                img_url=img_url,
                shop_name=shop_name,
            )

            db.add(product)

        db.commit()
        db.refresh(product)

        return product

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()