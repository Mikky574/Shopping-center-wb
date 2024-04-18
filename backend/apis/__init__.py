# 接口引入
from fastapi import APIRouter
from .cart import router as cart_router
from .users import router as users_router
# from .address import router as addr_router


router = APIRouter()
router.include_router(cart_router, prefix="/cart", tags=["cart"])
router.include_router(users_router, prefix="/users", tags=["users"])
# router.include_router(addr_router, prefix="/addresses", tags=["addresses"])
