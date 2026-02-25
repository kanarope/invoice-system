from __future__ import annotations
from typing import Optional

from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "department"
    department_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    department_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
