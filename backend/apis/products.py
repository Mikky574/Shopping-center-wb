from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Product
from utils import get_db
from typing import List
from datetime import datetime

from pydantic import BaseModel

# Pydantic模型用于响应格式化
class ProductModel(BaseModel):
    id: int
    model: str
    sku: str
    mpn: str
    quantity: int
    stock_status_id: int
    image_url: str
    manufacturer_id: int
    price: float
    date_available: datetime
    weight_grams: float
    viewed: int
    date_added: datetime
    date_modified: datetime

    class Config:
        orm_mode = True  # 允许将ORM模型转换为Pydantic模型


router = APIRouter()

# @router.get("/products/{product_id}", response_model=Product)
# async def get_product(product_id: str, db: Session = Depends(get_db)):
#     product = db.query(Product).filter(Product.id == product_id).first()
#     if not product:
#         raise HTTPException(status_code=404, detail="Product not found")
#     return product

@router.get("/{product_id}", response_model=ProductModel)
async def get_product(product_id: int, db: Session = Depends(get_db)):  # product_id 应为 int 类型
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product