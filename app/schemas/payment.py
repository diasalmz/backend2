from pydantic import BaseModel, Field, RootModel
from datetime import datetime
from typing import Dict, Any

class UserData(BaseModel):
    fio: str
    iin: str
    phone: str

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Сумма платежа")
    user_data: UserData = Field(..., description="Данные пользователя для покупки")

class Payment(BaseModel):
    id: int
    amount: float
    status: str
    created_at: datetime
    paid_at: datetime | None = None

    class Config:
        from_attributes = True

# Удалена схема CloudPaymentsCallback

# Webhook payload from FreedomPay can include various fields; accept as arbitrary dict
class FreedomPayWebhook(RootModel[Dict[str, Any]]):
    root: Dict[str, Any]