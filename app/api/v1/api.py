from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, payments, sms, admin

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])