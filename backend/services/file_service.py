from __future__ import annotations
from typing import Optional

import hashlib
import os
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta

from PIL import Image
from config import settings


def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def verify_file_hash(file_path: str, expected_hash: str) -> bool:
    with open(file_path, "rb") as f:
        actual = compute_sha256(f.read())
    return actual == expected_hash


def save_upload(file_bytes: bytes, original_filename: str) -> tuple[str, str]:
    """Save uploaded file and return (relative_path, sha256_hash)."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(original_filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    rel_path = unique_name
    abs_path = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    sha256 = compute_sha256(file_bytes)
    return rel_path, sha256


def check_image_dpi(file_path: str) -> Optional[int]:
    """Return DPI of image if available, else None."""
    try:
        with Image.open(file_path) as img:
            dpi = img.info.get("dpi")
            if dpi:
                return min(int(dpi[0]), int(dpi[1]))
    except Exception:
        pass
    return None


def calculate_retention_date(invoice_date: Optional[date]) -> date:
    base = invoice_date or date.today()
    return base + relativedelta(years=settings.RETENTION_YEARS)
