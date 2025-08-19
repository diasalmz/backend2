from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.models.user import User as UserModel
from app.api import deps
from app.services.payment import freedompay_service
from app.schemas.payment import Payment, PaymentCreate, FreedomPayWebhook

router = APIRouter()

@router.post("/freedompay/", response_model=Payment)
async def create_freedompay_payment(
    *,
    db: Session = Depends(deps.get_db),
    payment_in: PaymentCreate,
    current_user: UserModel = Depends(deps.get_current_user),
):
    """
    Create new payment via FreedomPay.
    """
    payment = await freedompay_service.create_invoice(
        db,
        amount=payment_in.amount,
        user_data=payment_in.user_data.dict(),
        user=current_user
    )
    return payment

@router.post("/freedompay/webhook/")
async def freedompay_webhook(
    *,
    db: Session = Depends(deps.get_db),
    webhook_data: FreedomPayWebhook,
):
    """
    Process FreedomPay webhook.
    """
    payment = freedompay_service.process_webhook(db, webhook_data.root)
    return {"status": "ok"}