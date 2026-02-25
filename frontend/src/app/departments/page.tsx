"use client";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { api } from "@/lib/api";
import type { Department } from "@/types";
import { Plus } from "lucide-react";

export default function DepartmentsPage() {
  const [depts, setDepts] = useState<Department[]>([]);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const load = () => api.getDepartments().then(setDepts).catch(() => {});
  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!name || !code) return;
    await api.createDepartment({ name, code });
    setName(""); setCode(""); load();
  };

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">事業部管理</h1>
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="font-semibold mb-3">新規追加</h2>
          <div className="flex gap-2">
            <input placeholder="事業部名" value={name} onChange={e => setName(e.target.value)} className="border rounded px-3 py-1.5 text-sm flex-1" />
            <input placeholder="コード" value={code} onChange={e => setCode(e.target.value)} className="border rounded px-3 py-1.5 text-sm w-32" />
            <button onClick={create} className="flex items-center gap-1 bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700"><Plus size={14} />追加</button>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50"><tr><th className="text-left px-4 py-2">ID</th><th className="text-left px-4 py-2">名前</th><th className="text-left px-4 py-2">コード</th><th className="text-left px-4 py-2">状態</th></tr></thead>
            <tbody>{depts.map(d => (<tr key={d.id} className="border-t"><td className="px-4 py-2">{d.id}</td><td className="px-4 py-2">{d.name}</td><td className="px-4 py-2">{d.code}</td><td className="px-4 py-2">{d.is_active ? <span className="text-green-600">有効</span> : <span className="text-gray-400">無効</span>}</td></tr>))}</tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
