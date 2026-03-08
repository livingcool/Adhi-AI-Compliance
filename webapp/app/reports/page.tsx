"use client";

import { useState } from "react";
import {
  BarChart3,
  ClipboardList,
  Scale,
  FileCode2,
  TrendingUp,
  Download,
  RefreshCw,
  CheckCircle2,
  Clock,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { GlassCard } from '@/components/ui/GlassCard';

// ── Types ─────────────────────────────────────────────────────────────────
type ReportStatus = "READY" | "GENERATING" | "DONE";

interface ReportType {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  iconColor: string;
  iconBg: string;
  accentBorder: string;
  lastGenerated?: string;
  estimatedTime: string;
}

interface RecentReport {
  id: string;
  name: string;
  type: string;
  generatedAt: string;
  size: string;
  status: "COMPLETE" | "FAILED";
}

// ── Report type definitions ───────────────────────────────────────────────
const REPORT_TYPES: ReportType[] = [
  {
    id: "audit",
    title: "Compliance Audit Report",
    description:
      "Full compliance posture across all registered AI systems. Includes regulation mapping, gap analysis, and remediation priorities.",
    icon: ClipboardList,
    iconColor: "text-blue-400",
    iconBg: "bg-blue-500/15",
    accentBorder: "border-l-blue-500/50",
    lastGenerated: "Feb 20, 2026",
    estimatedTime: "~45 sec",
  },
  {
    id: "bias",
    title: "Bias & Fairness Report",
    description:
      "Demographic parity, disparate impact, and equalised odds metrics across all AI systems with historical trend analysis.",
    icon: Scale,
    iconColor: "text-purple-400",
    iconBg: "bg-purple-500/15",
    accentBorder: "border-l-purple-500/50",
    lastGenerated: "Feb 18, 2026",
    estimatedTime: "~30 sec",
  },
  {
    id: "model-card",
    title: "Model Card Bundle",
    description:
      "Auto-generated model cards for all registered AI systems following Google Model Card and EU AI Act Annex IV documentation standards.",
    icon: FileCode2,
    iconColor: "text-green-400",
    iconBg: "bg-green-500/15",
    accentBorder: "border-l-green-500/50",
    lastGenerated: "Feb 15, 2026",
    estimatedTime: "~1 min",
  },
  {
    id: "gap",
    title: "Gap Analysis Report",
    description:
      "Identifies compliance gaps against selected regulatory frameworks (EU AI Act, GDPR, NIST AI RMF) with actionable remediation steps.",
    icon: TrendingUp,
    iconColor: "text-orange-400",
    iconBg: "bg-orange-500/15",
    accentBorder: "border-l-orange-500/50",
    lastGenerated: "Feb 10, 2026",
    estimatedTime: "~50 sec",
  },
];

const RECENT_REPORTS: RecentReport[] = [
  {
    id: "RPT-024",
    name: "Compliance Audit — Feb 2026",
    type: "Audit",
    generatedAt: "Feb 20, 2026 14:32",
    size: "2.4 MB",
    status: "COMPLETE",
  },
  {
    id: "RPT-023",
    name: "Bias & Fairness — Feb 2026",
    type: "Bias",
    generatedAt: "Feb 18, 2026 09:15",
    size: "1.1 MB",
    status: "COMPLETE",
  },
  {
    id: "RPT-022",
    name: "Model Card Bundle — Feb 2026",
    type: "Model Card",
    generatedAt: "Feb 15, 2026 16:48",
    size: "3.8 MB",
    status: "COMPLETE",
  },
  {
    id: "RPT-021",
    name: "Gap Analysis — GDPR Focus",
    type: "Gap Analysis",
    generatedAt: "Feb 10, 2026 11:20",
    size: "0.9 MB",
    status: "COMPLETE",
  },
  {
    id: "RPT-020",
    name: "Compliance Audit — Jan 2026",
    type: "Audit",
    generatedAt: "Jan 31, 2026 10:05",
    size: "2.1 MB",
    status: "COMPLETE",
  },
  {
    id: "RPT-019",
    name: "Gap Analysis — EU AI Act Focus",
    type: "Gap Analysis",
    generatedAt: "Jan 25, 2026 14:00",
    size: "1.2 MB",
    status: "FAILED",
  },
];

// ── Report card ───────────────────────────────────────────────────────────
function ReportCard({ report }: { report: ReportType }) {
  const [status, setStatus] = useState<ReportStatus>("READY");
  const Icon = report.icon;

  const generate = () => {
    if (status === "GENERATING") return;
    setStatus("GENERATING");
    setTimeout(() => setStatus("DONE"), 3000);
  };

  return (
    <GlassCard className={`p-5 border-l-4 ${report.accentBorder} flex flex-col gap-4`}>
      <div className="flex items-start gap-3">
        <div
          className={`w-10 h-10 rounded-xl ${report.iconBg} flex items-center justify-center flex-shrink-0`}
        >
          <Icon className={`w-5 h-5 ${report.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-heading font-bold text-white text-sm">
            {report.title}
          </h3>
          <p className="text-xs text-[rgb(163,163,163)] mt-1 leading-relaxed">
            {report.description}
          </p>
        </div>
      </div>

      <div className="flex items-center justify-between text-[10px] text-[rgb(115,115,115)]">
        <span>
          {report.lastGenerated
            ? `Last: ${report.lastGenerated}`
            : "Never generated"}
        </span>
        <span>{report.estimatedTime}</span>
      </div>

      <div className="flex items-center gap-2">
        {status === "DONE" ? (
          <>
            <button className="flex-1 btn-pill btn-ghost text-xs flex items-center justify-center gap-1.5">
              <Download className="w-3.5 h-3.5" />
              Download PDF
            </button>
            <button
              onClick={() => setStatus("READY")}
              className="flex-shrink-0 w-9 h-9 rounded-xl glass border border-white/[0.08] flex items-center justify-center hover:bg-white/[0.08] transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5 text-[rgb(163,163,163)]" />
            </button>
          </>
        ) : (
          <button
            onClick={generate}
            disabled={status === "GENERATING"}
            className="w-full btn-pill btn-primary text-xs flex items-center justify-center gap-2 disabled:opacity-70"
          >
            {status === "GENERATING" ? (
              <>
                <Sparkles className="w-3.5 h-3.5 animate-spin" />
                Generating…
              </>
            ) : (
              <>
                <BarChart3 className="w-3.5 h-3.5" />
                Generate Report
              </>
            )}
          </button>
        )}
      </div>
    </GlassCard>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────
export default function ReportsPage() {
  return (
    <div className="p-6 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-heading font-bold text-2xl text-white">
          Reports Centre
        </h1>
        <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
          Generate and download compliance reports for your AI systems
        </p>
      </div>

      {/* Report type cards */}
      <div>
        <h2 className="font-heading font-semibold text-white text-sm mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          Generate Report
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {REPORT_TYPES.map((r) => (
            <ReportCard key={r.id} report={r} />
          ))}
        </div>
      </div>

      {/* Recent reports */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading font-semibold text-white text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-[rgb(163,163,163)]" />
            Recent Reports
          </h2>
          <button className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-0.5 transition-colors">
            View all <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        <GlassCard className="overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/[0.06]">
                {["Report ID", "Name", "Type", "Generated", "Size", "Status", ""].map(
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
              {RECENT_REPORTS.map((r, idx) => (
                <tr
                  key={r.id}
                  className={`border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors ${idx === RECENT_REPORTS.length - 1 ? "border-b-0" : ""
                    }`}
                >
                  <td className="px-4 py-3.5">
                    <span className="text-xs font-mono text-blue-400">{r.id}</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <p className="text-sm font-medium text-white">{r.name}</p>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs text-[rgb(163,163,163)]">{r.type}</span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs text-[rgb(163,163,163)]">
                      {r.generatedAt}
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className="text-xs text-[rgb(163,163,163)]">{r.size}</span>
                  </td>
                  <td className="px-4 py-3.5">
                    {r.status === "COMPLETE" ? (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/15 text-green-400 border border-green-500/20 flex items-center gap-1 w-fit font-medium">
                        <CheckCircle2 className="w-3 h-3" />
                        Complete
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 border border-red-500/20 w-fit font-medium block">
                        Failed
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3.5">
                    {r.status === "COMPLETE" && (
                      <button className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition-colors">
                        <Download className="w-3.5 h-3.5" />
                        Download
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </GlassCard>
      </div>
    </div>
  );
}
