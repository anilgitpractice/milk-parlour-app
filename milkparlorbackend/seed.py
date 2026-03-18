from sqlalchemy.orm import Session

from database import SessionLocal
from models import Product


def seed_products(db: Session) -> None:
    has_any = db.query(Product).first() is not None
    if has_any:
        return

    products = [
        Product(name="Full Cream Milk 500ml", price=35.0, stock=150),
        Product(name="Toned Milk 500ml", price=28.0, stock=200),
        Product(name="Fresh Cow Milk 1L", price=80.0, stock=50),
        Product(name="Buffalo Milk 1L", price=90.0, stock=40),
        Product(name="Fresh Curd 250g", price=20.0, stock=100),
        Product(name="Fresh Paneer 200g", price=85.0, stock=30),
        Product(name="Pure Ghee 250g", price=250.0, stock=20),
    ]

    db.add_all(products)
    db.commit()


def seed_on_startup() -> None:
    db = SessionLocal()
    try:
        seed_products(db)
    finally:
        db.close()

