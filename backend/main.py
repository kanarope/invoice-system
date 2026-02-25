from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from config import settings
import models  # noqa: F401 -- ensure all models are imported for table creation

from routers import auth, departments, vendors, invoices, transfers, compliance, users, gmail, dashboard, audit


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(title="請求書管理システム", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(departments.router)
app.include_router(vendors.router)
app.include_router(invoices.router)
app.include_router(transfers.router)
app.include_router(compliance.router)
app.include_router(gmail.router)
app.include_router(dashboard.router)
app.include_router(audit.router)


@app.get("/")
def health():
    return {"status": "ok", "service": "請求書管理システム"}
