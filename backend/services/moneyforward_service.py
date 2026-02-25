"""マネーフォワード クラウド請求書 API連携 -- 振込設定・取引登録"""

import httpx
from config import settings

MF_API_BASE = "https://invoice.moneyforward.com/api/v3"
MF_AUTH_BASE = "https://api.biz.moneyforward.com"

_token_store: dict = {}


def set_tokens(access_token: str, refresh_token: str):
    _token_store["access_token"] = access_token
    _token_store["refresh_token"] = refresh_token


def _headers() -> dict:
    token = _token_store.get("access_token", "")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def get_auth_url() -> str:
    return (
        f"{MF_AUTH_BASE}/authorize"
        f"?client_id={settings.MF_CLIENT_ID}"
        f"&redirect_uri={settings.MF_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=mfc/invoice/write mfc/invoice/read"
    )


def exchange_code(code: str) -> dict:
    resp = httpx.post(
        f"{MF_AUTH_BASE}/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.MF_CLIENT_ID,
            "client_secret": settings.MF_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.MF_REDIRECT_URI,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    set_tokens(data["access_token"], data.get("refresh_token", ""))
    return data


def refresh_access_token() -> dict:
    rt = _token_store.get("refresh_token")
    if not rt:
        raise RuntimeError("マネーフォワード未認証です。先にOAuth認証を完了してください。")
    resp = httpx.post(
        f"{MF_AUTH_BASE}/token",
        data={
            "grant_type": "refresh_token",
            "client_id": settings.MF_CLIENT_ID,
            "client_secret": settings.MF_CLIENT_SECRET,
            "refresh_token": rt,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    set_tokens(data["access_token"], data.get("refresh_token", rt))
    return data


def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """401時にトークンをリフレッシュして1回リトライ"""
    resp = httpx.request(method, url, headers=_headers(), timeout=30, **kwargs)
    if resp.status_code == 401:
        refresh_access_token()
        resp = httpx.request(method, url, headers=_headers(), timeout=30, **kwargs)
    resp.raise_for_status()
    return resp


def get_partners(page: int = 1, per_page: int = 100) -> dict:
    """取引先一覧を取得"""
    resp = _request_with_retry("GET", f"{MF_API_BASE}/partners", params={"page": page, "per_page": per_page})
    return resp.json()


def find_or_create_partner(name: str) -> dict:
    """取引先を名前で検索し、なければ作成"""
    partners = get_partners()
    for p in partners.get("data", []):
        if p.get("name") == name:
            return p

    resp = _request_with_retry("POST", f"{MF_API_BASE}/partners", json={"partner": {"name": name}})
    return resp.json()


def create_billing(
    invoice_date: str,
    due_date: str,
    amount: int,
    partner_name: str,
    description: str = "",
    items: list[dict] | None = None,
) -> dict:
    """マネーフォワードに請求データ（支払い）を登録"""
    if not _token_store.get("access_token"):
        raise RuntimeError("マネーフォワード未認証です。先にOAuth認証を完了してください。")

    partner = find_or_create_partner(partner_name)
    partner_id = partner.get("id") or partner.get("data", {}).get("id")

    billing_items = []
    if items:
        for item in items:
            billing_items.append({
                "name": item.get("description", "品目"),
                "quantity": 1,
                "unit_price": int(item.get("amount", 0)),
                "tax_type": "with_tax",
            })
    else:
        billing_items.append({
            "name": description or "請求書支払い",
            "quantity": 1,
            "unit_price": amount,
            "tax_type": "with_tax",
        })

    body = {
        "billing": {
            "partner_id": partner_id,
            "billing_date": invoice_date,
            "due_date": due_date,
            "billing_type": "other",
            "items": billing_items,
        }
    }

    resp = _request_with_retry("POST", f"{MF_API_BASE}/billings", json=body)
    return resp.json()


def get_billings(page: int = 1, per_page: int = 20) -> dict:
    """登録済み請求データ一覧を取得"""
    resp = _request_with_retry("GET", f"{MF_API_BASE}/billings", params={"page": page, "per_page": per_page})
    return resp.json()
