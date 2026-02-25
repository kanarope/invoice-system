from __future__ import annotations
from typing import Optional

from datetime import datetime
from pydantic import BaseModel


class VendorCreate(BaseModel):
    name: str
    invoice_registration_number: Optional[str] = None
    default_department_id: Optional[int] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    invoice_registration_number: Optional[str] = None
    default_department_id: Optional[int] = None


class VendorOut(BaseModel):
    id: int
    name: str
    invoice_registration_number: Optional[str]
    registration_status: Optional[str]
    registration_checked_at: Optional[datetime]
    default_department_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
