from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from services.auth_service import require_role
from services.audit_service import get_audit_logs

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
def list_audit_logs(
    entity_type: str | None = None,
    entity_id: int | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin", "accountant")),
):
    logs = get_audit_logs(db, entity_type=entity_type, entity_id=entity_id, limit=limit, offset=offset)
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "action": l.action,
            "old_values": l.old_values,
            "new_values": l.new_values,
            "ip_address": l.ip_address,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
