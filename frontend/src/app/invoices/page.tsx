"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import Sidebar from "@/components/Sidebar";
import StatusBadge from "@/components/StatusBadge";
import FileDropzone from "@/components/FileDropzone";
import ComplianceBadge from "@/components/ComplianceBadge";
import { api } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { Invoice, InvoiceList } from "@/types";
import { Plus, Search } from "lucide-react";

export default function InvoicesPage() {
  const [data, setData] = useState<InvoiceList | null>(null);
  const [page, setPage] = useState(1);
  const [showUpload, setShowUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [filters, setFilters] = useState({ vendor_name: "", status: "", date_from: "", date_to: "" });

  const load = () => { api.getInvoices({ page, per_page: 20, ...filters }).then(setData).catch(() => {}); };
  useEffect(load, [page, filters]);

  const handleUpload = async (files: File[]) => {
    setUploading(true);
    try { await api.uploadInvoices(files); setShowUpload(false); load(); } catch {} finally { setUploading(false); }
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">請求書一覧</h1>
          <button onClick={() => setShowUpload(!showUpload)} className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"><Plus size={16} />アップロード</button>
        </div>
        {showUpload && <div className="mb-4">{uploading ? <p className="text-center py-8 text-gray-500">アップロード・解析中...</p> : <FileDropzone onFiles={handleUpload} />}</div>}
        <div className="flex gap-2 mb-4 flex-wrap">
          <input placeholder="取引先名" value={filters.vendor_name} onChange={e => setFilters(f => ({ ...f, vendor_name: e.target.value }))} className="border rounded px-3 py-1.5 text-sm w-40" />
          <select value={filters.status} onChange={e => setFilters(f => ({ ...f, status: e.target.value }))} className="border rounded px-3 py-1.5 text-sm">
            <option value="">全ステータス</option>
            {["uploaded","extracted","compliance_checked","reviewed","approved","rejected","transferred"].map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <input type="date" value={filters.date_from} onChange={e => setFilters(f => ({ ...f, date_from: e.target.value }))} className="border rounded px-3 py-1.5 text-sm" />
          <input type="date" value={filters.date_to} onChange={e => setFilters(f => ({ ...f, date_to: e.target.value }))} className="border rounded px-3 py-1.5 text-sm" />
          <button onClick={load} className="bg-gray-100 px-3 py-1.5 rounded text-sm hover:bg-gray-200"><Search size={14} /></button>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr>{["ID","ステータス","取引先","請求日","支払期日","金額","適格番号","事業部",""].map(h => <th key={h} className="text-left px-4 py-2 font-medium text-gray-600">{h}</th>)}</tr></thead>
            <tbody>
              {data?.items.map(inv => (
                <tr key={inv.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-2">{inv.id}</td>
                  <td className="px-4 py-2"><StatusBadge status={inv.status} /></td>
                  <td className="px-4 py-2">{inv.vendor_name || "-"}</td>
                  <td className="px-4 py-2">{formatDate(inv.invoice_date)}</td>
                  <td className="px-4 py-2">{formatDate(inv.due_date)}</td>
                  <td className="px-4 py-2 font-medium">{formatCurrency(inv.total_amount)}</td>
                  <td className="px-4 py-2"><ComplianceBadge status={inv.invoice_registration_status} /></td>
                  <td className="px-4 py-2">{inv.department_name || "-"}</td>
                  <td className="px-4 py-2"><Link href={"/invoices/" + inv.id} className="text-blue-600 hover:underline text-xs">詳細</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {data && data.total > data.per_page && (
          <div className="flex justify-center gap-2 mt-4">
            <button disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="px-3 py-1 border rounded text-sm disabled:opacity-40">前へ</button>
            <span className="px-3 py-1 text-sm">{page} / {Math.ceil(data.total / data.per_page)}</span>
            <button disabled={page >= Math.ceil(data.total / data.per_page)} onClick={() => setPage(p => p + 1)} className="px-3 py-1 border rounded text-sm disabled:opacity-40">次へ</button>
          </div>
        )}
      </main>
    </div>
  );
}
