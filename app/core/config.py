import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Auth Service"
    API_V1_STR: str = "/api/v1"

    # Database
    # Для локального запуска вам нужно будет создать файл .env и указать в нем DATABASE_URL
    # Пример: DATABASE_URL=postgresql://user:password@localhost/db
    DATABASE_URL: str

    # SMS Service (Mobizon)
    MOBIZON_API_KEY: str

    # FreedomPay credentials
    # Для локальной разработки можно эмулировать платежи,
    # тогда поля ниже не обязательны
    FREEDOMPAY_MERCHANT_ID: str = ""
    FREEDOMPAY_SECRET_KEY: str = ""
    FREEDOMPAY_EMULATE: bool = True


    # JWT
    # Сгенерируйте секретный ключ, например, с помощью `openssl rand -hex 32`
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней

    # Pydantic v2 configuration: read from .env, keep case sensitivity,
    # and IGNORE extra env keys so unknown variables don't crash the app
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()