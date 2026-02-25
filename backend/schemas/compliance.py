from pydantic import BaseModel


class NTAVerificationResult(BaseModel):
    registration_number: str
    is_valid: bool
    company_name: str | None = None
    address: str | None = None
    registration_date: str | None = None
    update_date: str | None = None
    raw_response: dict | None = None


class ComplianceCheckResult(BaseModel):
    has_registration_number: bool = False
    has_invoice_date: bool = False
    has_description: bool = False
    has_tax_breakdown: bool = False
    has_tax_amount: bool = False
    has_recipient_name: bool = False
    registration_valid: bool | None = None
    missing_items: list[str] = []
    passed: bool = False
