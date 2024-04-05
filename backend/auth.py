from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import User, UserInfo
from utils import (
    hash_password,
    check_username_and_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_db,
    verify_password)
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session

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

from pydantic import BaseModel, EmailStr

class PasswordResetForm(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

@router.post("/users/reset-password")
async def reset_password(form_data: PasswordResetForm, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.email).first()

    # 检查用户是否存在
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 验证旧密码
    if not verify_password(form_data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    # 更新密码
    user.hashed_password = hash_password(form_data.new_password)
    db.commit()

    return {"message": "Password updated successfully."}


@router.post("/users/login")
async def login_user(form_data: LoginFormData, db: Session = Depends(get_db)):
    user_email = form_data.email
    password = form_data.password

    is_authenticated, not_disabled = check_username_and_password(user_email, password, db)

    if not is_authenticated:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not not_disabled:
        raise HTTPException(status_code=403, detail="User is disabled")

    access_token = create_access_token(data={"sub": user_email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES,  # 7天的秒数
    }


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

