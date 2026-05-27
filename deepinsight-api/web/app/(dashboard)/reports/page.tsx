"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText, Download, Sparkles, ChevronDown, ChevronUp,
  Loader2, AlertCircle, CheckCircle, Presentation,
  TrendingUp, AlertTriangle, BarChart2, Lightbulb, Target
} from "lucide-react";
import { fetchApi } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────

interface Dataset {
  id: string;
  file_name: string;
  row_count: number;
  column_count: number;
  quality_score: number;
}

interface ExecutiveSummary {
  dataset_id: string;
  dataset_name: string;
  generated_at: string;
  overview: string;
  performance_insights: string;
  forecast_insights: string;
  anomaly_insights: string;
  model_performance: string;
  recommendations: string;
  conclusion: string;
  raw_narrative: string;
}

// ── Section Card ──────────────────────────────────────────────

const SECTION_META: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  overview: {
    icon: <Target size={16} />,
    color: "text-indigo-400 border-indigo-500/30 bg-indigo-500/10",
    label: "Overview",
  },
  performance_insights: {
    icon: <TrendingUp size={16} />,
    color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
    label: "Performance Insights",
  },
  forecast_insights: {
    icon: <BarChart2 size={16} />,
    color: "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
    label: "Forecast Insights",
  },
  anomaly_insights: {
    icon: <AlertTriangle size={16} />,
    color: "text-red-400 border-red-500/30 bg-red-500/10",
    label: "Anomaly Insights",
  },
  model_performance: {
    icon: <Sparkles size={16} />,
    color: "text-purple-400 border-purple-500/30 bg-purple-500/10",
    label: "Model Performance",
  },
  recommendations: {
    icon: <Lightbulb size={16} />,
    color: "text-yellow-400 border-yellow-500/30 bg-yellow-500/10",
    label: "Recommendations",
  },
  conclusion: {
    icon: <CheckCircle size={16} />,
    color: "text-slate-400 border-slate-500/30 bg-slate-500/10",
    label: "Conclusion",
  },
};

function SummarySection({
  sectionKey,
  content,
}: {
  sectionKey: string;
  content: string;
}) {
  const [open, setOpen] = useState(sectionKey === "overview");
  const meta = SECTION_META[sectionKey] ?? {
    icon: <FileText size={16} />,
    color: "text-slate-400 border-slate-700 bg-slate-800/50",
    label: sectionKey.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
  };

  return (
    <div className={`rounded-xl border ${meta.color} overflow-hidden`}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-3 font-semibold text-sm">
          {meta.icon}
          {meta.label}
        </div>
        <motion.div animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={16} className="opacity-60" />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
          >
            <div className="px-5 pb-5 text-sm text-slate-300 leading-relaxed border-t border-white/5 pt-4 whitespace-pre-wrap">
              {content}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────

export default function ReportsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [format, setFormat] = useState<"json" | "html" | "pdf" | "pptx">("pptx");
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportResult, setReportResult] = useState<{ download_url?: string; html_content?: string } | null>(null);
  const [reportError, setReportError] = useState("");
  const [includeExec, setIncludeExec] = useState(true);

  useEffect(() => {
    fetchApi("/api/datasets/")
      .then((data) => {
        setDatasets(data);
        if (data.length > 0) setSelectedId(data[0].id);
      })
      .catch(() => {});
  }, []);

  const generateSummary = async () => {
    if (!selectedId) return;
    setSummaryLoading(true);
    setSummaryError("");
    setSummary(null);
    try {
      const data = await fetchApi(`/api/reports/${selectedId}/executive-summary`, {
        method: "POST",
      });
      setSummary(data);
    } catch (e: any) {
      setSummaryError(e.message || "Failed to generate summary");
    } finally {
      setSummaryLoading(false);
    }
  };

  const generateReport = async () => {
    if (!selectedId) return;
    setReportLoading(true);
    setReportError("");
    setReportResult(null);
    try {
      const data = await fetchApi("/api/reports/generate", {
        method: "POST",
        body: JSON.stringify({ dataset_id: selectedId, format }),
      });
      setReportResult(data);
    } catch (e: any) {
      setReportError(e.message || "Failed to generate report");
    } finally {
      setReportLoading(false);
    }
  };

  const selectedDataset = datasets.find((d) => d.id === selectedId);

  const SUMMARY_KEYS = [
    "overview",
    "performance_insights",
    "forecast_insights",
    "anomaly_insights",
    "model_performance",
    "recommendations",
    "conclusion",
  ] as const;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-3xl font-bold text-white mb-1">Reports</h1>
        <p className="text-slate-400 text-sm">
          Generate AI-powered executive summaries and export board-ready presentations.
        </p>
      </motion.div>

      {/* Dataset + Format Selector */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-panel rounded-2xl p-6 border border-slate-700/50 space-y-5"
      >
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <FileText size={18} className="text-indigo-400" /> Report Configuration
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2">Dataset</label>
            <select
              value={selectedId}
              onChange={(e) => {
                setSelectedId(e.target.value);
                setSummary(null);
                setReportResult(null);
              }}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              {datasets.length === 0 && <option value="">No datasets</option>}
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.file_name} ({d.row_count?.toLocaleString()} rows)
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2">Export Format</label>
            <div className="grid grid-cols-4 gap-2">
              {(["json", "html", "pdf", "pptx"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFormat(f)}
                  className={`py-3 rounded-lg text-sm font-medium border transition-all ${
                    format === f
                      ? "bg-indigo-600 border-indigo-500 text-white shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                      : "bg-slate-800 border-slate-700 text-slate-400 hover:border-slate-600"
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {selectedDataset && (
          <div className="flex gap-4 text-xs text-slate-500">
            <span>Rows: <span className="text-slate-300">{selectedDataset.row_count?.toLocaleString()}</span></span>
            <span>Columns: <span className="text-slate-300">{selectedDataset.column_count}</span></span>
            <span>Quality: <span className="text-emerald-400">{selectedDataset.quality_score}%</span></span>
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          <button
            onClick={generateSummary}
            disabled={summaryLoading || !selectedId}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-all"
          >
            {summaryLoading ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
            {summaryLoading ? "Generating..." : "Generate Executive Summary"}
          </button>
          <button
            onClick={generateReport}
            disabled={reportLoading || !selectedId}
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-all border border-slate-600"
          >
            {reportLoading ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
            {reportLoading ? "Exporting..." : `Export ${format.toUpperCase()}`}
          </button>
        </div>
      </motion.div>

      {/* Executive Summary Panel */}
      <AnimatePresence>
        {summaryLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="glass-panel rounded-2xl p-8 border border-slate-700/50 flex items-center justify-center gap-3 text-slate-400"
          >
            <Loader2 size={20} className="animate-spin text-indigo-400" />
            <span>AI is generating your executive summary…</span>
          </motion.div>
        )}

        {summaryError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-panel rounded-2xl p-5 border border-red-500/30 bg-red-500/10 flex items-center gap-3 text-red-400 text-sm"
          >
            <AlertCircle size={18} /> {summaryError}
          </motion.div>
        )}

        {summary && !summaryLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                <Sparkles size={18} className="text-indigo-400" />
                Executive Summary — {summary.dataset_name}
              </h2>
              <span className="text-xs text-slate-500">
                {new Date(summary.generated_at).toLocaleString()}
              </span>
            </div>

            <div className="space-y-3">
              {SUMMARY_KEYS.map((key) => (
                <SummarySection
                  key={key}
                  sectionKey={key}
                  content={(summary as any)[key] || "No data available."}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Report Export Result */}
      <AnimatePresence>
        {reportError && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-panel rounded-xl p-5 border border-red-500/30 bg-red-500/10 flex items-center gap-3 text-red-400 text-sm"
          >
            <AlertCircle size={18} /> {reportError}
          </motion.div>
        )}

        {reportResult && !reportLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-panel rounded-xl p-5 border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-between"
          >
            <div className="flex items-center gap-3 text-emerald-400">
              <CheckCircle size={18} />
              <span className="text-sm font-medium">Report generated successfully!</span>
            </div>
            {reportResult.download_url && (
              <a
                href={reportResult.download_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                <Download size={14} /> Download {format.toUpperCase()}
              </a>
            )}
            {reportResult.html_content && (
              <button
                onClick={() => {
                  const blob = new Blob([reportResult.html_content!], { type: "text/html" });
                  const url = URL.createObjectURL(blob);
                  window.open(url, "_blank");
                }}
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                <FileText size={14} /> View HTML
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
