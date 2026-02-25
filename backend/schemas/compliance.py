from __future__ import annotations
from typing import Optional

from pydantic import BaseModel


class NTAVerificationResult(BaseModel):
    registration_number: str
    is_valid: bool
    company_name: Optional[str] = None
    address: Optional[str] = None
    registration_date: Optional[str] = None
    update_date: Optional[str] = None
    raw_response: Optional[dict] = None


class ComplianceCheckResult(BaseModel):
    has_registration_number: bool = False
    has_invoice_date: bool = False
    has_description: bool = False
    has_tax_breakdown: bool = False
    has_tax_amount: bool = False
    has_recipient_name: bool = False
    registration_valid: Optional[bool] = None
    missing_items: list[str] = []
    passed: bool = False
