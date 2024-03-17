from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import User,SessionLocal
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

router = APIRouter()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class RegisterUser(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users/register")
async def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    try:
        db.commit()
        return {"status": "success", "message": "User registered successfully."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")

# 检查用户登录
from typing import Tuple

def check_username_and_password(db: Session, username: str, password: str) -> Tuple[bool, bool]:
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return False, False  # 用户不存在或密码错误
    if user.disabled:
        return True, True  # 用户存在且被禁用
    return True, False  # 用户存在、密码正确且未被禁用


@router.post("/users/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    is_authenticated, is_disabled = check_username_and_password(db, form_data.username, form_data.password)
    
    if not is_authenticated:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if is_disabled:
        raise HTTPException(status_code=403, detail="User is disabled")  # 403 Forbidden表示资源不可用
    
    return {"status": "success", "message": "User logged in successfully."}


##########################
# OAuth2认证
##########################

# import jwt
# from datetime import datetime, timedelta
# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# import os

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# async def authenticate_user(username: str, password: str):
#     # 这里应该是验证用户名和密码的逻辑
#     # 假设有一个函数叫check_username_and_password
#     user = check_username_and_password(username, password)
#     if not user:
#         return False
#     return user

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# @router.post("/users/token")
# async def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == form_data.username).first()
#     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user.username}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# from jose import jwt, JWTError

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         user = db.query(User).filter(User.username == username).first()
#         if user is None:
#             raise credentials_exception
#         return user
#     except JWTError:
#         raise credentials_exception

# @router.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return {"username": current_user.username}
