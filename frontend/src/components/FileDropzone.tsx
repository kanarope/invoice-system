"use client";
import { useCallback, useState } from "react";
import { Upload } from "lucide-react";

interface Props {
  onFiles: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
}

export default function FileDropzone({ onFiles, accept = ".pdf,.jpg,.jpeg,.png", multiple = true }: Props) {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) onFiles(files);
  }, [onFiles]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length) onFiles(files);
  }, [onFiles]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${dragging ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
    >
      <Upload className="mx-auto mb-3 text-gray-400" size={36} />
      <p className="text-sm text-gray-600 mb-1">ファイルをドラッグ&ドロップ</p>
      <p className="text-xs text-gray-400 mb-3">PDF / JPEG / PNG</p>
      <label className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 cursor-pointer">
        ファイルを選択
        <input type="file" className="hidden" accept={accept} multiple={multiple} onChange={handleChange} />
      </label>
    </div>
  );
}
