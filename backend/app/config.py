from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
ROOT_ENV = ROOT_DIR / ".env"

if ROOT_ENV.exists():
    load_dotenv(dotenv_path=ROOT_ENV, override=False)

if BACKEND_ENV.exists():
    load_dotenv(dotenv_path=BACKEND_ENV, override=True)


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    DB_NAME: str = "hackathon"
    GEMINI_API_KEY: str = ""
    GOOGLE_MAP_API_KEY: str = ""

    API_TITLE: str = "CivicLens AI API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "AI-powered Civic Complaint Management System"

    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8501",
        "*",
    ]
    EXTRA_ALLOWED_ORIGINS: str = ""

    @property
    def google_maps_key(self) -> str:
        return self.GOOGLE_MAP_API_KEY.strip()

    @property
    def cors_origins(self) -> list:
        origins = list(self.ALLOWED_ORIGINS)
        if self.EXTRA_ALLOWED_ORIGINS:
            origins.extend(
                o.strip() for o in self.EXTRA_ALLOWED_ORIGINS.split(",") if o.strip()
            )
        return origins

    class Config:
        env_file = str(BACKEND_ENV if BACKEND_ENV.exists() else ROOT_ENV)
        extra = "ignore"


settings = Settings()

# Support alternate env var name
import os
if not settings.GOOGLE_MAP_API_KEY and os.getenv("GOOGLE_MAPS_API_KEY"):
    settings.GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
