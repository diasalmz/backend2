from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing_extensions import Annotated
from app.api.deps import get_db
from app.services.otp import otp_service
from app.schemas.otp import SendSmsRequest, SendSmsResponse, CheckSmsRequest, CheckSmsResponse

router = APIRouter()

@router.post("/send-sms", response_model=SendSmsResponse)
async def send_sms(
    request: SendSmsRequest,
    db: Session = Depends(get_db)
):
    """
    Отправляет SMS с OTP кодом для подтверждения покупки подписки.
    """
    # Валидация ИИН
    if not otp_service.validate_iin(request.iin):
        raise HTTPException(
            status_code=400,
            detail="Неверный формат ИИН. ИИН должен состоять из 12 цифр"
        )
    
    # Валидация ФИО
    if len(request.fio.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="ФИО должно содержать минимум 5 символов"
        )
    
    # Создаем OTP и отправляем SMS
    result = otp_service.create_otp(db, request.phone)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    return SendSmsResponse(
        success=True,
        message=result["message"],
        phone=result["phone"]
    )

@router.post("/check-sms", response_model=CheckSmsResponse)
async def check_sms(
    request: CheckSmsRequest,
    db: Session = Depends(get_db)
):
    """
    Проверяет OTP код из SMS.
    """
    result = otp_service.verify_otp(db, request.phone, request.code)
    
    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )
    
    return CheckSmsResponse(
        success=True,
        message=result["message"],
        verified=result["verified"]
    )

@router.post("/callback")
async def smsc_callback(
    id: Annotated[int, Form()],
    status: Annotated[int, Form()],
    phone: Annotated[str, Form()],
    sender_id: Annotated[str | None, Form()] = None,
    cost: Annotated[float | None, Form()] = None,
    err: Annotated[str | None, Form()] = None,
):
    """
    Принимает callback от SMSC.kz со статусом отправленного сообщения.
    """
    print("--- SMSC.kz Callback Received ---")
    print(f"Message ID: {id}")
    print(f"Phone: {phone}")
    print(f"Status: {status}")
    if err:
        print(f"Error: {err}")
    print("---------------------------------")
    
    # SMSC ожидает ответ "OK"
    return "OK"