from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str]
    password: Mapped[str] = mapped_column(String(1024), nullable=False)