from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.payment import Payment
from app.schemas.payment import Payment as PaymentSchema

router = APIRouter()

@router.get("/payments", response_model=List[PaymentSchema])
def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db)
):
    """
    Получить все платежи с данными пользователей для админ-панели
    """
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments

@router.get("/payments/{payment_id}", response_model=PaymentSchema)
def get_payment_by_id(
    payment_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Получить конкретный платеж по ID
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.get("/payments/search/{phone}")
def search_payments_by_phone(
    phone: str,
    db: Session = Depends(deps.get_db)
):
    """
    Найти платежи по номеру телефона
    """
    payments = db.query(Payment).filter(Payment.phone.contains(phone)).all()
    return payments
