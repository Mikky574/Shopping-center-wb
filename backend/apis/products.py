from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Product
from utils import get_db
from typing import List

router = APIRouter()

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

