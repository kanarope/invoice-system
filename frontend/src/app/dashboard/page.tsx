"use client";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { api } from "@/lib/api";
import { formatCurrency, STATUS_LABELS } from "@/lib/utils";
import type { DashboardSummary } from "@/types";
import { FileText, AlertTriangle, Clock, CheckCircle } from "lucide-react";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  useEffect(() => { api.getDashboard().then(setData).catch(() => {}); }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">ダッシュボード</h1>
        {!data ? <p className="text-gray-500">読み込み中...</p> : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <Card icon={<FileText />} label="請求書総数" value={data.total_invoices} color="blue" />
              <Card icon={<Clock />} label="支払期限7日以内" value={data.upcoming_due_7days} color="yellow" />
              <Card icon={<AlertTriangle />} label="期限超過" value={data.overdue} color="red" />
              <Card icon={<CheckCircle />} label="振込済" value={data.by_status?.transferred || 0} color="green" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-5">
                <h2 className="font-semibold mb-3">ステータス別</h2>
                {Object.entries(data.by_status || {}).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1 text-sm"><span>{STATUS_LABELS[k] || k}</span><span className="font-medium">{v}</span></div>
                ))}
              </div>
              <div className="bg-white rounded-lg shadow p-5">
                <h2 className="font-semibold mb-3">事業部別</h2>
                {data.by_department?.map((d) => (
                  <div key={d.name} className="flex justify-between py-1 text-sm"><span>{d.name}</span><span className="font-medium">{formatCurrency(d.total_amount)} ({d.count}件)</span></div>
                ))}
                {(!data.by_department || data.by_department.length === 0) && <p className="text-gray-400 text-sm">データなし</p>}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function Card({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  const colors: Record<string, string> = { blue: "bg-blue-50 text-blue-600", yellow: "bg-yellow-50 text-yellow-600", red: "bg-red-50 text-red-600", green: "bg-green-50 text-green-600" };
  return (
    <div className="bg-white rounded-lg shadow p-5 flex items-center gap-4">
      <div className={`p-3 rounded-lg ${colors[color]}`}>{icon}</div>
      <div><p className="text-sm text-gray-500">{label}</p><p className="text-2xl font-bold">{value}</p></div>
    </div>
  );
}
