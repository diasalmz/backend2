import httpx
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.payment import Payment
from app.models.user import User

class FreedomPayService:
    def __init__(self):
        from app.core.config import settings
        self.merchant_id = settings.FREEDOMPAY_MERCHANT_ID
        self.secret_key = settings.FREEDOMPAY_SECRET_KEY
        self.emulate = getattr(settings, "FREEDOMPAY_EMULATE", False)
        self.base_url = "https://api.freedompay.kz"

    def _generate_signature(self, params: dict, script_name: str) -> str:
        import hashlib
        import hmac

        # In emulation, skip real signature generation
        if self.emulate or not self.secret_key:
            return "emulated-signature"

        sorted_params = sorted(params.items())
        param_str = ";".join([str(v) for k, v in sorted_params])
        
        sig_str = f"{script_name};{param_str}"

        return hmac.new(self.secret_key.encode(), sig_str.encode(), hashlib.sha512).hexdigest()

    async def create_invoice(self, db: Session, amount: float, user_data: dict, user: User) -> Payment:
        db_payment = Payment(
            amount=amount,
            user_id=user.id,
            status="pending",
            fio=user_data.get('fio'),
            iin=user_data.get('iin'),
            phone=user_data.get('phone')
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)

        payload = {
            "pg_merchant_id": self.merchant_id,
            "pg_order_id": db_payment.id,
            "pg_amount": amount,
            "pg_description": f"Оплата заказа №{db_payment.id}",
            "pg_salt": "some_random_string",  # Should be random
            "pg_currency": "KZT",
            "pg_user_phone": user.phone_number,
            "pg_user_email": user.email,
        }
        payload["pg_sig"] = self._generate_signature(payload, "init_payment.php")

        # Emulated flow: mark as success and return immediately
        if self.emulate:
            db_payment.external_id = f"emul-{db_payment.id}"
            db_payment.status = "success"
            db_payment.meta = {"redirect_url": f"http://localhost/mock-payment?order={db_payment.id}"}
            db.commit()
            db.refresh(db_payment)
            return db_payment

        # Real flow: ensure credentials present
        if not self.merchant_id or not self.secret_key:
            # Credentials missing in non-emulation mode
            return db_payment

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/init_payment.php", json=payload)
            data = response.json()
            if data.get("pg_status") == "ok":
                db_payment.external_id = data.get("pg_payment_id")
                db_payment.meta = {"redirect_url": data.get("pg_redirect_url")}
                db.commit()
                db.refresh(db_payment)
        return db_payment

    def process_webhook(self, db: Session, payload: dict) -> Payment:
        order_id = payload.get("pg_order_id")
        status = payload.get("pg_result")
        
        payment = db.query(Payment).filter(Payment.id == int(order_id)).first()
        if payment:
            payment.status = "success" if status == "1" else "failed"
            db.commit()
            db.refresh(payment)
        return payment

freedompay_service = FreedomPayService()