import base64
import json
import mimetypes
import re

from openai import OpenAI
from config import settings

client: OpenAI | None = None


def _get_client() -> OpenAI:
    global client
    if client is None:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return client


EXTRACTION_PROMPT = """あなたは日本の請求書を解析する専門家です。
添付された請求書画像/PDFから以下の情報をJSON形式で抽出してください。

必須フィールド:
- vendor_name: 請求元会社名
- invoice_number: 請求書番号
- invoice_date: 請求日 (YYYY-MM-DD)
- due_date: 支払期日 (YYYY-MM-DD)
- total_amount: 請求金額（税込合計、数値のみ）
- subtotal_amount: 税抜金額（数値のみ）
- tax_amount: 消費税額合計（数値のみ）
- tax_8_amount: 8%対象の消費税額（数値のみ、該当なしはnull）
- tax_10_amount: 10%対象の消費税額（数値のみ、該当なしはnull）
- invoice_registration_number: 適格請求書発行事業者の登録番号（T+13桁、見つからなければnull）
- recipient_name: 請求先（書類の交付を受ける事業者名）
- bank_account:
    - bank_name: 銀行名
    - branch_name: 支店名
    - account_type: 口座種別（普通/当座）
    - account_number: 口座番号
    - account_holder: 口座名義
- items: 品目リスト
    - description: 品目名/摘要
    - amount: 金額
    - tax: 消費税額
    - tax_rate: 税率（"8%" or "10%"）

値が読み取れない場合はnullとしてください。
JSON形式のみ出力してください（マークダウン不要）。"""


def extract_invoice_data(file_path: str) -> dict:
    """Extract structured invoice data from an image/PDF using GPT-4o Vision."""
    c = _get_client()

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    b64 = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    response = c.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACTION_PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                ],
            }
        ],
        temperature=0.1,
        max_tokens=4000,
    )

    content = response.choices[0].message.content.strip()

    json_match = re.search(r"```(?:json)?\s*\n(.*?)```", content, re.DOTALL)
    if json_match:
        content = json_match.group(1).strip()

    brace_start = content.find("{")
    brace_end = content.rfind("}")
    if brace_start != -1 and brace_end != -1:
        content = content[brace_start : brace_end + 1]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"_raw_text": content, "_parse_error": True}
