import httpx
import random
import string
from datetime import datetime, timedelta
from app.core.config import settings

class SmsService:
    def __init__(self):
        self.api_key = settings.MOBIZON_API_KEY
        self.base_url = "https://api.mobizon.kz/service/message/sendsmsmessage"

    def generate_otp_code(self, length: int = 6) -> str:
        """Генерирует OTP код заданной длины"""
        return ''.join(random.choices(string.digits, k=length))

    def send_otp_sms(self, phone: str, code: str) -> dict:
        """Отправляет SMS с OTP кодом"""
        message = f"Ваш код подтверждения: {code}. Код действителен 5 минут."
        
        params = {
            "apiKey": self.api_key,
            "recipient": phone.lstrip('+'),
            "text": message,
        }
        
        with httpx.Client() as client:
            try:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                response_data = response.json()
                
                if response_data.get("code") == 0:
                    return {
                        "success": True,
                        "message": "SMS отправлено успешно",
                        "data": response_data
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Ошибка отправки SMS: {response_data.get('message', 'Неизвестная ошибка')}",
                        "data": response_data
                    }
            except (httpx.HTTPStatusError, Exception) as e:
                return {
                    "success": False,
                    "message": f"Ошибка отправки SMS: {str(e)}",
                    "data": None
                }

    def send_sms(self, phone: str, message: str):
        """Общий метод отправки SMS (для обратной совместимости)"""
        params = {
            "apiKey": self.api_key,
            "recipient": phone.lstrip('+'),
            "text": message,
        }
        
        with httpx.Client() as client:
            try:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                response_data = response.json()
                
                if response_data.get("code") == 0:
                    return response_data
                else:
                    return None
            except (httpx.HTTPStatusError, Exception) as e:
                return None

sms_service = SmsService()