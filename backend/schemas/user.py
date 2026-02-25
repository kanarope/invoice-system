from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: str = "department"
    department_id: int | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    department_id: int | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: str
    department_id: int | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
