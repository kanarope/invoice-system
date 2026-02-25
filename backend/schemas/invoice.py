from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel


class InvoiceDetailOut(BaseModel):
    id: int
    description: str | None
    amount: Decimal | None
    tax: Decimal | None
    tax_rate: str | None

    class Config:
        from_attributes = True


class InvoiceDetailUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    tax: Decimal | None = None
    tax_rate: str | None = None


class InvoiceBankAccountOut(BaseModel):
    id: int
    bank_name: str | None
    branch_name: str | None
    account_type: str | None
    account_number: str | None
    account_holder: str | None

    class Config:
        from_attributes = True


class BankAccountUpdate(BaseModel):
    bank_name: str | None = None
    branch_name: str | None = None
    account_type: str | None = None
    account_number: str | None = None
    account_holder: str | None = None


class InvoiceUpdate(BaseModel):
    invoice_number: str | None = None
    vendor_id: int | None = None
    department_id: int | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    total_amount: Decimal | None = None
    tax_amount: Decimal | None = None
    tax_8_amount: Decimal | None = None
    tax_10_amount: Decimal | None = None
    subtotal_amount: Decimal | None = None
    invoice_registration_number: str | None = None
    description: str | None = None
    recipient_name: str | None = None
    bank_account: BankAccountUpdate | None = None
    details: list[InvoiceDetailUpdate] | None = None


class InvoiceOut(BaseModel):
    id: int
    invoice_number: str | None
    vendor_id: int | None
    department_id: int | None
    status: str
    invoice_date: date | None
    due_date: date | None
    total_amount: Decimal | None
    tax_amount: Decimal | None
    tax_8_amount: Decimal | None
    tax_10_amount: Decimal | None
    subtotal_amount: Decimal | None
    file_path: str | None
    file_hash_sha256: str | None
    original_filename: str | None
    source_type: str
    invoice_registration_number: str | None
    invoice_registration_status: str | None
    ai_raw_result: dict | None
    compliance_check_result: dict | None
    is_deleted: bool
    retention_until: date | None
    description: str | None
    recipient_name: str | None
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None
    details: list[InvoiceDetailOut] = []
    bank_account: InvoiceBankAccountOut | None = None
    vendor_name: str | None = None
    department_name: str | None = None

    class Config:
        from_attributes = True


class InvoiceListOut(BaseModel):
    items: list[InvoiceOut]
    total: int
    page: int
    per_page: int
