from datetime import datetime
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    code: str


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_active: bool | None = None


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
