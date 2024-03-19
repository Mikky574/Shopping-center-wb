from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import User, SessionLocal, TokenBlacklist  # 调整导入以匹配你的项目结构
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha512
from os import getenv
from jose import JWTError
from typing import Tuple
# import redis

SECRET_KEY = sha512(getenv('SECRET_KEY', 'dev').encode('ascii')).hexdigest()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌过期时间
REFRESH_TOKEN_EXPIRE_MINUTES = 43200  # 刷新令牌过期时间，设置为30天
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# # 假设您的Redis运行在本地，默认端口6379
# redis_client = redis.Redis(host='localhost', port=6379,
#                            db=0, decode_responses=True)


# def add_token_to_blacklist(token: str, expire_seconds: int):
#     # 将令牌设置为黑名单中的一个键，值为"invalid"，并设置过期时间
#     redis_client.set(token, "invalid", ex=expire_seconds)

# def is_token_blacklisted(token: str, redis_client) -> bool:
#     # 在Redis中查找令牌，如果找到，表示令牌在黑名单中
#     return redis_client.exists(token)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# def add_token_to_blacklist(token: str, expire_seconds: int,db: Session = Depends(get_db)):
#     db.add(TokenBlacklist(token=token, created_at=datetime.now(
#         timezone.utc), expires_in=expire_seconds))
#     db.commit()

import time

def add_token_to_blacklist(token: str, expires_seconds: int, db: Session):
    expires_at = int(time.time()) + expires_seconds
    db.add(TokenBlacklist(token=token, expires_at=expires_at))
    db.commit()


# def is_token_blacklisted(token: str, db: Session) -> bool:
#     token_record = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
#     if token_record:
#         # 确保比较使用的都是带时区的datetime
#         expiration_date = token_record.created_at + timedelta(seconds=token_record.expires_in)
#         current_time = datetime.now(timezone.utc)  # 确保当前时间也是带UTC时区的
#         if expiration_date > current_time:
#             return True  # 令牌未过期且在黑名单中
#     return False  # 令牌不在黑名单中或已过期

def is_token_blacklisted(token: str, db: Session) -> bool:
    current_time = int(time.time())
    token_record = db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first()
    if token_record and token_record.expires_at > current_time:
        return True  # 令牌在黑名单中且未过期
    return False  # 令牌不在黑名单中或已过期



def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def check_username_and_password(db: Session, email: str, password: str) -> Tuple[bool, bool]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False, False
    if user.disabled:
        return True, False
    return True, True


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(
        timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta if expires_delta else datetime.now(
        timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str, db: Session) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 首先检查令牌是否在黑名单中
        # if is_token_blacklisted(token, redis_client):
        if is_token_blacklisted(token,db):
            raise credentials_exception
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 首先检查令牌是否在黑名单中
        # if is_token_blacklisted(token, redis_client):
        if is_token_blacklisted(token,db):
            raise credentials_exception

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()

        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        raise credentials_exception
