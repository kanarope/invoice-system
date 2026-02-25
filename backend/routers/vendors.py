from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.vendor import Vendor
from schemas.vendor import VendorCreate, VendorUpdate, VendorOut
from services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


@router.get("", response_model=list[VendorOut])
def list_vendors(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Vendor).order_by(Vendor.name).all()


@router.post("", response_model=VendorOut)
def create_vendor(body: VendorCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    vendor = Vendor(
        name=body.name,
        invoice_registration_number=body.invoice_registration_number,
        default_department_id=body.default_department_id,
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, body: VendorUpdate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="取引先が見つかりません")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    db.commit()
    db.refresh(vendor)
    return vendor
