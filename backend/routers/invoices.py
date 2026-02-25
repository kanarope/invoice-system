import os
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database import get_db
from models.invoice import Invoice
from models.invoice_detail import InvoiceDetail
from models.bank_account import BankAccount
from models.vendor import Vendor
from schemas.invoice import InvoiceOut, InvoiceUpdate, InvoiceListOut
from services.auth_service import get_current_user, require_role
from services.file_service import save_upload, compute_sha256, calculate_retention_date, check_image_dpi, verify_file_hash
from services.ocr_service import extract_invoice_data
from services.compliance_service import check_invoice_compliance
from services.classifier import classify_department, update_vendor_department
from services.audit_service import log_action
from config import settings
from models.user import User

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


def _to_out(inv: Invoice) -> InvoiceOut:
    d = InvoiceOut.model_validate(inv)
    d.vendor_name = inv.vendor.name if inv.vendor else None
    d.department_name = inv.department.name if inv.department else None
    return d


@router.post("/upload", response_model=list[InvoiceOut])
async def upload_invoices(
    request: Request,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = []
    for f in files:
        content = await f.read()
        rel_path, sha256 = save_upload(content, f.filename)

        inv = Invoice(
            file_path=rel_path,
            file_hash_sha256=sha256,
            original_filename=f.filename,
            source_type="upload",
            status="uploaded",
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
            new_values={"filename": f.filename, "sha256": sha256},
            ip_address=request.client.host if request.client else None,
        )

        abs_path = os.path.join(settings.UPLOAD_DIR, rel_path)
        try:
            ai_result = extract_invoice_data(abs_path)
            inv.ai_raw_result = ai_result
            inv.status = "extracted"

            inv.invoice_number = ai_result.get("invoice_number")
            inv.invoice_date = _parse_date(ai_result.get("invoice_date"))
            inv.due_date = _parse_date(ai_result.get("due_date"))
            inv.total_amount = _to_decimal(ai_result.get("total_amount"))
            inv.subtotal_amount = _to_decimal(ai_result.get("subtotal_amount"))
            inv.tax_amount = _to_decimal(ai_result.get("tax_amount"))
            inv.tax_8_amount = _to_decimal(ai_result.get("tax_8_amount"))
            inv.tax_10_amount = _to_decimal(ai_result.get("tax_10_amount"))
            inv.invoice_registration_number = ai_result.get("invoice_registration_number")
            inv.recipient_name = ai_result.get("recipient_name")
            inv.retention_until = calculate_retention_date(inv.invoice_date)

            vendor_name = ai_result.get("vendor_name")
            if vendor_name:
                vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()
                if not vendor:
                    vendor = Vendor(name=vendor_name, invoice_registration_number=ai_result.get("invoice_registration_number"))
                    db.add(vendor)
                    db.flush()
                inv.vendor_id = vendor.id

            dept_id = classify_department(db, vendor_name)
            if dept_id:
                inv.department_id = dept_id

            bank_data = ai_result.get("bank_account", {})
            if bank_data and any(bank_data.values()):
                ba = BankAccount(
                    invoice_id=inv.id,
                    bank_name=bank_data.get("bank_name"),
                    branch_name=bank_data.get("branch_name"),
                    account_type=bank_data.get("account_type"),
                    account_number=bank_data.get("account_number"),
                    account_holder=bank_data.get("account_holder"),
                )
                db.add(ba)

            items = ai_result.get("items", [])
            for item in items:
                detail = InvoiceDetail(
                    invoice_id=inv.id,
                    description=item.get("description"),
                    amount=_to_decimal(item.get("amount")),
                    tax=_to_decimal(item.get("tax")),
                    tax_rate=item.get("tax_rate"),
                )
                db.add(detail)

            compliance = check_invoice_compliance(ai_result)
            inv.compliance_check_result = compliance.model_dump()
            inv.invoice_registration_status = (
                "valid" if compliance.registration_valid
                else "invalid" if compliance.registration_valid is False
                else "unchecked"
            )
            inv.status = "compliance_checked"

        except Exception as e:
            inv.ai_raw_result = {"error": str(e)}
            inv.status = "extraction_failed"

        db.flush()
        results.append(inv)

    db.commit()
    for inv in results:
        db.refresh(inv)
    return [_to_out(inv) for inv in results]


@router.get("", response_model=InvoiceListOut)
def list_invoices(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = None,
    department_id: int | None = None,
    vendor_name: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    amount_min: int | None = None,
    amount_max: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Invoice).filter(Invoice.is_deleted.is_(False))

    if current_user.role == "department" and current_user.department_id:
        q = q.filter(Invoice.department_id == current_user.department_id)

    if status:
        q = q.filter(Invoice.status == status)
    if department_id:
        q = q.filter(Invoice.department_id == department_id)
    if vendor_name:
        q = q.join(Vendor).filter(Vendor.name.ilike(f"%{vendor_name}%"))
    if date_from:
        q = q.filter(Invoice.invoice_date >= date_from)
    if date_to:
        q = q.filter(Invoice.invoice_date <= date_to)
    if amount_min is not None:
        q = q.filter(Invoice.total_amount >= amount_min)
    if amount_max is not None:
        q = q.filter(Invoice.total_amount <= amount_max)

    total = q.count()
    items = q.order_by(Invoice.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return InvoiceListOut(
        items=[_to_out(inv) for inv in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.is_deleted.is_(False)).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")
    return _to_out(inv)


@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int,
    body: InvoiceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.is_deleted.is_(False)).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    old_values = {}
    new_values = {}
    update_data = body.model_dump(exclude_unset=True, exclude={"bank_account", "details"})

    for field, value in update_data.items():
        old_val = getattr(inv, field)
        if old_val != value:
            old_values[field] = str(old_val) if old_val is not None else None
            new_values[field] = str(value) if value is not None else None
            setattr(inv, field, value)

    if body.bank_account:
        if inv.bank_account:
            for field, value in body.bank_account.model_dump(exclude_unset=True).items():
                setattr(inv.bank_account, field, value)
        else:
            ba = BankAccount(invoice_id=inv.id, **body.bank_account.model_dump(exclude_unset=True))
            db.add(ba)

    if body.details is not None:
        for detail in inv.details:
            db.delete(detail)
        db.flush()
        for item in body.details:
            detail = InvoiceDetail(invoice_id=inv.id, **item.model_dump(exclude_unset=True))
            db.add(detail)

    if body.department_id and inv.vendor_id:
        update_vendor_department(db, inv.vendor_id, body.department_id)

    if inv.status in ("extracted", "compliance_checked"):
        inv.status = "reviewed"

    log_action(
        db,
        user_id=current_user.id,
        entity_type="invoice",
        entity_id=inv.id,
        action="update",
        old_values=old_values,
        new_values=new_values,
        ip_address=request.client.host if request.client else None,
    )

    db.commit()
    db.refresh(inv)
    return _to_out(inv)


@router.post("/{invoice_id}/approve", response_model=InvoiceOut)
def approve_invoice(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "accountant")),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")
    if inv.status not in ("reviewed", "compliance_checked"):
        raise HTTPException(status_code=400, detail=f"現在のステータス({inv.status})では承認できません")

    from datetime import datetime, timezone
    inv.status = "approved"
    inv.approved_by_id = current_user.id
    inv.approved_at = datetime.now(timezone.utc)

    log_action(
        db,
        user_id=current_user.id,
        entity_type="invoice",
        entity_id=inv.id,
        action="approve",
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(inv)
    return _to_out(inv)


@router.post("/{invoice_id}/reject", response_model=InvoiceOut)
def reject_invoice(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "accountant")),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")

    inv.status = "rejected"

    log_action(
        db,
        user_id=current_user.id,
        entity_type="invoice",
        entity_id=inv.id,
        action="reject",
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(inv)
    return _to_out(inv)


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")
    if inv.retention_until and date.today() < inv.retention_until:
        raise HTTPException(status_code=400, detail=f"保管期間中({inv.retention_until}まで)のため削除できません")
    inv.is_deleted = True
    log_action(
        db,
        user_id=current_user.id,
        entity_type="invoice",
        entity_id=inv.id,
        action="soft_delete",
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return {"ok": True}


@router.get("/{invoice_id}/verify-hash")
def verify_invoice_hash(invoice_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv or not inv.file_path:
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    abs_path = os.path.join(settings.UPLOAD_DIR, inv.file_path)
    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="ファイルが存在しません")
    is_valid = verify_file_hash(abs_path, inv.file_hash_sha256)
    return {"valid": is_valid, "expected": inv.file_hash_sha256}


def _parse_date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _to_decimal(value) -> Decimal | None:
    if value is None:
        return None
    try:
        cleaned = str(value).replace(",", "").replace("¥", "").replace("円", "").strip()
        return Decimal(cleaned)
    except Exception:
        return None
