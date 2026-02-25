import { STATUS_LABELS, STATUS_COLORS } from "@/lib/utils";

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[status] || "bg-gray-100 text-gray-600"}`}>
      {STATUS_LABELS[status] || status}
    </span>
  );
}
