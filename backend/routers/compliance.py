from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice
from models.vendor import Vendor
from models.user import User
from schemas.compliance import NTAVerificationResult, ComplianceCheckResult
from services.auth_service import get_current_user
from services.nta_api_service import verify_registration_number
from services.compliance_service import check_invoice_compliance
from services.audit_service import log_action

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/verify/{registration_number}", response_model=NTAVerificationResult)
def verify_number(registration_number: str, _=Depends(get_current_user)):
    return verify_registration_number(registration_number)


@router.post("/check/{invoice_id}", response_model=ComplianceCheckResult)
def check_compliance(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    result = check_invoice_compliance(inv.ai_raw_result)
    inv.compliance_check_result = result.model_dump()
    inv.invoice_registration_status = (
        "valid" if result.registration_valid
        else "invalid" if result.registration_valid is False
        else "unchecked"
    )

    if inv.vendor_id and inv.invoice_registration_number:
        vendor = db.query(Vendor).filter(Vendor.id == inv.vendor_id).first()
        if vendor:
            vendor.invoice_registration_number = inv.invoice_registration_number
            vendor.registration_status = inv.invoice_registration_status
            from datetime import datetime, timezone
            vendor.registration_checked_at = datetime.now(timezone.utc)

    db.commit()
    return result


@router.get("/dashboard")
def compliance_dashboard(db: Session = Depends(get_db), _=Depends(get_current_user)):
    total = db.query(Invoice).filter(Invoice.is_deleted.is_(False)).count()
    valid = db.query(Invoice).filter(Invoice.invoice_registration_status == "valid", Invoice.is_deleted.is_(False)).count()
    invalid = db.query(Invoice).filter(Invoice.invoice_registration_status == "invalid", Invoice.is_deleted.is_(False)).count()
    unchecked = db.query(Invoice).filter(
        Invoice.invoice_registration_status.in_(["unchecked", None]),
        Invoice.is_deleted.is_(False),
    ).count()

    return {
        "total_invoices": total,
        "valid_registration": valid,
        "invalid_registration": invalid,
        "unchecked_registration": unchecked,
    }
