"use client";

import { useState, useRef } from "react";
import {
  ScanSearch,
  Upload,
  ChevronDown,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  Clock,
  BarChart3,
  FileUp,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────
type AuditStatus = "PASS" | "WARN" | "FAIL";

interface BiasMetric {
  name: string;
  description: string;
  value: number;
  threshold: { warn: number; fail: number };
  higherIsBetter: boolean;
  status: AuditStatus;
}

interface HistoricalAudit {
  id: string;
  system: string;
  runDate: string;
  overallStatus: AuditStatus;
  score: number;
  dataset: string;
}

// ── Constants ─────────────────────────────────────────────────────────────
const AI_SYSTEMS = [
  "Loan Approval Model",
  "HR Screening Tool",
  "Customer Analytics AI",
  "Content Moderation AI",
  "Fraud Detection System",
  "Pricing Optimization AI",
  "Recommendation Engine",
  "Churn Predictor",
];

const MOCK_METRICS: BiasMetric[] = [
  {
    name: "Demographic Parity",
    description: "Difference in positive prediction rates between demographic groups",
    value: 0.082,
    threshold: { warn: 0.1, fail: 0.2 },
    higherIsBetter: false,
    status: "PASS",
  },
  {
    name: "Disparate Impact Ratio",
    description:
      "Ratio of positive outcome rates between protected and reference groups (≥0.8 required)",
    value: 0.74,
    threshold: { warn: 0.8, fail: 0.6 },
    higherIsBetter: true,
    status: "WARN",
  },
  {
    name: "Equal Opportunity Difference",
    description: "Difference in true positive rates between demographic groups",
    value: 0.143,
    threshold: { warn: 0.1, fail: 0.2 },
    higherIsBetter: false,
    status: "WARN",
  },
  {
    name: "Average Odds Difference",
    description:
      "Average of true positive rate and false positive rate differences across groups",
    value: 0.065,
    threshold: { warn: 0.1, fail: 0.2 },
    higherIsBetter: false,
    status: "PASS",
  },
  {
    name: "Predictive Parity",
    description:
      "Difference in positive predictive values between demographic groups",
    value: 0.031,
    threshold: { warn: 0.05, fail: 0.1 },
    higherIsBetter: false,
    status: "PASS",
  },
  {
    name: "Theil Index",
    description: "Generalised entropy index measuring individual fairness across all groups",
    value: 0.19,
    threshold: { warn: 0.15, fail: 0.25 },
    higherIsBetter: false,
    status: "WARN",
  },
];

const HISTORICAL: HistoricalAudit[] = [
  {
    id: "AUD-012",
    system: "Loan Approval Model",
    runDate: "Feb 20, 2026",
    overallStatus: "WARN",
    score: 68,
    dataset: "Q1-2026-loan-apps.csv",
  },
  {
    id: "AUD-011",
    system: "HR Screening Tool",
    runDate: "Feb 15, 2026",
    overallStatus: "FAIL",
    score: 41,
    dataset: "candidates-jan-2026.csv",
  },
  {
    id: "AUD-010",
    system: "Customer Analytics AI",
    runDate: "Feb 10, 2026",
    overallStatus: "PASS",
    score: 92,
    dataset: "analytics-dataset-v3.parquet",
  },
  {
    id: "AUD-009",
    system: "Pricing Optimization AI",
    runDate: "Feb 5, 2026",
    overallStatus: "FAIL",
    score: 38,
    dataset: "pricing-feb-2026.csv",
  },
  {
    id: "AUD-008",
    system: "Fraud Detection System",
    runDate: "Jan 28, 2026",
    overallStatus: "PASS",
    score: 85,
    dataset: "fraud-dataset-q4-2025.csv",
  },
];

// ── Helpers ───────────────────────────────────────────────────────────────
function statusBadge(s: AuditStatus, size: "sm" | "md" = "sm") {
  const base =
    size === "sm"
      ? "text-[10px] px-2 py-0.5 rounded-full font-semibold flex items-center gap-1 w-fit"
      : "text-xs px-3 py-1 rounded-full font-bold flex items-center gap-1.5 w-fit";
  if (s === "PASS")
    return (
      <span className={`${base} bg-green-500/15 text-green-400 border border-green-500/25`}>
        <CheckCircle2 className={size === "sm" ? "w-3 h-3" : "w-4 h-4"} />
        PASS
      </span>
    );
  if (s === "WARN")
    return (
      <span className={`${base} bg-yellow-500/15 text-yellow-400 border border-yellow-500/25`}>
        <AlertTriangle className={size === "sm" ? "w-3 h-3" : "w-4 h-4"} />
        WARN
      </span>
    );
  return (
    <span className={`${base} bg-red-500/15 text-red-400 border border-red-500/25`}>
      <XCircle className={size === "sm" ? "w-3 h-3" : "w-4 h-4"} />
      FAIL
    </span>
  );
}

function MetricBar({ metric }: { metric: BiasMetric }) {
  // Normalise value for display (0-1 range)
  const maxScale = metric.threshold.fail * 1.5;
  const pct = metric.higherIsBetter
    ? (metric.value / 1) * 100
    : Math.min((metric.value / maxScale) * 100, 100);

  const barColor =
    metric.status === "PASS"
      ? "#22c55e"
      : metric.status === "WARN"
      ? "#eab308"
      : "#ef4444";

  return (
    <div className="glass-card p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white">{metric.name}</p>
          <p className="text-[11px] text-[rgb(163,163,163)] mt-0.5 leading-relaxed">
            {metric.description}
          </p>
        </div>
        {statusBadge(metric.status)}
      </div>

      <div className="flex items-center gap-3">
        <div className="flex-1 h-2 bg-white/[0.06] rounded-full overflow-hidden">
          <div
            className="h-2 rounded-full transition-all duration-700"
            style={{ width: `${pct}%`, background: barColor }}
          />
        </div>
        <span
          className="text-sm font-bold w-16 text-right"
          style={{ color: barColor }}
        >
          {metric.value.toFixed(3)}
        </span>
      </div>

      <div className="flex items-center gap-4 text-[10px] text-[rgb(115,115,115)]">
        <span>
          Warn threshold: {metric.higherIsBetter ? "≥" : "≤"}{" "}
          {metric.threshold.warn}
        </span>
        <span>
          Fail threshold: {metric.higherIsBetter ? "≥" : "≤"}{" "}
          {metric.threshold.fail}
        </span>
      </div>
    </div>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────
export default function BiasPage() {
  const [selectedSystem, setSelectedSystem] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const overallStatus: AuditStatus = showResults
    ? MOCK_METRICS.some((m) => m.status === "FAIL")
      ? "FAIL"
      : MOCK_METRICS.some((m) => m.status === "WARN")
      ? "WARN"
      : "PASS"
    : "PASS";

  const handleFile = (file: File) => {
    setUploadedFile(file.name);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const runAudit = () => {
    if (!selectedSystem || !uploadedFile) return;
    setRunning(true);
    setShowResults(false);
    setTimeout(() => {
      setRunning(false);
      setShowResults(true);
    }, 2800);
  };

  const passCount = MOCK_METRICS.filter((m) => m.status === "PASS").length;
  const warnCount = MOCK_METRICS.filter((m) => m.status === "WARN").length;
  const failCount = MOCK_METRICS.filter((m) => m.status === "FAIL").length;

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white">
          Bias Auditor
        </h1>
        <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
          Analyse AI systems for demographic bias and fairness metrics
        </p>
      </div>

      {/* Setup panel */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Upload */}
        <div className="glass-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <FileUp className="w-4 h-4 text-blue-400" />
            <h2 className="font-heading font-semibold text-white text-sm">
              Upload Dataset
            </h2>
          </div>

          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              dragOver
                ? "border-blue-500/60 bg-blue-500/10"
                : uploadedFile
                ? "border-green-500/40 bg-green-500/05"
                : "border-white/[0.10] hover:border-white/[0.20] hover:bg-white/[0.03]"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.parquet,.json"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />
            {uploadedFile ? (
              <div className="space-y-1">
                <CheckCircle2 className="w-8 h-8 text-green-400 mx-auto" />
                <p className="text-sm font-medium text-white">{uploadedFile}</p>
                <p className="text-xs text-[rgb(163,163,163)]">
                  Click to replace
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-8 h-8 text-[rgb(115,115,115)] mx-auto" />
                <p className="text-sm font-medium text-white">
                  Drop dataset here
                </p>
                <p className="text-xs text-[rgb(163,163,163)]">
                  Supports CSV, Parquet, JSON · max 500 MB
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Config */}
        <div className="glass-card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <ScanSearch className="w-4 h-4 text-purple-400" />
            <h2 className="font-heading font-semibold text-white text-sm">
              Audit Configuration
            </h2>
          </div>

          {/* System select */}
          <div>
            <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
              Select AI System
            </label>
            <div className="relative">
              <select
                value={selectedSystem}
                onChange={(e) => setSelectedSystem(e.target.value)}
                className="w-full appearance-none bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-colors pr-8"
              >
                <option value="" disabled className="bg-[rgb(10,10,10)]">
                  Choose a system to audit
                </option>
                {AI_SYSTEMS.map((s) => (
                  <option key={s} value={s} className="bg-[rgb(10,10,10)]">
                    {s}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)] pointer-events-none" />
            </div>
          </div>

          {/* Metrics checkboxes */}
          <div>
            <label className="text-xs font-medium text-[rgb(163,163,163)] mb-2 block">
              Metrics to Compute
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {[
                "Demographic Parity",
                "Disparate Impact",
                "Equal Opportunity",
                "Average Odds",
                "Predictive Parity",
                "Theil Index",
              ].map((m) => (
                <label
                  key={m}
                  className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/[0.04] cursor-pointer"
                >
                  <input
                    type="checkbox"
                    defaultChecked
                    className="accent-blue-500 w-3.5 h-3.5"
                  />
                  <span className="text-xs text-[rgb(163,163,163)]">{m}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={runAudit}
            disabled={!selectedSystem || !uploadedFile || running}
            className="w-full btn-pill btn-primary text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {running ? (
              <>
                <ScanSearch className="w-4 h-4 animate-pulse" />
                Running Audit…
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Run Bias Audit
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results */}
      {showResults && (
        <div className="space-y-4">
          {/* Overall result */}
          <div className="glass-card p-5 flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-yellow-500/15 border border-yellow-500/25 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-yellow-400" />
              </div>
              <div>
                <p className="text-xs text-[rgb(163,163,163)] mb-1">
                  Audit result for{" "}
                  <span className="text-white font-medium">{selectedSystem}</span>
                </p>
                <div className="flex items-center gap-3">
                  {statusBadge(overallStatus, "md")}
                  <span className="text-[rgb(115,115,115)] text-xs">
                    {passCount} pass · {warnCount} warn · {failCount} fail
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="font-heading font-black text-4xl text-yellow-400">
                68
              </p>
              <p className="text-xs text-[rgb(163,163,163)]">Fairness Score</p>
            </div>
          </div>

          {/* Metric cards */}
          <h2 className="font-heading font-semibold text-white text-sm">
            Metric Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {MOCK_METRICS.map((m) => (
              <MetricBar key={m.name} metric={m} />
            ))}
          </div>
        </div>
      )}

      {/* Historical audits */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-4 h-4 text-[rgb(163,163,163)]" />
          <h2 className="font-heading font-semibold text-white text-sm">
            Historical Audits
          </h2>
        </div>

        <div className="glass-card overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/[0.06]">
                {["Audit ID", "System", "Dataset", "Run Date", "Score", "Result"].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-[10px] font-semibold text-[rgb(115,115,115)] uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {HISTORICAL.map((audit, idx) => (
                <tr
                  key={audit.id}
                  className={`border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors ${
                    idx === HISTORICAL.length - 1 ? "border-b-0" : ""
                  }`}
                >
                  <td className="px-4 py-3.5">
                    <span className="text-xs font-mono text-blue-400">
                      {audit.id}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-sm font-medium text-white">
                      {audit.system}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs text-[rgb(163,163,163)] font-mono">
                      {audit.dataset}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs text-[rgb(163,163,163)]">
                      {audit.runDate}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className="text-sm font-bold"
                      style={{
                        color:
                          audit.score >= 80
                            ? "#22c55e"
                            : audit.score >= 60
                            ? "#eab308"
                            : "#ef4444",
                      }}
                    >
                      {audit.score}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    {statusBadge(audit.overallStatus)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
