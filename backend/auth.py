from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import User, UserInfo, SessionLocal
from utils import (
    hash_password,
    check_username_and_password,
    create_access_token,
    get_current_user,
    add_token_to_blacklist,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES)
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from fastapi import HTTPException, APIRouter, Depends, Header, Body
from sqlalchemy.orm import Session
from database import SessionLocal, User
from utils import create_access_token, verify_refresh_token, create_refresh_token

class RegisterUser(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    # email由邮箱格式来保证

    @validator('password')
    def check_password_not_empty(cls, value):
        if not value:
            raise HTTPException(
                status_code=422, detail="password must not be empty")
        return value


class LoginFormData(BaseModel):
    email: str
    password: str


class UserMe(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    # disabled: bool

    class Config:
        from_attributes = True


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/users/register", status_code=status.HTTP_200_OK)
async def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    try:
        # 检查邮箱是否已经注册
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email already registered")

        # 加密密码
        hashed_password = hash_password(user.password)
        # 创建User实例
        new_user = User(email=user.email,
                        hashed_password=hashed_password, disabled=False)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 总是创建UserInfo实例，即使信息部分为空
        db_user_info = UserInfo(
            user_id=new_user.id,
            first_name=user.first_name if user.first_name else "",  # 如果提供了信息，则使用提供的信息，否则使用空字符串
            last_name=user.last_name if user.last_name else "",  # 同上
            phone_number=user.phone_number if user.phone_number else ""  # 同上
        )
        db.add(db_user_info)
        db.commit()

        # 只返回HTTP状态码200，表示成功，不返回用户信息
        return {"message": "User registered successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/users/login")
async def login_user(form_data: LoginFormData, db: Session = Depends(get_db)):
    user_email = form_data.email
    password = form_data.password
    is_authenticated, not_disabled = check_username_and_password(
        db, user_email, password)

    if not is_authenticated:
        raise HTTPException(
            status_code=400, detail="Incorrect email or password")
    if not not_disabled:
        raise HTTPException(status_code=403, detail="User is disabled")

    access_token = create_access_token(data={"sub": user_email})
    refresh_token = create_refresh_token(data={"sub": user_email})  # 生成刷新令牌

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # 返回刷新令牌
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_expires_in": REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/users/logout")
async def logout_user(authorization: str = Header(None),  body: dict = Body(...),db: Session = Depends(get_db)):
    refresh_token = body.get("refresh_token", "")
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]
        # 获取Redis客户端实例，用于操作黑名单
        # 禁用访问令牌
        add_token_to_blacklist(access_token, ACCESS_TOKEN_EXPIRE_MINUTES * 60,db)
        # 禁用刷新令牌
        add_token_to_blacklist(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60,db)
        
        return {"message": "You have been logged out."}
    else:
        raise HTTPException(status_code=401, detail="Invalid authorization header.")



@router.get("/me", response_model=UserMe)
def read_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_info = db.query(UserInfo).filter(
        UserInfo.user_id == current_user.id).first()
    if user_info:
        return UserMe(
            email=current_user.email,
            first_name=user_info.first_name,
            last_name=user_info.last_name,
            phone_number=user_info.phone_number,
            # disabled=current_user.disabled
        )
    else:
        raise HTTPException(
            status_code=404, detail="User information not found")


@router.post("/users/refresh_token")
async def refresh_access_token(body: dict = Body(...), db: Session = Depends(get_db)):
    refresh_token = body.get("refresh_token", "")
    user = verify_refresh_token(refresh_token, db)
    if not user:
        raise HTTPException(
            status_code=403, detail="Refresh token is invalid or expired")

    new_access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
