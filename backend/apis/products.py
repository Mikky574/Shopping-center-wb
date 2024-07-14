from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import Product, ProductDescribe
from utils import get_db
from typing import List
from pydantic import BaseModel
from pathlib import Path
import platform
import html

from typing import Optional

# Pydantic模型用于响应格式化
class ProductModel(BaseModel):
    id: int  # 产品ID，唯一标识符
    model: str  # 产品型号，只需要这个作为产品名称
    sku: str
    mpn:str
    quantity: int  # 库存数量
    image_url: str  # 产品图片URL，首个产品的图片。先这样，后面会改为list
    price: float  # 产品价格
    weight_grams: float
    sold_count: Optional[int] = None  # 销售数量，可选字段
    name: Optional[str] = None  # 产品名称，可选字段

    class Config:
        orm_mode = True  # 使用orm_mode以支持从SQLAlchemy模型自动转换

router = APIRouter()

def correct_path(path_str: str) -> str:
    parts = path_str.split('/')
    corrected_parts = [part if not part.endswith(' ') else part[:-1] + '_' for part in parts]
    corrected_path = '/'.join(corrected_parts)
    return corrected_path


@router.get("/id/{product_id}", response_model=ProductModel)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    result = db.query(Product).filter(Product.id == product_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if platform.system() == "Windows":
        result.image_url = correct_path(result.image_url)
    
    result.image_url = f"/api/image/{result.image_url}"  # Construct the full image URL
    
    # Convert SQLAlchemy object to dictionary for optional fields
    product_dict = {
        "id": result.id,
        "model": result.model,
        "sku": result.sku,
        "mpn": result.mpn,
        "quantity": result.quantity,
        "image_url": result.image_url,
        "price": result.price,
        "weight_grams": result.weight_grams,
        "sold_count": getattr(result, 'viewed', None),  # Assuming 'viewed' might be used for 'sold_count'
        "name": getattr(result, 'name', None)  # Only include this line if 'name' is a direct attribute of Product
    }
    # print(product_dict)

    return product_dict


class ProductDescriptionModel(BaseModel):
    description: str

@router.get("/id/{product_id}/desc", response_model=ProductDescriptionModel)
async def get_product_description(product_id: int, db: Session = Depends(get_db)):
    result = db.query(ProductDescribe.description)\
               .filter(ProductDescribe.product_id == product_id)\
               .first()

    if not result:
        raise HTTPException(status_code=404, detail="Product description not found")

    decoded_description = html.unescape(result.description)  # 确保这里使用了正确的属性访问方式

    return ProductDescriptionModel(description=decoded_description)


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

