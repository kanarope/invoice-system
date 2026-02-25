"""事業部自動分類"""

from __future__ import annotations
from typing import Optional

from sqlalchemy.orm import Session
from models.vendor import Vendor
from models.invoice import Invoice


def classify_department(db: Session, vendor_name: Optional[str], description: Optional[str] = None) -> Optional[int]:
    """Attempt to auto-classify department based on vendor history."""
    if not vendor_name:
        return None

    vendor = db.query(Vendor).filter(Vendor.name == vendor_name).first()
    if vendor and vendor.default_department_id:
        return vendor.default_department_id

    past = (
        db.query(Invoice)
        .join(Vendor)
        .filter(Vendor.name == vendor_name, Invoice.department_id.isnot(None))
        .order_by(Invoice.created_at.desc())
        .first()
    )
    if past:
        return past.department_id

    return None


def update_vendor_department(db: Session, vendor_id: int, department_id: int):
    """Update default department for a vendor based on user classification."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if vendor:
        vendor.default_department_id = department_id
        db.flush()
