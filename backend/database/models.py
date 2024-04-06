from sqlalchemy import Boolean, Column, Integer, String, ForeignKey,DateTime
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

class UserInfo(Base):
    __tablename__ = "user_info"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    first_name = Column(String)  # 名
    last_name = Column(String)  # 姓
    phone_number = Column(String)  # 电话号码
    user = relationship("User", back_populates="info")  # 建立与User的反向关系


class AccTokenMapping(Base):
    __tablename__ = 'acc_token_mapping'

    access_token = Column(String, primary_key=True, index=True)
    refresh_token = Column(String, nullable=False)
    exp_at = Column(Integer, nullable=False)  # 使用Integer来存储时间戳

    def __repr__(self):
        return f"<TokenMapping(access_token='{self.access_token}', refresh_token='{self.refresh_token}', exp_at={self.exp_at})>"