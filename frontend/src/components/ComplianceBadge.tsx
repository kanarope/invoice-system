import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

interface Props {
  status: string | null | undefined;
}

export default function ComplianceBadge({ status }: Props) {
  if (status === "valid") return <span className="inline-flex items-center gap-1 text-green-600 text-xs"><CheckCircle size={14} />有効</span>;
  if (status === "invalid") return <span className="inline-flex items-center gap-1 text-red-600 text-xs"><XCircle size={14} />無効</span>;
  return <span className="inline-flex items-center gap-1 text-gray-400 text-xs"><AlertTriangle size={14} />未確認</span>;
}
