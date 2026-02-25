"""電帳法・インボイス制度コンプライアンスチェック"""

from schemas.compliance import ComplianceCheckResult
from services.nta_api_service import verify_registration_number


def check_invoice_compliance(ai_result: dict | None) -> ComplianceCheckResult:
    """Check if extracted invoice data meets qualified invoice requirements."""
    if not ai_result or ai_result.get("_parse_error"):
        return ComplianceCheckResult(missing_items=["AI解析失敗"], passed=False)

    result = ComplianceCheckResult()
    missing = []

    reg_num = ai_result.get("invoice_registration_number")
    if reg_num:
        result.has_registration_number = True
        nta = verify_registration_number(reg_num)
        result.registration_valid = nta.is_valid
        if not nta.is_valid:
            missing.append("適格請求書発行事業者番号が無効です")
    else:
        missing.append("適格請求書発行事業者の登録番号")

    if ai_result.get("invoice_date"):
        result.has_invoice_date = True
    else:
        missing.append("取引年月日")

    items = ai_result.get("items", [])
    if items and any(i.get("description") for i in items):
        result.has_description = True
    elif ai_result.get("description"):
        result.has_description = True
    else:
        missing.append("取引内容")

    has_8 = ai_result.get("tax_8_amount") is not None
    has_10 = ai_result.get("tax_10_amount") is not None
    if has_8 or has_10:
        result.has_tax_breakdown = True
    elif items and any(i.get("tax_rate") for i in items):
        result.has_tax_breakdown = True
    else:
        missing.append("税率ごとに区分した対価の額")

    if ai_result.get("tax_amount") is not None:
        result.has_tax_amount = True
    else:
        missing.append("税率ごとに区分した消費税額")

    if ai_result.get("recipient_name"):
        result.has_recipient_name = True
    else:
        missing.append("書類の交付を受ける事業者の氏名または名称")

    result.missing_items = missing
    result.passed = len(missing) == 0
    return result
