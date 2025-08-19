import logging
import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import Otp
from app.models.user import User
from app.services.sms import sms_service
from app.schemas.otp import OtpCreate
import re

logger = logging.getLogger(__name__)

class OtpService:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 5
        self.max_attempts = 3

    def validate_phone(self, phone: str) -> bool:
        """Валидация номера телефона"""
        # Проверяем формат +7XXXXXXXXXX
        pattern = r'^\+7[0-9]{10}$'
        return bool(re.match(pattern, phone))

    def validate_iin(self, iin: str) -> bool:
        """Валидация ИИН"""
        # Проверяем что ИИН состоит из 12 цифр
        return bool(re.match(r'^[0-9]{12}$', iin))

    def create_otp(self, db: Session, phone: str) -> dict:
        """Создает новый OTP код"""
        # Проверяем валидность телефона
        if not self.validate_phone(phone):
            logger.warning(f"Попытка создать OTP с некорректным номером: {phone}")
            return {
                "success": False,
                "message": "Неверный формат номера телефона. Используйте формат +7XXXXXXXXXX"
            }

        # Генерируем код
        code = sms_service.generate_otp_code(self.otp_length)
        expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)

        # Создаем запись в БД
        otp = Otp(
            phone=phone,
            code=code,
            expires_at=expires_at,
            is_used=False,
            attempts=0
        )
        
        try:
            db.add(otp)
            db.commit()
            db.refresh(otp)
            
            # Отправляем SMS
            sms_result = sms_service.send_otp_sms(phone, code)
            
            if sms_result["success"]:
                return {
                    "success": True,
                    "message": "Код подтверждения отправлен на ваш номер",
                    "phone": phone
                }
            else:
                # Если SMS не отправилось, удаляем запись из БД
                db.delete(otp)
                db.commit()
                logger.error(f"Ошибка отправки SMS: {sms_result['message']}")
                return {
                    "success": False,
                    "message": sms_result["message"]
                }
                
        except Exception as e:
            db.rollback()
            logger.exception(f"Ошибка создания OTP для {phone}: {e}")
            return {
                "success": False,
                "message": f"Ошибка создания OTP: {str(e)}"
            }

    def verify_otp(self, db: Session, phone: str, code: str) -> dict:
        """Проверяет OTP код"""
        if not self.validate_phone(phone):
            logger.warning(f"Попытка проверки OTP с некорректным номером: {phone}")
            return {
                "success": False,
                "message": "Неверный формат номера телефона"
            }

        # Ищем активный OTP для данного телефона
        otp = db.query(Otp).filter(
            Otp.phone == phone,
            Otp.is_used == False,
            Otp.expires_at > datetime.utcnow()
        ).order_by(Otp.created_at.desc()).first()

        if not otp:
            logger.info(f"OTP не найден или истек для номера: {phone}")
            return {
                "success": False,
                "message": "Код не найден или истек. Запросите новый код",
                "verified": False
            }

        # Проверяем количество попыток
        if otp.attempts >= self.max_attempts:
            otp.is_used = True
            db.commit()
            logger.warning(f"Превышено количество попыток для номера: {phone}")
            return {
                "success": False,
                "message": "Превышено количество попыток. Запросите новый код",
                "verified": False
            }

        # Увеличиваем счетчик попыток
        otp.attempts += 1

        # Проверяем код
        if otp.code == code:
            otp.is_used = True
            db.commit()
            logger.info(f"OTP успешно подтвержден для номера: {phone}")
            return {
                "success": True,
                "message": "Код подтвержден успешно",
                "verified": True
            }
        else:
            db.commit()
            logger.warning(f"Введён неверный код OTP для номера: {phone}")
            return {
                "success": False,
                "message": "Неверный код. Попробуйте еще раз",
                "verified": False
            }

    def cleanup_expired_otp(self, db: Session):
        """Удаляет истекшие OTP коды"""
        expired_otps = db.query(Otp).filter(
            Otp.expires_at < datetime.utcnow()
        ).all()
        
        for otp in expired_otps:
            db.delete(otp)
        
        db.commit()
        logger.info(f"Удалено {len(expired_otps)} истекших OTP-кодов")

otp_service = OtpService()