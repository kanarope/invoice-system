import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number | string | null | undefined): string {
  if (amount === null || amount === undefined) return "-";
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY", maximumFractionDigits: 0 }).format(num);
}

export function formatDate(date: string | null | undefined): string {
  if (!date) return "-";
  return new Date(date).toLocaleDateString("ja-JP");
}

export const STATUS_LABELS: Record<string, string> = {
  uploaded: "未処理",
  extracted: "AI読取済",
  extraction_failed: "読取失敗",
  compliance_checked: "チェック済",
  reviewed: "確認済",
  approved: "承認済",
  rejected: "差戻し",
  transferred: "振込済",
  archived: "保管済",
};

export const STATUS_COLORS: Record<string, string> = {
  uploaded: "bg-gray-100 text-gray-700",
  extracted: "bg-blue-100 text-blue-700",
  extraction_failed: "bg-red-100 text-red-700",
  compliance_checked: "bg-cyan-100 text-cyan-700",
  reviewed: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  transferred: "bg-purple-100 text-purple-700",
  archived: "bg-gray-100 text-gray-600",
};
