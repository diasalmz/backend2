from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SendSmsRequest(BaseModel):
    phone: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    fio: str = Field(..., description="ФИО пользователя")
    iin: str = Field(..., description="ИИН пользователя (12 цифр)")

class SendSmsResponse(BaseModel):
    success: bool
    message: str
    phone: str

class CheckSmsRequest(BaseModel):
    phone: str = Field(..., description="Номер телефона")
    code: str = Field(..., description="Код из SMS")

class CheckSmsResponse(BaseModel):
    success: bool
    message: str
    verified: bool = False

class OtpCreate(BaseModel):
    phone: str
    code: str
    expires_at: datetime

class OtpResponse(BaseModel):
    id: int
    phone: str
    is_used: bool
    attempts: int
    created_at: datetime
    expires_at: datetime