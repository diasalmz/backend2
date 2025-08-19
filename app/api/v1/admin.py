from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.user import User
from app.models.otp import Otp
from app.main import templates
import os

router = APIRouter()

ADMIN_PASSWORD = os.environ.get("KARAK_ADMIN_PASS", "admin123")

# Простая авторизация через сессию (cookie)
def check_admin(request: Request):
    if request.cookies.get("admin_auth") == "ok":
        return True
    raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db), auth: bool = Depends(check_admin)):
    users = db.query(User).all()
    otps = db.query(Otp).order_by(Otp.created_at.desc()).limit(100).all()
    return templates.TemplateResponse("admin_panel.html", {"request": request, "users": users, "otps": otps})

@router.get("/login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": None})

@router.post("/login", response_class=HTMLResponse)
def admin_login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/api/v1/admin/", status_code=302)
        response.set_cookie("admin_auth", "ok", httponly=True, max_age=60*60*8)
        return response
    return templates.TemplateResponse("admin_login.html", {"request": request, "error": "Неверный пароль"})

@router.get("/logout")
def admin_logout(auth: bool = Depends(check_admin)):
    response = RedirectResponse(url="/api/v1/admin/login", status_code=302)
    response.delete_cookie("admin_auth")
    return response 