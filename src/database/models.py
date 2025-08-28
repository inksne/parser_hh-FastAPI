from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str]
    password: Mapped[str] = mapped_column(String(1024), nullable=False)

    vacancies: Mapped[list["Vacancy"]] = relationship("Vacancy", back_populates="user", cascade="all, delete-orphan")


class Vacancy(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    experience: Mapped[str] = mapped_column(nullable=False)
    employment_form: Mapped[str] = mapped_column(nullable=False)
    work_format: Mapped[str] = mapped_column(nullable=False)
    schedule: Mapped[str] = mapped_column(nullable=False)
    salary: Mapped[int] = mapped_column(nullable=False)
    education: Mapped[str] = mapped_column(nullable=False)
    hh_link: Mapped[str] = mapped_column(nullable=False)
    premium: Mapped[bool] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped[User] = relationship("User", back_populates="vacancies")