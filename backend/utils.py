from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import User, SessionLocal,AccTokenMapping
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from hashlib import sha512
from os import getenv
from jose import JWTError
from typing import Tuple,Optional

SECRET_KEY = sha512(getenv('SECRET_KEY', 'dev').encode('ascii')).hexdigest()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3*60  # 令牌过期时间（3h自动登录）
REFRESH_TOKEN_EXPIRE_MINUTES = 7*24*60  # 刷新令牌过期时间，设置为7天
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def check_username_and_password(email: str, password: str, db: Session) -> Tuple[bool, bool]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False, False
    if user.disabled:
        return True, False
    return True, True


def create_access_token(*, data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 使用变量设置令牌有效期为7天
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 把刷新令牌的逻辑给加回来
def create_refresh_token(*, data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def store_token_info(access_token: str, refresh_token: str, db: Session, exp_timestamp: int = None):
    """
    将访问令牌和刷新令牌及其过期时间存入数据库。

    :param db: 数据库会话实例。
    :param access_token: 生成的访问令牌。
    :param refresh_token: 生成的刷新令牌。
    :param exp_timestamp: 刷新令牌的过期时间戳，如果未提供，则使用默认计算方法。
    """
    # 如果没有提供过期时间戳，使用默认的计算方法
    if exp_timestamp is None:
        exp_at = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        exp_timestamp = int(exp_at.timestamp())

    # 创建一个新的AccTokenMapping实例并添加到数据库
    token_mapping = AccTokenMapping(access_token=access_token, refresh_token=refresh_token, exp_at=exp_timestamp)
    db.add(token_mapping)
    db.commit()

def verify_token(token: str) -> Tuple[Optional[str], bool]:
    """
    验证令牌的有效性并提取用户邮箱。返回email和令牌是否有效的信息。
    :param token: 提供的JWT令牌。
    :return: 一个元组，其中第一个元素是email（如果提取成功），否则为None；
             第二个元素是一个布尔值，表示令牌是否有效（未过期）。
    """
    try:
        # 尝试解码，忽略过期检查
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        email = payload.get("sub")
        if not email:
            return None, False  # 没有email，令牌无效

        # 再次尝试解码，不忽略过期检查，来确定令牌是否真的过期
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return email, True  # 令牌有效
    except ExpiredSignatureError:
        return email, False  # 令牌过期，但email仍然提取成功
    except JWTError:
        return None, False  # 解码失败，令牌无效


def verify_token_and_check_db(token: str, db: Session) -> Tuple[Optional[str], bool]:
    """
    验证令牌的有效性，并检查它是否存在于数据库中。
    :param token: 提供的JWT令牌。
    :param db: 数据库会话实例。
    :return: 一个元组，其中第一个元素是email（如果提取成功），否则为None；
             第二个元素是一个布尔值，表示令牌是否有效（未过期）。
    """
    email, is_valid = verify_token(token)  # 调用已有的验证函数
    if not is_valid:
        return email, False  # 令牌无效或已过期

    # 在数据库中检查token是否存在
    token_exists = db.query(AccTokenMapping).filter(AccTokenMapping.access_token == token).first() is not None
    if not token_exists:
        return email, False  # 令牌不在数据库中

    return email, True  # 令牌在数据库中存在且有


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    email, token_expired = verify_token_and_check_db(token,db)
    if not token_expired:
        # 如果令牌过期，直接抛出异常提示令牌过期
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # # 如果无法根据电子邮件找到用户，抛出用户未找到的异常
        # raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def handle_refresh_token_expiration(db: Session, email: str) -> Tuple[str, int]:
    """处理刷新令牌即将过期的情况，返回新的刷新令牌和过期时间。"""

    # 使用现有的逻辑生成新的刷新令牌
    new_refresh_token = create_refresh_token(data={"sub": email})
    new_exp_at = int((datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)).timestamp())

    return new_refresh_token, new_exp_at

def refresh_token_logic(db: Session, refresh_token: str, SECRET_KEY: str, ALGORITHM: str) -> (str, int):
    """
    处理刷新令牌的逻辑，包括解码刷新令牌、检查有效性和生成新的令牌。
    :param db: 数据库会话实例。
    :param refresh_token: 当前的刷新令牌。
    :param SECRET_KEY: 用于JWT编解码的秘钥。
    :param ALGORITHM: 使用的JWT算法。
    :return: 新的刷新令牌和它的过期时间戳。
    """
    try:
        # 解码刷新令牌，检查过期
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        exp_at = payload.get("exp")

        if not email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

        current_utc_timestamp = int(datetime.now(timezone.utc).timestamp())

        # 如果刷新令牌即将过期，生成新的刷新令牌
        if exp_at - current_utc_timestamp < REFRESH_TOKEN_EXPIRE_MINUTES * 60 / 7:
            new_refresh_token, new_exp_at = handle_refresh_token_expiration(db, email)
        else:
            new_refresh_token = refresh_token
            new_exp_at = exp_at

        return new_refresh_token, new_exp_at

    except ExpiredSignatureError:
        # 令牌过期，直接抛出异常
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is expired")
    except JWTError:
        # 令牌解码失败或其他JWT错误
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid refresh token")

def generate_and_store_tokens(db: Session, email: str, refresh_token: str, exp_at: int) -> str:
    """生成新的访问令牌，更新数据库，并返回新的访问令牌。"""
    new_access_token = create_access_token(data={"sub": email})
    new_token_data = AccTokenMapping(access_token=new_access_token, refresh_token=refresh_token, exp_at=exp_at)
    db.add(new_token_data)
    db.commit()
    return new_access_token

def delete_specific_token_record(db: Session, access_token: str):
    """
    删除与给定访问令牌相关的记录。
    :param db: 数据库会话实例。
    :param access_token: 需要删除记录的访问令牌。
    """
    records_deleted = db.query(AccTokenMapping).filter(AccTokenMapping.access_token == access_token).delete()
    db.commit()
    return records_deleted > 0  # 返回是否成功删除了记录