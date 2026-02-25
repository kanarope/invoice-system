from __future__ import annotations
from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id"), unique=True, nullable=False)
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    branch_name: Mapped[Optional[str]] = mapped_column(String(100))
    account_type: Mapped[Optional[str]] = mapped_column(String(20))
    account_number: Mapped[Optional[str]] = mapped_column(String(20))
    account_holder: Mapped[Optional[str]] = mapped_column(String(100))

    invoice = relationship("Invoice", back_populates="bank_account")
