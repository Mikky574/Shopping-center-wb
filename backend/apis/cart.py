from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils import get_db,get_current_user
from database import User, Cart, Product
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class CartItem(BaseModel):
    product_id: int
    amount: int

class CartUpdateItem(BaseModel):
    amount: int

@router.get("/", response_model=List[CartItem])
async def view_cart_items(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # if not current_user:
    #     raise HTTPException(status_code=401, detail="Token is invalid")
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    return [{"product_id": item.product_id, "amount": item.quantity} for item in cart_items]

@router.get("/{product_id}", response_model=CartItem)
async def view_cart_item_details(product_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    return {"product_id": cart_item.product_id, "amount": cart_item.quantity}

@router.patch("/{product_id}", response_model=None)
async def update_cart_item(product_id: int, item_update: CartUpdateItem, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(Cart).filter(Cart.user_id == current_user.id, Cart.product_id == product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    if item_update.amount == 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = item_update.amount
    db.commit()
    return {"message": "Cart updated successfully"}
