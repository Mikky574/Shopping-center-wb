# models.py
from sqlalchemy import Column, Integer, String
from .database import Base  # 注意根据你的项目结构调整导入路径

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

