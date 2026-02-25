import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "請求書管理システム", description: "請求書回収・分類・振込設定システム" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
