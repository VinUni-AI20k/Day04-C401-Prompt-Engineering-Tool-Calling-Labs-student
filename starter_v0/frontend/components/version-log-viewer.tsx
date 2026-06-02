"use client";

import { useEffect, useState } from "react";
import { GraduationCap, AlertCircle, RefreshCw, FileText, CheckCircle2, ArrowRight } from "lucide-react";

interface VersionLogRow {
  version: string;
  author: string;
  changed_artifact: string;
  artifact_version: string;
  prompt_hash: string;
  tools_hash: string;
  reason: string;
  hypothesis: string;
  metric_before: string;
  metric_after: string;
  run_file: string;
}

export function VersionLogViewer() {
  const [data, setData] = useState<{ headers: string[]; rows: VersionLogRow[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/version-log");
      if (!res.ok) throw new Error("Failed to fetch version logs");
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center font-mono text-xs text-[#3c3a39]">
        <RefreshCw className="size-4 animate-spin text-[#ff7300] mr-2" />
        /loading-version-logs...
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600 flex items-center gap-2">
        <AlertCircle className="size-4 shrink-0" />
        <span>Error: {error}</span>
      </div>
    );
  }

  const rows = data?.rows || [];

  return (
    <div className="space-y-6">
      {/* Header Info Card */}
      <div className="rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fefcf5] p-5 shadow-xs">
        <div className="flex items-start justify-between">
          <div>
            <span className="font-mono text-[10px] font-bold text-[#ff7300] uppercase tracking-wider">
              /version-registry-system
            </span>
            <h2 className="text-lg font-bold text-[#3c3a39] mt-1">Prompt Engineering Optimization Log</h2>
            <p className="text-xs text-[rgba(11,9,7,0.5)] mt-1.5 leading-5 max-w-2xl">
              Danh sách các phiên bản tối ưu hóa Prompt và cấu hình Tool. Nhật ký này ghi nhận các thay đổi dựa trên bằng chứng (evidence-based), ghi lại giả thuyết cải tiến và đo lường độ chính xác trước & sau khi chạy thử nghiệm.
            </p>
          </div>
          <button
            onClick={fetchLogs}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] text-xs font-mono font-medium hover:bg-[#eaeae2]/30 transition-all text-[#3c3a39]"
          >
            <RefreshCw className="size-3.5" />
            Refresh
          </button>
        </div>
      </div>

      {/* Main Table view */}
      {rows.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[rgba(11,9,7,0.15)] bg-[#fffcf6] p-8 text-center space-y-3">
          <GraduationCap className="size-8 text-[rgba(11,9,7,0.3)] mx-auto" />
          <h3 className="text-sm font-bold text-[#3c3a39]">No Optimization Runs Logged Yet</h3>
          <p className="text-xs text-[rgba(11,9,7,0.5)] max-w-md mx-auto leading-relaxed">
            Bạn cần chạy thử nghiệm baseline và ghi nhận các vòng tối ưu vào file <code className="font-mono bg-[#eaeae2] px-1 py-0.5 rounded text-[10px] text-[#ff272d]">artifacts/version_log.csv</code> sau mỗi lượt tối ưu (v0, v1, v2, v3).
          </p>
        </div>
      ) : (
        <div className="rounded-xl border border-[rgba(11,9,7,0.1)] bg-[#fffcf6] overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#f7f7f5] border-b border-[rgba(11,9,7,0.1)] font-mono text-[9px] uppercase tracking-wider text-[rgba(11,9,7,0.5)]">
                  <th className="px-4 py-3 font-semibold">Version</th>
                  <th className="px-4 py-3 font-semibold">Author</th>
                  <th className="px-4 py-3 font-semibold">Changed Artifact</th>
                  <th className="px-4 py-3 font-semibold">Reason</th>
                  <th className="px-4 py-3 font-semibold">Hypothesis</th>
                  <th className="px-4 py-3 font-semibold text-center">Metric Change</th>
                  <th className="px-4 py-3 font-semibold">Run File</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[rgba(11,9,7,0.06)] text-xs text-[#3c3a39]">
                {rows.map((row, idx) => {
                  const beforeVal = parseFloat(row.metric_before) || 0;
                  const afterVal = parseFloat(row.metric_after) || 0;
                  const isImproved = afterVal > beforeVal;
                  const isDegraded = afterVal < beforeVal;
                  
                  return (
                    <tr key={idx} className="hover:bg-[#eaeae2]/10 transition-colors">
                      <td className="px-4 py-3 font-mono font-bold text-[#ff272d]">
                        {row.version}
                      </td>
                      <td className="px-4 py-3 font-medium text-[rgba(11,9,7,0.7)]">
                        {row.author}
                      </td>
                      <td className="px-4 py-3">
                        <span className="rounded bg-[#eaeae2] px-1.5 py-0.5 font-mono text-[10px] text-[rgba(11,9,7,0.7)] border border-[rgba(11,9,7,0.06)]">
                          {row.changed_artifact}
                        </span>
                      </td>
                      <td className="px-4 py-3 max-w-xs truncate" title={row.reason}>
                        {row.reason}
                      </td>
                      <td className="px-4 py-3 max-w-xs truncate" title={row.hypothesis}>
                        {row.hypothesis}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <div className="flex items-center justify-center gap-1.5 font-mono font-bold">
                          <span className="text-neutral-500">{row.metric_before || "0%"}</span>
                          <ArrowRight className="size-3 text-neutral-400" />
                          <span className={isImproved ? "text-emerald-600 font-semibold" : isDegraded ? "text-red-500" : "text-[#3c3a39]"}>
                            {row.metric_after || "0%"}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono text-[10px] text-[rgba(11,9,7,0.4)] truncate max-w-[120px]" title={row.run_file}>
                        {row.run_file ? row.run_file.split(/[/\\]/).pop() : "-"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
