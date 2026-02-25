from __future__ import annotations
from typing import Optional

from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    invoice_registration_number: Mapped[Optional[str]] = mapped_column(String(14))
    registration_status: Mapped[Optional[str]] = mapped_column(String(20))
    registration_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    default_department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    default_department = relationship("Department", back_populates="vendors")
    invoices = relationship("Invoice", back_populates="vendor")
