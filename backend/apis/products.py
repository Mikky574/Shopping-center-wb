from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import Product, ProductDescribe
from utils import get_db
from typing import List
from pydantic import BaseModel
from pathlib import Path
import platform

# Pydantic模型用于响应格式化
class ProductModel(BaseModel):
    id: int # 
    model: str # 只需要这个作为产品名称
    # sku: str
    # mpn: str
    quantity: int # 库存容量
    # stock_status_id: int
    image_url: str # 首个产品的图片。先这样，后面会改为list
    # manufacturer_id: int
    price: float # 价格
    sold_count:int
    # 这些是Product表的
    ###########################
    # 这些是ProductDescribe表的
    name: str
    description:str
    class Config:
        from_attributes = True  # 替代原来的 orm_mode


router = APIRouter()

def correct_path(path_str: str) -> str:
    parts = path_str.split('/')
    corrected_parts = [part if not part.endswith(' ') else part[:-1] + '_' for part in parts]
    corrected_path = '/'.join(corrected_parts)
    return corrected_path

@router.get("/id/{product_id}", response_model=ProductModel)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    # Fetching product details including description using join
    result = db.query(Product.id, Product.model, Product.quantity, Product.image_url,
                      Product.price, ProductDescribe.name, Product.viewed, ProductDescribe.description)\
               .join(ProductDescribe, Product.id == ProductDescribe.product_id)\
               .filter(Product.id == product_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 检查操作系统
    if platform.system() == "Windows":
        image_url = correct_path(result[3])
    else:
        image_url = result[3]
        
    base_url = "/api/image"
    image_url = str(Path(base_url) / image_url)

    # Mapping query results to dictionary that matches Pydantic model
    product = {
        "id": result[0],  # product.id
        "model": result[1],  # product.model
        "quantity": result[2],  # product.quantity
        "image_url": image_url, # result[3],  # product.image_url
        "price": result[4],  # product.price
        "name": result[5],  # product_describe.name
        "sold_count": result[6],
        "description": result[7]  # product_describe.description
    }

    return ProductModel(**product)  # Creating a Pydantic model instance with unpacked data


# 放到这里下面

# # 简化的 Pydantic 模型，只包含需要的字段
# class SimpleProductModel(BaseModel):
#     id: int
#     img_url: str
#     name: str
#     model: str

#     class Config:
#         from_attributes = True  # 替代原来的 orm_mode


# @router.get("/popular", response_model=List[SimpleProductModel])
# async def get_popular_products(db: Session = Depends(get_db)):
#     # 从数据库查询访问次数最多的前八个商品，并包含产品ID
#     popular_products = db.query(
#         Product.id.label("id"),  # Including the product ID in the query
#         Product.image_url.label("img_url"),
#         Product.model,
#         ProductDescribe.name
#     ).join(
#         ProductDescribe, Product.id == ProductDescribe.product_id
#     ).order_by(
#         desc(Product.viewed)  # Sorting by the viewed count in descending order
#     ).limit(8).all()

#     if not popular_products:
#         raise HTTPException(status_code=404, detail="No popular products found")

#     # Mapping results into Pydantic models using list comprehension
#     return [SimpleProductModel(id=product.id, img_url=product.img_url, name=product.name, model=product.model) for product in popular_products]

@router.get("/popular", response_model=List[int])
async def get_popular_products(db: Session = Depends(get_db)):
    # 从数据库查询访问次数最多的前八个商品的ID
    popular_product_ids = db.query(
        Product.id
    ).order_by(
        desc(Product.viewed)  # 根据访问次数降序排序
    ).limit(8).all()

    if not popular_product_ids:
        raise HTTPException(status_code=404, detail="No popular products found")

    # 将查询结果中的ID提取出来形成一个列表
    return [product_id[0] for product_id in popular_product_ids]

