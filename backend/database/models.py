from sqlalchemy import Boolean, Column, Integer, String, ForeignKey,DECIMAL, Date,DateTime,Numeric,Text
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # 使用email作为唯一标识
    hashed_password = Column(String)  # 加密密码
    disabled = Column(Boolean, default=False)  # 用户是否被禁用
    info = relationship("UserInfo", back_populates="user",
                        uselist=False)  # 与UserInfo建立一对一关系
    
    #################################################
    # todo: 一对多关系 -> Cart
    # todo: 一对多关系 -> Order
    # todo: 一对多关系 -> PaymentInfo
    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    payment_infos = relationship("PaymentInfo", back_populates="user")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    #################################################

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)  
    first_name = Column(String, nullable=False)  # 名
    last_name = Column(String, nullable=False)  # 姓
    phone_number = Column(String, nullable=False)  # 电话号码
    user = relationship("User", back_populates="info")  # 建立与User的反向关系
    currency_id = Column(Integer, ForeignKey('currency.id'))  
    payment_info = Column(String, ForeignKey('payment_info.id'), nullable=True)

class Currency(Base):
    __tablename__ = 'currency'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    symbol = Column(String(1), unique=True, nullable=False)

class AccTokenMapping(Base):
    __tablename__ = 'acc_token_mapping'
    access_token = Column(String, primary_key=True, nullable=False)
    refresh_token = Column(String, nullable=False)
    exp_at = Column(Integer, nullable=False)  # 使用Integer来存储时间戳

import enum
from sqlalchemy import Enum

class PaymentTypeEnum(enum.Enum):
    bank = 'bank'
    check = 'check'
    paypal = 'paypal'
 
class PaymentInfo(Base):
    __tablename__ = 'payment_info'
    id = Column(Integer, primary_key=True) 
    user_id = Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    payment_type = Column(Enum(PaymentTypeEnum), nullable=False)
    info = Column(String, nullable=False)
    # todo：反向一对多关系 -> User
    user = relationship("User", back_populates="payment_infos")

#################################

# class Product(Base):
#     __tablename__ = 'product'
#     id = Column(String, primary_key=True)  # 根据类型定义，ID 是字符串
#     name = Column(String, nullable=False)
#     description = Column(String, nullable=False)
#     price = Column(Numeric(10, 2), nullable=False)  # 使用 Numeric 类型支持小数点
#     currency_symbol = Column(String, nullable=False)
#     weight_grams = Column(Integer, nullable=False)
#     image_url = Column(String, nullable=False)  # 存储图片的 URL
#     # todo：反向多对一关系 -> Cart
#     # todo：反向多对一关系 -> Order
#     carts = relationship("Cart", back_populates="product")
#     orders = relationship("Order", back_populates="product")

class Product(Base):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True, index=True)  # 使用oc_product的product_id作为主键
    model = Column(String(64), nullable=False)
    sku = Column(String(64), nullable=True)  # SKU 可能不是必须的，可以设置为 nullable
    mpn = Column(String(64), nullable=True)  # 同上
    quantity = Column(Integer, nullable=False, default=0)
    # stock_status_id = Column(Integer, nullable=True)  # 如果这是一个外键，需要添加ForeignKey
    image_url = Column(String(255), nullable=True)  # 存储图片URL，转换为完整的URL路径
    # manufacturer_id = Column(Integer, nullable=True)  # 如果这是一个外键，需要添加ForeignKey
    price = Column(DECIMAL(15, 4), nullable=False)
    # date_available = Column(Date, nullable=False)
    weight_grams = Column(DECIMAL(15, 8), nullable=False)  # 需要转换成克
    viewed = Column(Integer, nullable=False, default=0)
    # date_added = Column(DateTime, nullable=False)
    # date_modified = Column(DateTime, nullable=False)
    
    # todo：反向多对一关系 -> Cart
    # todo：反向多对一关系 -> Order
    carts = relationship("Cart", back_populates="product")
    orders = relationship("Order", back_populates="product")

    descriptions = relationship("ProductDescribe", back_populates="product")  # 反向多对一关系


class ProductDescribe(Base):
    __tablename__ = 'product_describe'
    
    id = Column(Integer, primary_key=True, index=True)  # 主键
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)  # 关联 Product 表
    # language_id = Column(Integer, nullable=False)  # 语言 ID
    name = Column(String(255), nullable=False)  # 产品名称
    description = Column(Text, nullable=False)  # 详细描述

    product = relationship("Product", back_populates="descriptions")  # 与 Product 表建立关系

#####################################################

class Cart(Base):
    __tablename__ = 'cart'
    id = Column(Integer, primary_key=True)
    user_id =  Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    # todo：反向一对多关系 -> User
    # todo：多对一关系 -> Product
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")

from sqlalchemy.sql.functions import now

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id =  Column(Integer, ForeignKey('users.id'), index=True, nullable=False)
    order_time = Column(DateTime, default=now())
    invoice_id = Column(String, nullable=True) 
    total = Column(Integer, nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False) 
    payment_info = Column(String, ForeignKey('payment_info.id'), nullable=True)
    # todo：反向一对多关系 -> User
    # todo：多对一关系 -> Product
    user = relationship("User", back_populates="orders")
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="orders")
    

## 地址部分

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    address_1 = Column(String, nullable=False)
    address_2 = Column(String, nullable=False)
    address_3 = Column(String, nullable=True)
    city_state = Column(String, nullable=False)
    zip = Column(String, nullable=False)
    country = Column(String, nullable=False)
    user = relationship("User", back_populates="addresses")

