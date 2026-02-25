"use client";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { api } from "@/lib/api";
import { ShieldCheck, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

export default function CompliancePage() {
  const [data, setData] = useState<any>(null);
  const [regNum, setRegNum] = useState("");
  const [verifyResult, setVerifyResult] = useState<any>(null);
  useEffect(() => { api.getComplianceDashboard().then(setData).catch(() => {}); }, []);

  const verify = async () => {
    if (!regNum) return;
    const r = await api.checkCompliance(0).catch(() => null);
    const res = await fetch("http://localhost:8000/api/compliance/verify/" + regNum, { headers: { Authorization: "Bearer " + localStorage.getItem("token") } });
    setVerifyResult(await res.json());
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">コンプライアンス</h1>
        {data && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <StatCard icon={<ShieldCheck />} label="請求書総数" value={data.total_invoices} />
            <StatCard icon={<CheckCircle className="text-green-600" />} label="適格番号 有効" value={data.valid_registration} />
            <StatCard icon={<XCircle className="text-red-600" />} label="適格番号 無効" value={data.invalid_registration} />
            <StatCard icon={<AlertTriangle className="text-yellow-600" />} label="未確認" value={data.unchecked_registration} />
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-5 mb-6">
          <h2 className="font-semibold mb-3">適格請求書発行事業者番号の照合</h2>
          <div className="flex gap-2">
            <input placeholder="T1234567890123" value={regNum} onChange={e => setRegNum(e.target.value)} className="border rounded px-3 py-2 text-sm flex-1 max-w-xs" />
            <button onClick={verify} className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700">照合</button>
          </div>
          {verifyResult && (
            <div className="mt-4 p-3 border rounded text-sm">
              <p className={verifyResult.is_valid ? "text-green-600 font-medium" : "text-red-600 font-medium"}>{verifyResult.is_valid ? "有効な事業者です" : "無効または該当なし"}</p>
              {verifyResult.company_name && <p className="mt-1">会社名: {verifyResult.company_name}</p>}
              {verifyResult.address && <p>住所: {verifyResult.address}</p>}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: number }) {
  return <div className="bg-white rounded-lg shadow p-5 flex items-center gap-4"><div className="p-3 rounded-lg bg-gray-50">{icon}</div><div><p className="text-sm text-gray-500">{label}</p><p className="text-2xl font-bold">{value}</p></div></div>;
}
