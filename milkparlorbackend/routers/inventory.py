from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Product, ProductRead, ProductUpdateStock


router = APIRouter()


@router.get("/stock", response_model=List[ProductRead])
async def list_products(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.id.asc()).all()


@router.patch("/stock/{product_id}", response_model=ProductRead)
async def update_product_stock(
    product_id: int, payload: ProductUpdateStock, db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    product.stock = payload.stock
    db.commit()
    db.refresh(product)
    return product

