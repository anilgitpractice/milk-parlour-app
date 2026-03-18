from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

try:
    # Pydantic v2
    from pydantic import ConfigDict

    _ORM_CONFIG = ConfigDict(from_attributes=True)
except Exception:  # pragma: no cover
    # Pydantic v1 fallback
    _ORM_CONFIG = {"orm_mode": True}

from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


# -----------------------------
# SQLAlchemy ORM models
# -----------------------------


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("name", name="uq_products_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    milk_type: Mapped[str] = mapped_column(String, nullable=False)
    quantity_litres: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    subscription: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="Active")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    item: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="Pending")


# -----------------------------
# Pydantic schemas
# -----------------------------


class MilkType(str, Enum):
    COW = "cow"
    BUFFALO = "buffalo"
    MIXED = "mixed"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    full_name: Optional[str] = None

    model_config = _ORM_CONFIG


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    full_name: Optional[str] = None

    model_config = _ORM_CONFIG


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    model_config = _ORM_CONFIG


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None

    model_config = _ORM_CONFIG


class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    model_config = _ORM_CONFIG


class ProductUpdateStock(BaseModel):
    stock: int = Field(..., ge=0)

    model_config = _ORM_CONFIG


class SubscriptionCreateRequest(BaseModel):
    customer_id: int = Field(..., gt=0)
    milk_type: MilkType
    quantity_litres: float = Field(..., gt=0)
    start_date: date = Field(default_factory=date.today)

    model_config = _ORM_CONFIG


class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    milk_type: MilkType
    quantity_litres: float
    start_date: date
    status: SubscriptionStatus

    model_config = _ORM_CONFIG


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = _ORM_CONFIG

