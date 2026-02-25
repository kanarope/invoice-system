"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FileText, Building2, ShieldCheck, Settings, LogOut } from "lucide-react";
import { api } from "@/lib/api";

const nav = [
  { href: "/dashboard", label: "ダッシュボード", icon: LayoutDashboard },
  { href: "/invoices", label: "請求書", icon: FileText },
  { href: "/departments", label: "事業部", icon: Building2 },
  { href: "/compliance", label: "コンプライアンス", icon: ShieldCheck },
  { href: "/settings", label: "設定", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-56 bg-gray-900 text-white min-h-screen flex flex-col">
      <div className="p-4 text-lg font-bold border-b border-gray-700">請求書管理</div>
      <nav className="flex-1 p-2 space-y-1">
        {nav.map((n) => {
          const active = pathname.startsWith(n.href);
          return (
            <Link key={n.href} href={n.href} className={`flex items-center gap-3 px-3 py-2 rounded text-sm ${active ? "bg-gray-700" : "hover:bg-gray-800"}`}>
              <n.icon size={18} />
              {n.label}
            </Link>
          );
        })}
      </nav>
      <button onClick={() => { api.clearToken(); window.location.href = "/login"; }} className="flex items-center gap-3 px-5 py-3 text-sm text-gray-400 hover:text-white border-t border-gray-700">
        <LogOut size={18} />ログアウト
      </button>
    </aside>
  );
}
