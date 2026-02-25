from sqlalchemy.orm import Session
from models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    user_id: int | None,
    entity_type: str,
    entity_id: int,
    action: str,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
):
    entry = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
    )
    db.add(entry)
    db.flush()
    return entry


def get_audit_logs(
    db: Session,
    entity_type: str | None = None,
    entity_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
):
    q = db.query(AuditLog)
    if entity_type:
        q = q.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.filter(AuditLog.entity_id == entity_id)
    return q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
