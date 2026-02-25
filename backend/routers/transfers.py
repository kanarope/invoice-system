from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from database import get_db
from models.invoice import Invoice
from models.user import User
from services.auth_service import get_current_user, require_role
from services.moneyforward_service import get_auth_url, exchange_code, create_billing
from services.audit_service import log_action

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


@router.get("/mf/auth-url")
def mf_auth_url(_=Depends(require_role("admin", "accountant"))):
    return {"url": get_auth_url()}


@router.get("/mf/callback")
def mf_callback(code: str = Query(...)):
    try:
        result = exchange_code(code)
        return {"ok": True, "token_type": result.get("token_type")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{invoice_id}/execute")
def execute_transfer(
    invoice_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "accountant")),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="請求書が見つかりません")
    if inv.status != "approved":
        raise HTTPException(status_code=400, detail="承認済みの請求書のみ振込設定できます")

    items = None
    if inv.details:
        items = [
            {"description": d.description or "品目", "amount": int(d.amount) if d.amount else 0}
            for d in inv.details
        ]

    try:
        result = create_billing(
            invoice_date=str(inv.invoice_date) if inv.invoice_date else "",
            due_date=str(inv.due_date) if inv.due_date else "",
            amount=int(inv.total_amount) if inv.total_amount else 0,
            partner_name=inv.vendor.name if inv.vendor else "不明",
            description=f"請求書#{inv.invoice_number or inv.id}",
            items=items,
        )
        inv.status = "transferred"
        log_action(
            db,
            user_id=current_user.id,
            entity_type="invoice",
            entity_id=inv.id,
            action="transfer",
            new_values={"mf_billing": result},
            ip_address=request.client.host if request.client else None,
        )
        db.commit()
        return {"ok": True, "billing": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"マネーフォワード連携エラー: {str(e)}")
