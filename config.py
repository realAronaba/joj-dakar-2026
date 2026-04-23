import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY               = os.getenv("SECRET_KEY", "dev-key")
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.getenv("DATABASE_URL", "sqlite:///joj_dakar.db")
    SQLALCHEMY_DATABASE_URI  = _db_url.replace("postgres://", "postgresql://", 1)

    # Web Push (VAPID)
    VAPID_PUBLIC_KEY  = os.getenv("VAPID_PUBLIC_KEY", "")
    VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
    VAPID_CONTACT     = os.getenv("VAPID_CONTACT", "contact@joj-dakar.sn")

    # Email (SMTP)
    MAIL_SERVER   = os.getenv("MAIL_SERVER",   "smtp.gmail.com")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_SENDER   = os.getenv("MAIL_SENDER",   "JOJ Dakar 2026 <infosdakar2026@gmail.com>")
