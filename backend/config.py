import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY                     = os.environ.get("SECRET_KEY", "ie-manager-secret-2024")
    JWT_SECRET_KEY                 = os.environ.get("JWT_SECRET_KEY", "ie-jwt-secret-2024")
    BASE_DIR                       = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI        = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "ie_manager.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES       = timedelta(days=7)
    DEBUG                          = os.environ.get("DEBUG", "True") == "True"
