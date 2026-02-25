"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import StatusBadge from "@/components/StatusBadge";
import ComplianceBadge from "@/components/ComplianceBadge";
import { api } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { Invoice } from "@/types";

export default function InvoiceDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [inv, setInv] = useState<Invoice | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => { if (id) api.getInvoice(Number(id)).then(setInv).catch(() => router.push("/invoices")); }, [id]);

  const act = async (fn: () => Promise<any>, label: string) => {
    try { await fn(); setMsg(label + "完了"); api.getInvoice(Number(id)).then(setInv); } catch (e: any) { setMsg(e.message); }
  };

  if (!inv) return <div className="flex min-h-screen"><Sidebar /><main className="flex-1 p-6">読み込み中...</main></div>;

  const fileUrl = inv.file_path ? "http://localhost:8000/uploads/" + inv.file_path : null;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => router.push("/invoices")} className="text-sm text-gray-500 hover:text-gray-700">← 一覧に戻る</button>
          <h1 className="text-xl font-bold">請求書 #{inv.id}</h1>
          <StatusBadge status={inv.status} />
        </div>
        {msg && <p className="mb-3 text-sm text-blue-600 bg-blue-50 px-3 py-2 rounded">{msg}</p>}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            {fileUrl && (
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold mb-2">原本</h2>
                {inv.file_path?.endsWith(".pdf") ? <iframe src={fileUrl} className="w-full h-96 border rounded" /> : <img src={fileUrl} alt="請求書" className="max-w-full rounded" />}
              </div>
            )}
            {inv.compliance_check_result && (
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold mb-2">コンプライアンスチェック</h2>
                <p className={inv.compliance_check_result.passed ? "text-green-600 font-medium" : "text-red-600 font-medium"}>{inv.compliance_check_result.passed ? "全項目OK" : "不備あり"}</p>
                {inv.compliance_check_result.missing_items?.length > 0 && <ul className="mt-2 text-sm text-red-600 list-disc pl-5">{inv.compliance_check_result.missing_items.map((m, i) => <li key={i}>{m}</li>)}</ul>}
              </div>
            )}
          </div>
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="font-semibold mb-3">基本情報</h2>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                <dt className="text-gray-500">取引先</dt><dd>{inv.vendor_name || "-"}</dd>
                <dt className="text-gray-500">請求書番号</dt><dd>{inv.invoice_number || "-"}</dd>
                <dt className="text-gray-500">請求日</dt><dd>{formatDate(inv.invoice_date)}</dd>
                <dt className="text-gray-500">支払期日</dt><dd>{formatDate(inv.due_date)}</dd>
                <dt className="text-gray-500">税抜金額</dt><dd>{formatCurrency(inv.subtotal_amount)}</dd>
                <dt className="text-gray-500">消費税</dt><dd>{formatCurrency(inv.tax_amount)}</dd>
                <dt className="text-gray-500">合計金額</dt><dd className="font-bold text-lg">{formatCurrency(inv.total_amount)}</dd>
                <dt className="text-gray-500">事業部</dt><dd>{inv.department_name || "未分類"}</dd>
                <dt className="text-gray-500">適格番号</dt><dd className="flex items-center gap-2">{inv.invoice_registration_number || "-"} <ComplianceBadge status={inv.invoice_registration_status} /></dd>
                <dt className="text-gray-500">請求先</dt><dd>{inv.recipient_name || "-"}</dd>
                <dt className="text-gray-500">保管期限</dt><dd>{formatDate(inv.retention_until)}</dd>
              </dl>
            </div>
            {inv.bank_account && (
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold mb-3">振込先口座</h2>
                <dl className="grid grid-cols-2 gap-2 text-sm">
                  <dt className="text-gray-500">銀行</dt><dd>{inv.bank_account.bank_name}</dd>
                  <dt className="text-gray-500">支店</dt><dd>{inv.bank_account.branch_name}</dd>
                  <dt className="text-gray-500">種別</dt><dd>{inv.bank_account.account_type}</dd>
                  <dt className="text-gray-500">口座番号</dt><dd>{inv.bank_account.account_number}</dd>
                  <dt className="text-gray-500">名義</dt><dd>{inv.bank_account.account_holder}</dd>
                </dl>
              </div>
            )}
            {inv.details.length > 0 && (
              <div className="bg-white rounded-lg shadow p-4">
                <h2 className="font-semibold mb-3">明細</h2>
                <table className="w-full text-sm"><thead><tr className="text-gray-500"><th className="text-left py-1">品目</th><th className="text-right py-1">金額</th><th className="text-right py-1">税</th><th className="text-right py-1">税率</th></tr></thead>
                <tbody>{inv.details.map((d, i) => <tr key={i} className="border-t"><td className="py-1">{d.description}</td><td className="text-right">{formatCurrency(d.amount)}</td><td className="text-right">{formatCurrency(d.tax)}</td><td className="text-right">{d.tax_rate}</td></tr>)}</tbody></table>
              </div>
            )}
            <div className="flex gap-2 flex-wrap">
              {["extracted", "compliance_checked"].includes(inv.status) && <button onClick={() => act(() => api.approveInvoice(inv.id), "承認")} className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700">承認</button>}
              {["extracted", "compliance_checked", "reviewed"].includes(inv.status) && <button onClick={() => act(() => api.rejectInvoice(inv.id), "差戻し")} className="bg-red-600 text-white px-4 py-2 rounded text-sm hover:bg-red-700">差戻し</button>}
              {inv.status === "approved" && <button onClick={() => act(() => api.executeTransfer(inv.id), "振込設定")} className="bg-purple-600 text-white px-4 py-2 rounded text-sm hover:bg-purple-700">振込設定</button>}
              <button onClick={() => act(() => api.checkCompliance(inv.id), "コンプライアンス再チェック")} className="bg-cyan-600 text-white px-4 py-2 rounded text-sm hover:bg-cyan-700">再チェック</button>
              <button onClick={() => api.verifyHash(inv.id).then(r => setMsg(r.valid ? "改ざんなし" : "改ざん検知!"))} className="border px-4 py-2 rounded text-sm hover:bg-gray-50">ハッシュ検証</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
