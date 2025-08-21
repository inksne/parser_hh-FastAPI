from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path

import os
import logging
from typing import Final


load_dotenv()


POSTGRES_USER: Final[str] = os.environ.get("POSTGRES_USER", "inksne")
POSTGRES_PASSWORD: Final[str] = os.environ.get("POSTGRES_PASSWORD", "inksne")
POSTGRES_DB: Final[str] = os.environ.get("POSTGRES_DB", "inksne")
POSTGRES_HOST: Final[str] = os.environ.get("POSTGRES_HOST", "postgres")

CLIENT_ID: Final[str] = os.environ.get("CLIENT_ID", "null")
CLIENT_SECRET: Final[str] = os.environ.get("CLIENT_SECRET", "null")

APP_NAME: Final[str] = os.environ.get("APP_NAME", "null")
APP_EMAIL: Final[str] = os.environ.get("APP_EMAIL", "null")

ACCESS_TOKEN: Final[str] = os.environ.get("ACCESS_TOKEN", "null")


class AuthJWT(BaseModel):
    private_key_path: Path = Path("certs") / "jwt-private.pem"
    public_key_path: Path = Path("certs") / "jwt-public.pem"
    algorithm: Final[str] = "RS256"
    access_token_expire_minutes: int = 5
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()


class DBSettings(BaseSettings):
    db_url: str = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}'

db_settings = DBSettings()


def configure_logging(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d] %(funcName)20s %(module)s:%(lineno)d %(levelname)-8s - %(message)s"
    )