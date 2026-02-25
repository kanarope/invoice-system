import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://invoice:invoice@localhost:5432/invoice_db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    GMAIL_CREDENTIALS_FILE: str = "credentials.json"
    GMAIL_TOKEN_FILE: str = "token.json"

    MF_CLIENT_ID: str = ""
    MF_CLIENT_SECRET: str = ""
    MF_REDIRECT_URI: str = "http://localhost:8000/api/transfers/mf/callback"

    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "uploads")

    NTA_API_BASE_URL: str = "https://web-api.invoice-kohyo.nta.go.jp/1"

    RETENTION_YEARS: int = 7

    class Config:
        env_file = ".env"


settings = Settings()
