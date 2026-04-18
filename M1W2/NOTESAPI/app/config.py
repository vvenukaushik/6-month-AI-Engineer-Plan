import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
APP_TITLE = "Personal Notes API"
APP_VERSION = "1.0.0"