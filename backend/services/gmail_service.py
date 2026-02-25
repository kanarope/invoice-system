"""Gmail API連携 -- 請求書メール自動取得"""

import base64
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
INVOICE_LABEL = "InvoiceProcessed"


def _get_gmail_service():
    creds = None
    if os.path.exists(settings.GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(settings.GMAIL_TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.GMAIL_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(settings.GMAIL_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _ensure_label(service) -> str:
    results = service.users().labels().list(userId="me").execute()
    for label in results.get("labels", []):
        if label["name"] == INVOICE_LABEL:
            return label["id"]
    body = {"name": INVOICE_LABEL, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
    created = service.users().labels().create(userId="me", body=body).execute()
    return created["id"]


def fetch_invoice_emails(query: str = "subject:請求書 has:attachment -label:InvoiceProcessed") -> list[dict]:
    """Fetch unprocessed invoice emails and return list of {message_id, subject, sender, attachments}."""
    service = _get_gmail_service()
    label_id = _ensure_label(service)

    results = service.users().messages().list(userId="me", q=query, maxResults=50).execute()
    messages = results.get("messages", [])

    output = []
    for msg_meta in messages:
        msg = service.users().messages().get(userId="me", id=msg_meta["id"]).execute()
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}

        attachments = []
        parts = msg["payload"].get("parts", [])
        for part in parts:
            filename = part.get("filename", "")
            if not filename:
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in (".pdf", ".jpg", ".jpeg", ".png"):
                continue

            att_id = part["body"].get("attachmentId")
            if att_id:
                att = service.users().messages().attachments().get(
                    userId="me", messageId=msg_meta["id"], id=att_id
                ).execute()
                data = base64.urlsafe_b64decode(att["data"])
                attachments.append({"filename": filename, "data": data})

        if attachments:
            output.append({
                "message_id": msg_meta["id"],
                "subject": headers.get("Subject", ""),
                "sender": headers.get("From", ""),
                "attachments": attachments,
            })

        service.users().messages().modify(
            userId="me", id=msg_meta["id"], body={"addLabelIds": [label_id]}
        ).execute()

    return output
