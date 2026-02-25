from __future__ import annotations
from typing import Optional

from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class InvoiceDetail(Base):
    __tablename__ = "invoice_details"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("invoices.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    tax: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    tax_rate: Mapped[Optional[str]] = mapped_column(String(10))

    invoice = relationship("Invoice", back_populates="details")
