from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from database import get_db
from models.invoice import Invoice
from models.department import Department
from models.user import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    base = db.query(Invoice).filter(Invoice.is_deleted.is_(False))

    if current_user.role == "department" and current_user.department_id:
        base = base.filter(Invoice.department_id == current_user.department_id)

    total = base.count()
    by_status = dict(
        db.query(Invoice.status, sqlfunc.count(Invoice.id))
        .filter(Invoice.is_deleted.is_(False))
        .group_by(Invoice.status)
        .all()
    )

    upcoming_due = (
        base.filter(
            Invoice.due_date.isnot(None),
            Invoice.due_date <= date.today() + timedelta(days=7),
            Invoice.due_date >= date.today(),
            Invoice.status.notin_(["transferred", "cancelled"]),
        ).count()
    )

    overdue = (
        base.filter(
            Invoice.due_date.isnot(None),
            Invoice.due_date < date.today(),
            Invoice.status.notin_(["transferred", "cancelled"]),
        ).count()
    )

    dept_totals = (
        db.query(Department.name, sqlfunc.sum(Invoice.total_amount), sqlfunc.count(Invoice.id))
        .join(Invoice, Invoice.department_id == Department.id)
        .filter(Invoice.is_deleted.is_(False))
        .group_by(Department.name)
        .all()
    )

    return {
        "total_invoices": total,
        "by_status": by_status,
        "upcoming_due_7days": upcoming_due,
        "overdue": overdue,
        "by_department": [
            {"name": name, "total_amount": float(amt or 0), "count": cnt}
            for name, amt, cnt in dept_totals
        ],
    }
