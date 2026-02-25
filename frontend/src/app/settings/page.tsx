"use client";
import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import { api } from "@/lib/api";
import type { User } from "@/types";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  useEffect(() => { api.me().then(setUser).catch(() => {}); api.getAuditLogs({ limit: 50 }).then(setAuditLogs).catch(() => {}); }, []);

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-bold mb-6">設定</h1>
        {user && (
          <div className="bg-white rounded-lg shadow p-5 mb-6">
            <h2 className="font-semibold mb-3">アカウント情報</h2>
            <dl className="grid grid-cols-2 gap-2 text-sm max-w-md">
              <dt className="text-gray-500">名前</dt><dd>{user.name}</dd>
              <dt className="text-gray-500">メール</dt><dd>{user.email}</dd>
              <dt className="text-gray-500">権限</dt><dd>{user.role}</dd>
            </dl>
          </div>
        )}
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="font-semibold mb-3">監査ログ（最新50件）</h2>
          <table className="w-full text-xs">
            <thead><tr className="text-gray-500 border-b"><th className="text-left py-1 px-2">日時</th><th className="text-left py-1 px-2">操作</th><th className="text-left py-1 px-2">対象</th><th className="text-left py-1 px-2">ユーザーID</th></tr></thead>
            <tbody>{auditLogs.map(l => <tr key={l.id} className="border-b"><td className="py-1 px-2">{new Date(l.created_at).toLocaleString("ja-JP")}</td><td className="py-1 px-2">{l.action}</td><td className="py-1 px-2">{l.entity_type} #{l.entity_id}</td><td className="py-1 px-2">{l.user_id}</td></tr>)}</tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
