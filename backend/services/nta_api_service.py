"""国税庁 適格請求書発行事業者公表API連携"""

import httpx
from config import settings
from schemas.compliance import NTAVerificationResult


def verify_registration_number(reg_number: str) -> NTAVerificationResult:
    """Verify an invoice registration number against the NTA public API."""
    clean = reg_number.strip().upper()
    if not clean.startswith("T"):
        clean = "T" + clean

    url = f"{settings.NTA_API_BASE_URL}/num"
    params = {"id": clean, "type": "21"}

    try:
        resp = httpx.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            return NTAVerificationResult(
                registration_number=clean,
                is_valid=False,
                raw_response={"status_code": resp.status_code, "body": resp.text[:500]},
            )

        data = resp.json()
        announcements = data.get("announcement", [])
        if not announcements:
            return NTAVerificationResult(
                registration_number=clean,
                is_valid=False,
                raw_response=data,
            )

        rec = announcements[0]
        return NTAVerificationResult(
            registration_number=clean,
            is_valid=True,
            company_name=rec.get("name"),
            address=rec.get("address"),
            registration_date=rec.get("registrationDate"),
            update_date=rec.get("updateDate"),
            raw_response=data,
        )
    except Exception as e:
        return NTAVerificationResult(
            registration_number=clean,
            is_valid=False,
            raw_response={"error": str(e)},
        )
