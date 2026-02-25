from __future__ import annotations
from typing import Optional

from datetime import datetime
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    code: str


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
