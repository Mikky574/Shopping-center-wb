# 接口引入
from fastapi import APIRouter
from .cart import router as cart_router
from .users import router as users_router

router = APIRouter()
router.include_router(cart_router, prefix="/cart", tags=["cart"])
router.include_router(users_router, prefix="/users", tags=["users"])
