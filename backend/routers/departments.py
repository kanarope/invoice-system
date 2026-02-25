from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.department import Department
from schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut
from services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Department).order_by(Department.name).all()


@router.post("", response_model=DepartmentOut)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    existing = db.query(Department).filter(Department.code == body.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="この事業部コードは既に使用されています")
    dept = Department(name=body.name, code=body.code)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(dept_id: int, body: DepartmentUpdate, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="事業部が見つかりません")
    if body.name is not None:
        dept.name = body.name
    if body.code is not None:
        dept.code = body.code
    if body.is_active is not None:
        dept.is_active = body.is_active
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="事業部が見つかりません")
    dept.is_active = False
    db.commit()
    return {"ok": True}
