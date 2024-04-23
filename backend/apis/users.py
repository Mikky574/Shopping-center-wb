# 和登录有关的在这里叭
from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from utils import (
    oauth2_scheme,
    hash_password,
    check_username_and_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_db,
    verify_password,
    verify_token,
    store_token_info,
    refresh_token_logic,
    generate_and_store_tokens,
    delete_specific_token_record)
from database import User, UserInfo,AccTokenMapping
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
# router = APIRouter(prefix="/users")  # 添加路由前缀

@router.post("/register", status_code=status.HTTP_200_OK)
async def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    try:
        # 检查邮箱是否已经注册
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            print("y")
            raise HTTPException(
                status_code=400, detail="Email already registered") # 邮箱已被注册
        
        if not user.first_name and not user.last_name and not user.phone_number:
            raise HTTPException(
                status_code=422, detail="At least one of the following must be provided: first_name, last_name, phone_number")

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
            first_name=user.first_name, # if user.first_name else "",  # 如果提供了信息，则使用提供的信息，否则使用空字符串
            last_name=user.last_name, # if user.last_name else "",  # 同上
            phone_number=user.phone_number, # if user.phone_number else ""  # 同上
        )
        db.add(db_user_info)
        db.commit()

        # 只返回HTTP状态码200，表示成功，不返回用户信息
        return {"message": "User registered successfully."}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) # 关键词缺少

# from pydantic import BaseModel, EmailStr

class PasswordResetForm(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str

@router.post("/login")
async def login_user(form_data: LoginFormData, db: Session = Depends(get_db)):
    user_email = form_data.email
    password = form_data.password

    is_authenticated, not_disabled = check_username_and_password(user_email, password, db)

    if not is_authenticated:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not not_disabled:
        raise HTTPException(status_code=403, detail="User is disabled")

    access_token = create_access_token(data={"sub": user_email})
    # 同时要生成一个刷新令牌，进入数据库保存
    refresh_token = create_refresh_token(data={"sub": user_email})
    # 计算刷新令牌的过期时间戳
    store_token_info(access_token=access_token, refresh_token=refresh_token,db=db) # 存到数据库里面


    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES,  # 3h的分钟数
    }

@router.post("/reset_password")
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

@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    # 假设AccTokenMapping有一个字段表示令牌是否有效，如is_active
    # 首先验证令牌
    email, is_token_expired = verify_token(token)
    if is_token_expired: #email is None or 
        # 如果令牌无效或已过期，直接返回提示信息
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is expired",
            # headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 直接删除与当前访问令牌相关的记录
    token_record = db.query(AccTokenMapping).filter(AccTokenMapping.access_token == token).first()
    if token_record:
        db.delete(token_record)
        db.commit()
        return {"message": "You have been logged out."}
    else:
        # 如果找不到令牌记录，可能是因为它已被删除或从未存在
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token record not found",
        )


@router.get("/me", response_model=UserMe)
async def read_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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


@router.post("/refresh_token")
async def refresh_access_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    email,is_token_expired = verify_token(token)  # 验证acc是否有效
    token_data = db.query(AccTokenMapping).filter(AccTokenMapping.access_token == token).first()
    if not token_data :
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is invalid or expired")

    if not is_token_expired:
        return {
            "access_token": token,  # 直接返回现有的访问令牌
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES  # 可选：计算剩余有效时间
        }

    # 删除与当前访问令牌相关的记录
    delete_specific_token_record(db, token)

    new_refresh_token, new_exp_at = refresh_token_logic(db, token_data, email)

    # 生成新的访问令牌并存储新的令牌信息
    new_access_token = generate_and_store_tokens(db, email, new_refresh_token, new_exp_at)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES
    }


# address信息

# from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Address, User
# from utils import get_db, get_current_user
from typing import List, Optional

class AddressBase(BaseModel):
    address_1: str
    address_2: str
    address_3: Optional[str] = None
    city_state: str
    zip: str
    country: str

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass

class AddressResponse(AddressBase):
    id: int

# 新挂一个api
router_addresses = APIRouter()

@router_addresses.get("", response_model=List[AddressResponse])
async def read_addresses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses

@router_addresses.post("", response_model=AddressResponse, status_code=201)
async def add_address(address: AddressCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_address = Address(**address.dict(), user_id=current_user.id)
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


@router_addresses.get("/{address_id}", response_model=AddressResponse)
async def read_address_detail(address_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router_addresses.patch("/{address_id}", response_model=AddressResponse)
async def update_address(address_id: int, address: AddressUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not existing_address:
        raise HTTPException(status_code=404, detail="Address not found")
    for key, value in address.dict().items():
        setattr(existing_address, key, value)
    db.commit()
    return existing_address

@router_addresses.delete("/{address_id}", response_model=dict)
async def delete_address(address_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == current_user.id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}

router.include_router(router_addresses, prefix="/addresses", tags=["users"]) # 挂上去
