import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    AUTH_ENABLED = os.environ.get("AUTH_ENABLED", "false").lower() == "true"
    ADMIN_ENDPOINTS_ENABLED = (
        os.environ.get("ADMIN_ENDPOINTS_ENABLED", "false").lower() == "true"
    )
    JWT_EXPIRES_HOURS = int(os.environ.get("JWT_EXPIRES_HOURS", "24"))

    ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ] or ["*"]

    AMBIENTE = os.environ.get("AMBIENTE", "desenvolvimento")
    VERSAO = "1.0.0"
