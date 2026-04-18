import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Render fournit DATABASE_URL avec "postgres://" — SQLAlchemy exige "postgresql://"
    _db_url = os.getenv("DATABASE_URL", "sqlite:///joj_dakar.db")
    SQLALCHEMY_DATABASE_URI = _db_url.replace("postgres://", "postgresql://", 1)
