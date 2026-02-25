"""freee API連携 -- 振込設定・取引登録"""

import httpx
from config import settings

FREEE_API_BASE = "https://api.freee.co.jp/api/1"

_token_store: dict = {}


def set_tokens(access_token: str, refresh_token: str, company_id: int):
    _token_store["access_token"] = access_token
    _token_store["refresh_token"] = refresh_token
    _token_store["company_id"] = company_id


def _headers() -> dict:
    token = _token_store.get("access_token", "")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_auth_url() -> str:
    return (
        f"https://accounts.secure.freee.co.jp/public_api/authorize"
        f"?client_id={settings.FREEE_CLIENT_ID}"
        f"&redirect_uri={settings.FREEE_REDIRECT_URI}"
        f"&response_type=code&prompt=consent"
    )


def exchange_code(code: str) -> dict:
    resp = httpx.post(
        "https://accounts.secure.freee.co.jp/public_api/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.FREEE_CLIENT_ID,
            "client_secret": settings.FREEE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.FREEE_REDIRECT_URI,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    me = httpx.get(f"{FREEE_API_BASE}/users/me", headers={"Authorization": f"Bearer {data['access_token']}"}, timeout=15)
    me.raise_for_status()
    company_id = me.json()["user"]["companies"][0]["id"]

    set_tokens(data["access_token"], data["refresh_token"], company_id)
    return {"company_id": company_id, **data}


def create_deal(
    invoice_date: str,
    due_date: str,
    amount: int,
    partner_name: str,
    description: str = "",
    account_item_id: int | None = None,
) -> dict:
    """Create a payable deal in freee."""
    company_id = _token_store.get("company_id")
    if not company_id:
        raise RuntimeError("freee未認証です。先にOAuth認証を完了してください。")

    detail = {
        "tax_code": 136,
        "account_item_id": account_item_id or 0,
        "amount": amount,
        "description": description,
    }

    body = {
        "company_id": company_id,
        "issue_date": invoice_date,
        "due_date": due_date,
        "type": "expense",
        "partner_name": partner_name,
        "details": [detail],
    }

    resp = httpx.post(f"{FREEE_API_BASE}/deals", headers=_headers(), json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def create_transfer(
    date: str,
    from_wallet_id: int,
    to_wallet_id: int,
    amount: int,
    description: str = "",
) -> dict:
    """Create a bank transfer record in freee."""
    company_id = _token_store.get("company_id")
    body = {
        "company_id": company_id,
        "from_walletable_type": "bank_account",
        "from_walletable_id": from_wallet_id,
        "to_walletable_type": "bank_account",
        "to_walletable_id": to_wallet_id,
        "amount": amount,
        "date": date,
        "description": description,
    }
    resp = httpx.post(f"{FREEE_API_BASE}/transfers", headers=_headers(), json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()
