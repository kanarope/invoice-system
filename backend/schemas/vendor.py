from datetime import datetime
from pydantic import BaseModel


class VendorCreate(BaseModel):
    name: str
    invoice_registration_number: str | None = None
    default_department_id: int | None = None


class VendorUpdate(BaseModel):
    name: str | None = None
    invoice_registration_number: str | None = None
    default_department_id: int | None = None


class VendorOut(BaseModel):
    id: int
    name: str
    invoice_registration_number: str | None
    registration_status: str | None
    registration_checked_at: datetime | None
    default_department_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
