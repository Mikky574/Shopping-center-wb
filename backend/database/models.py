from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from .database import Base  # 调整导入路径以匹配你的项目结构

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    # 在User模型定义中建立与UserInfo的一对一关系
    info = relationship("UserInfo", back_populates="user", uselist=False)

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    email = Column(String, unique=True, index=True)
    # 根据需要添加更多字段
    # 建立与User模型的反向关系
    user = relationship("User", back_populates="info")
