from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.otp import SendSmsRequest, CheckSmsRequest
from app.services.otp import otp_service

router = APIRouter()

@router.post("/send-otp")
def send_otp(
    *,
    db: Session = Depends(deps.get_db),
    otp_in: SendSmsRequest,
):
    """
    Send OTP code to the user's phone.
    """
    otp = otp_service.create_otp(db=db, phone=otp_in.phone)
    if not otp:
        raise HTTPException(
            status_code=400,
            detail="Could not send OTP. Please try again.",
        )
    return {"message": "OTP sent successfully."}

from app.core.security import create_access_token

@router.post("/verify-otp")
def verify_otp(
    *,
    db: Session = Depends(deps.get_db),
    verify_in: CheckSmsRequest,
):
    """
    Verify OTP and login/register user.
    """
    user = otp_service.verify_otp(db=db, phone=verify_in.phone, code=verify_in.code)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP or phone number.",
        )
    access_token = create_access_token(
        subject=user.id,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }