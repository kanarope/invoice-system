from __future__ import annotations
from typing import Optional

from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel


class InvoiceDetailOut(BaseModel):
    id: int
    description: Optional[str]
    amount: Optional[Decimal]
    tax: Optional[Decimal]
    tax_rate: Optional[str]

    class Config:
        from_attributes = True


class InvoiceDetailUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    tax_rate: Optional[str] = None


class InvoiceBankAccountOut(BaseModel):
    id: int
    bank_name: Optional[str]
    branch_name: Optional[str]
    account_type: Optional[str]
    account_number: Optional[str]
    account_holder: Optional[str]

    class Config:
        from_attributes = True


class BankAccountUpdate(BaseModel):
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_type: Optional[str] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None


class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    vendor_id: Optional[int] = None
    department_id: Optional[int] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    tax_8_amount: Optional[Decimal] = None
    tax_10_amount: Optional[Decimal] = None
    subtotal_amount: Optional[Decimal] = None
    invoice_registration_number: Optional[str] = None
    description: Optional[str] = None
    recipient_name: Optional[str] = None
    bank_account: Optional[BankAccountUpdate] = None
    details: Optional[list[InvoiceDetailUpdate]] = None


class InvoiceOut(BaseModel):
    id: int
    invoice_number: Optional[str]
    vendor_id: Optional[int]
    department_id: Optional[int]
    status: str
    invoice_date: Optional[date]
    due_date: Optional[date]
    total_amount: Optional[Decimal]
    tax_amount: Optional[Decimal]
    tax_8_amount: Optional[Decimal]
    tax_10_amount: Optional[Decimal]
    subtotal_amount: Optional[Decimal]
    file_path: Optional[str]
    file_hash_sha256: Optional[str]
    original_filename: Optional[str]
    source_type: str
    invoice_registration_number: Optional[str]
    invoice_registration_status: Optional[str]
    ai_raw_result: Optional[dict]
    compliance_check_result: Optional[dict]
    is_deleted: bool
    retention_until: Optional[date]
    description: Optional[str]
    recipient_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    details: list[InvoiceDetailOut] = []
    bank_account: Optional[InvoiceBankAccountOut] = None
    vendor_name: Optional[str] = None
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceListOut(BaseModel):
    items: list[InvoiceOut]
    total: int
    page: int
    per_page: int
