from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

OPEN_STAGES = {"Prospecting", "Qualification", "Proposal", "Negotiation"}


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    industry: Mapped[str] = mapped_column(String)
    tier: Mapped[str] = mapped_column(String)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="account")
    deals: Mapped[list["Deal"]] = relationship(back_populates="account")


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))

    account: Mapped["Account"] = relationship(back_populates="contacts")


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    stage: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    probability: Mapped[float] = mapped_column(Float)
    close_date: Mapped[date] = mapped_column(Date)
    owner: Mapped[str] = mapped_column(String)

    account: Mapped["Account"] = relationship(back_populates="deals")
