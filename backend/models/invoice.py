from __future__ import annotations
from typing import Optional

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    String, Integer, ForeignKey, DateTime, Date, Numeric,
    Boolean, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    vendor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vendors.id"))
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"))
    assigned_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    approved_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))

    status: Mapped[str] = mapped_column(String(30), default="uploaded", index=True)

    invoice_date: Mapped[Optional[date]] = mapped_column(Date)
    due_date: Mapped[Optional[date]] = mapped_column(Date)

    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    tax_8_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    tax_10_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))
    subtotal_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 0))

    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    file_hash_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    original_filename: Mapped[Optional[str]] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(20), default="upload")

    invoice_registration_number: Mapped[Optional[str]] = mapped_column(String(14))
    invoice_registration_status: Mapped[Optional[str]] = mapped_column(String(20))

    ai_raw_result: Mapped[Optional[dict]] = mapped_column(JSONB)
    compliance_check_result: Mapped[Optional[dict]] = mapped_column(JSONB)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    retention_until: Mapped[Optional[date]] = mapped_column(Date)
    description: Mapped[Optional[str]] = mapped_column(Text)
    recipient_name: Mapped[Optional[str]] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    vendor = relationship("Vendor", back_populates="invoices")
    department = relationship("Department", back_populates="invoices")
    details = relationship("InvoiceDetail", back_populates="invoice", cascade="all, delete-orphan")
    bank_account = relationship("BankAccount", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
