from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice
from models.user import User
from schemas.invoice import InvoiceOut
from services.auth_service import require_role
from services.gmail_service import fetch_invoice_emails
from services.file_service import save_upload, calculate_retention_date
from services.ocr_service import extract_invoice_data
from services.compliance_service import check_invoice_compliance
from services.audit_service import log_action
from config import settings
import os

router = APIRouter(prefix="/api/gmail", tags=["gmail"])


@router.post("/fetch")
def fetch_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "accountant")),
):
    try:
        emails = fetch_invoice_emails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail取得エラー: {str(e)}")

    created = []
    for email_data in emails:
        for att in email_data["attachments"]:
            rel_path, sha256 = save_upload(att["data"], att["filename"])

            inv = Invoice(
                file_path=rel_path,
                file_hash_sha256=sha256,
                original_filename=att["filename"],
                source_type="gmail",
                status="uploaded",
                description=f"From: {email_data['sender']} Subject: {email_data['subject']}",
                retention_until=calculate_retention_date(None),
            )
            db.add(inv)
            db.flush()

            log_action(
                db,
                user_id=current_user.id,
                entity_type="invoice",
                entity_id=inv.id,
                action="create",
                new_values={"source": "gmail", "message_id": email_data["message_id"]},
            )

            abs_path = os.path.join(settings.UPLOAD_DIR, rel_path)
            try:
                ai_result = extract_invoice_data(abs_path)
                inv.ai_raw_result = ai_result
                inv.status = "extracted"

                compliance = check_invoice_compliance(ai_result)
                inv.compliance_check_result = compliance.model_dump()
                inv.status = "compliance_checked"
            except Exception:
                inv.status = "extraction_failed"

            db.flush()
            created.append(inv.id)

    db.commit()
    return {"ok": True, "created_count": len(created), "invoice_ids": created}
