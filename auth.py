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

@router.post("/users/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"status": "success", "message": "User logged in successfully."}

