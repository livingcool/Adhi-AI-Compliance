"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Plus,
  X,
  Search,
  ChevronDown,
  Clock,
  CheckCircle2,
  ShieldAlert,
  Eye,
} from "lucide-react";
import ErrorState from "@/components/ErrorState";
import { StatCardSkeleton, TableRowSkeleton } from "@/components/Skeleton";
import { useIncidents } from "@/lib/hooks";
import { getAuthHeaders } from "@/lib/auth";
import type { RiskLevel } from "@/lib/api";
import { GlassCard } from '@/components/ui/GlassCard';

// ── Types ─────────────────────────────────────────────────────────────────
type IncidentStatus = "INVESTIGATING" | "MITIGATING" | "RESOLVED" | "CLOSED";

interface Incident {
  id: string;
  title: string;
  system: string;
  severity: RiskLevel;
  status: IncidentStatus;
  reportedBy: string;
  createdAt: string;
  updatedAt: string;
  description: string;
  affectedUsers?: number;
}

// ── Style maps ────────────────────────────────────────────────────────────
const SEVERITY_STYLES: Record<RiskLevel, string> = {
  CRITICAL: "bg-red-500/15 text-red-400 border border-red-500/25",
  HIGH: "bg-orange-500/15 text-orange-400 border border-orange-500/25",
  MEDIUM: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/25",
  LOW: "bg-green-500/15 text-green-400 border border-green-500/25",
};

const STATUS_STYLES: Record<IncidentStatus, string> = {
  INVESTIGATING: "bg-red-500/10 text-red-300 border border-red-500/20",
  MITIGATING: "bg-orange-500/10 text-orange-300 border border-orange-500/20",
  RESOLVED: "bg-green-500/10 text-green-300 border border-green-500/20",
  CLOSED: "bg-white/[0.05] text-[rgb(115,115,115)] border border-white/[0.08]",
};

const STATUS_ICONS: Record<IncidentStatus, React.ElementType> = {
  INVESTIGATING: ShieldAlert,
  MITIGATING: Clock,
  RESOLVED: CheckCircle2,
  CLOSED: CheckCircle2,
};

// ── AI Systems for the form ───────────────────────────────────────────────
const AI_SYSTEMS = [
  "Customer Analytics AI",
  "Loan Approval Model",
  "HR Screening Tool",
  "Content Moderation AI",
  "Fraud Detection System",
  "Recommendation Engine",
  "Churn Predictor",
  "Pricing Optimization AI",
];

// ── Report Incident Modal ─────────────────────────────────────────────────
function ReportModal({
  onClose,
  onSuccess,
}: {
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [form, setForm] = useState({
    title: "",
    system: "",
    severity: "MEDIUM" as RiskLevel,
    description: "",
    reportedBy: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [err, setErr] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setErr("");
    try {
      const res = await fetch("/api/v1/incidents", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          title: form.title,
          system: form.system,
          severity: form.severity,
          description: form.description,
          reportedBy: form.reportedBy,
          status: "INVESTIGATING",
        }),
      });
      if (!res.ok) throw new Error("Failed to submit");
      setSubmitted(true);
      onSuccess();
      setTimeout(onClose, 1800);
    } catch {
      setErr("Failed to submit incident. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Report incident"
    >
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      <motion.div
        initial={{ scale: 0.95, y: 16 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.95, y: 16 }}
        transition={{ type: "spring", stiffness: 300, damping: 28 }}
        className="relative w-full max-w-lg z-10"
      >
        <GlassCard className="p-6 space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center">
                <AlertTriangle className="w-4 h-4 text-red-400" />
              </div>
              <div>
                <h2 className="font-heading font-bold text-white text-base">
                  Report Incident
                </h2>
                <p className="text-xs text-[rgb(163,163,163)]">
                  Log a new compliance incident
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              aria-label="Close modal"
              className="w-7 h-7 rounded-lg hover:bg-white/[0.06] flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-[rgb(163,163,163)]" />
            </button>
          </div>

          {submitted ? (
            <div className="py-8 text-center space-y-2">
              <CheckCircle2 className="w-10 h-10 text-green-400 mx-auto" />
              <p className="font-heading font-semibold text-white">
                Incident Reported
              </p>
              <p className="text-xs text-[rgb(163,163,163)]">
                The incident has been logged and assigned an ID.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {err && (
                <p className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-3 py-2">
                  {err}
                </p>
              )}
              <div>
                <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
                  Incident Title *
                </label>
                <input
                  required
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  placeholder="Brief description of the incident"
                  className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
                    Affected System *
                  </label>
                  <div className="relative">
                    <select
                      required
                      value={form.system}
                      onChange={(e) =>
                        setForm({ ...form, system: e.target.value })
                      }
                      className="w-full appearance-none bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-colors pr-8"
                    >
                      <option value="" disabled className="bg-[rgb(10,10,10)]">
                        Select system
                      </option>
                      {AI_SYSTEMS.map((s) => (
                        <option key={s} value={s} className="bg-[rgb(10,10,10)]">
                          {s}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)] pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
                    Severity *
                  </label>
                  <div className="relative">
                    <select
                      value={form.severity}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          severity: e.target.value as RiskLevel,
                        })
                      }
                      className="w-full appearance-none bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500/50 transition-colors pr-8"
                    >
                      {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as RiskLevel[]).map(
                        (s) => (
                          <option
                            key={s}
                            value={s}
                            className="bg-[rgb(10,10,10)]"
                          >
                            {s}
                          </option>
                        )
                      )}
                    </select>
                    <ChevronDown className="absolute right-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)] pointer-events-none" />
                  </div>
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
                  Reported By *
                </label>
                <input
                  required
                  value={form.reportedBy}
                  onChange={(e) =>
                    setForm({ ...form, reportedBy: e.target.value })
                  }
                  placeholder="Team or person reporting this"
                  className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-[rgb(163,163,163)] mb-1.5 block">
                  Description *
                </label>
                <textarea
                  required
                  rows={3}
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                  placeholder="Describe what happened, impact, and any immediate actions taken…"
                  className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl px-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors resize-none leading-relaxed"
                />
              </div>
              <div className="flex gap-3 pt-1">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 btn-pill btn-ghost text-sm"
                >
                  Cancel
                </button>
                <motion.button
                  whileTap={{ scale: 0.96 }}
                  type="submit"
                  disabled={submitting}
                  className="flex-1 btn-pill btn-primary text-sm disabled:opacity-60"
                >
                  {submitting ? "Submitting…" : "Submit Incident"}
                </motion.button>
              </div>
            </form>
          )}
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}

// ── Detail Drawer ─────────────────────────────────────────────────────────
function IncidentDetail({
  incident,
  onClose,
}: {
  incident: Incident;
  onClose: () => void;
}) {
  const StatusIcon = STATUS_ICONS[incident.status] ?? ShieldAlert;
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex justify-end"
      role="dialog"
      aria-modal="true"
      aria-label="Incident details"
    >
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />
      <motion.div
        initial={{ x: "100%" }}
        animate={{ x: 0 }}
        exit={{ x: "100%" }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="relative w-full max-w-md h-full flex flex-col z-10 border-l border-white/[0.08]"
      >
        <GlassCard className="h-full flex flex-col rounded-none">
          <div className="px-6 py-5 border-b border-white/[0.06] flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2">
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${SEVERITY_STYLES[incident.severity]}`}
                >
                  {incident.severity}
                </span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-medium flex items-center gap-1 ${STATUS_STYLES[incident.status]}`}
                >
                  <StatusIcon className="w-3 h-3" />
                  {incident.status}
                </span>
              </div>
              <p className="text-[10px] text-blue-400 font-mono mb-1">
                {incident.id}
              </p>
              <h2 className="font-heading font-bold text-white text-sm leading-snug">
                {incident.title}
              </h2>
            </div>
            <button
              onClick={onClose}
              aria-label="Close drawer"
              className="flex-shrink-0 w-7 h-7 rounded-lg hover:bg-white/[0.06] flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-[rgb(163,163,163)]" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "System", value: incident.system },
                { label: "Reported By", value: incident.reportedBy },
                { label: "Created", value: incident.createdAt },
                { label: "Last Updated", value: incident.updatedAt },
                ...(incident.affectedUsers
                  ? [
                    {
                      label: "Affected Users",
                      value: incident.affectedUsers.toLocaleString(),
                    },
                  ]
                  : []),
              ].map((item) => (
                <GlassCard key={item.label} className="p-3">
                  <p className="text-[10px] text-[rgb(115,115,115)] uppercase tracking-wider mb-1">
                    {item.label}
                  </p>
                  <p className="text-xs text-white font-medium">{item.value}</p>
                </GlassCard>
              ))}
            </div>

            <div>
              <p className="text-xs font-semibold text-[rgb(163,163,163)] uppercase tracking-wider mb-2">
                Description
              </p>
              <p className="text-sm text-white/80 leading-relaxed">
                {incident.description}
              </p>
            </div>

            <div>
              <p className="text-xs font-semibold text-[rgb(163,163,163)] uppercase tracking-wider mb-3">
                Timeline
              </p>
              <div className="space-y-3">
                {[
                  {
                    label: "Incident reported",
                    time: incident.createdAt,
                    dot: "bg-red-400",
                  },
                  {
                    label: "Assigned to compliance team",
                    time: incident.createdAt,
                    dot: "bg-orange-400",
                  },
                  {
                    label: "Status updated",
                    time: incident.updatedAt,
                    dot: "bg-blue-400",
                  },
                ].map((t, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="flex flex-col items-center mt-1 flex-shrink-0">
                      <div className={`w-2 h-2 rounded-full ${t.dot}`} />
                      {i < 2 && <div className="w-px h-4 bg-white/[0.06] mt-1" />}
                    </div>
                    <div>
                      <p className="text-xs text-white">{t.label}</p>
                      <p className="text-[10px] text-[rgb(115,115,115)]">
                        {t.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="px-6 py-4 border-t border-white/[0.06] flex gap-3">
            <button className="flex-1 btn-pill btn-ghost text-xs">
              Escalate
            </button>
            <button className="flex-1 btn-pill btn-primary text-xs">
              Update Status
            </button>
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────
export default function IncidentsPage() {
  const { data: rawIncidents, error, isLoading, mutate } = useIncidents();
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState<"ALL" | RiskLevel>("ALL");
  const [statusFilter, setStatusFilter] = useState<"ALL" | IncidentStatus>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState<Incident | null>(null);

  // Cast API data to local Incident type
  const incidents: Incident[] = (rawIncidents ?? []).map((inc) => ({
    id: inc.id,
    title: inc.title,
    system: inc.system,
    severity: inc.severity as RiskLevel,
    status: (inc.status as IncidentStatus) ?? "INVESTIGATING",
    reportedBy: "Compliance Team",
    createdAt: inc.createdAt,
    updatedAt: inc.resolvedAt ?? inc.createdAt,
    description: inc.description,
  }));

  const filtered = incidents.filter((inc) => {
    const matchSearch =
      search === "" ||
      inc.title.toLowerCase().includes(search.toLowerCase()) ||
      inc.system.toLowerCase().includes(search.toLowerCase()) ||
      inc.id.toLowerCase().includes(search.toLowerCase());
    const matchSeverity =
      severityFilter === "ALL" || inc.severity === severityFilter;
    const matchStatus =
      statusFilter === "ALL" || inc.status === statusFilter;
    return matchSearch && matchSeverity && matchStatus;
  });

  const openCount = incidents.filter(
    (i) => i.status === "INVESTIGATING" || i.status === "MITIGATING"
  ).length;
  const criticalCount = incidents.filter(
    (i) => i.severity === "CRITICAL"
  ).length;

  const summaryCards = [
    {
      label: "Total",
      value: incidents.length,
      color: "text-white",
      bg: "bg-white/[0.06]",
    },
    {
      label: "Investigating",
      value: incidents.filter((i) => i.status === "INVESTIGATING").length,
      color: "text-red-400",
      bg: "bg-red-500/10",
    },
    {
      label: "Mitigating",
      value: incidents.filter((i) => i.status === "MITIGATING").length,
      color: "text-orange-400",
      bg: "bg-orange-500/10",
    },
    {
      label: "Resolved",
      value: incidents.filter(
        (i) => i.status === "RESOLVED" || i.status === "CLOSED"
      ).length,
      color: "text-green-400",
      bg: "bg-green-500/10",
    },
  ];

  return (
    <>
      <AnimatePresence>
        {showModal && (
          <ReportModal
            onClose={() => setShowModal(false)}
            onSuccess={() => mutate()}
          />
        )}
        {selected && (
          <IncidentDetail
            incident={selected}
            onClose={() => setSelected(null)}
          />
        )}
      </AnimatePresence>

      <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h1 className="font-heading font-bold text-xl sm:text-2xl text-white">
              Incident Management
            </h1>
            <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
              {isLoading
                ? "Loading…"
                : `${openCount} open incidents · ${criticalCount} critical`}
            </p>
          </motion.div>
          <motion.button
            initial={{ opacity: 0, x: 12 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
            whileTap={{ scale: 0.95 }}
            whileHover={{ scale: 1.02 }}
            onClick={() => setShowModal(true)}
            className="btn-pill btn-primary flex items-center gap-2 text-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Report Incident</span>
          </motion.button>
        </div>

        {/* Summary cards */}
        {isLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[0, 1, 2, 3].map((i) => (
              <StatCardSkeleton key={i} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {summaryCards.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06, duration: 0.3 }}
              >
                <GlassCard className="p-4">
                  <p className={`font-heading font-bold text-3xl ${s.color}`}>
                    {s.value}
                  </p>
                  <p className="text-xs text-[rgb(163,163,163)] mt-0.5">
                    {s.label}
                  </p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        )}

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.3 }}
        >
          <GlassCard className="p-4 flex flex-wrap items-center gap-3">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)]" />
              <input
                type="text"
                placeholder="Search incidents…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                aria-label="Search incidents"
                className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors"
              />
            </div>

            <div className="flex items-center gap-1.5 flex-wrap">
              {(["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map(
                (s) => (
                  <button
                    key={s}
                    onClick={() => setSeverityFilter(s)}
                    aria-pressed={severityFilter === s}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${severityFilter === s
                      ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                      : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05] border border-transparent"
                      }`}
                  >
                    {s === "ALL" ? "All" : s}
                  </button>
                )
              )}
            </div>

            <div className="flex items-center gap-1.5 flex-wrap">
              {(
                [
                  "ALL",
                  "INVESTIGATING",
                  "MITIGATING",
                  "RESOLVED",
                  "CLOSED",
                ] as const
              ).map((s) => (
                <button
                  key={s}
                  onClick={() => setStatusFilter(s)}
                  aria-pressed={statusFilter === s}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${statusFilter === s
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05] border border-transparent"
                    }`}
                >
                  {s === "ALL" ? "All Status" : s}
                </button>
              ))}
            </div>
          </GlassCard>
        </motion.div>

        {/* Table */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="glass-card overflow-hidden"
        >
          {error ? (
            <ErrorState
              title="Could not load incidents"
              onRetry={() => mutate()}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[800px]">
                <thead>
                  <tr className="border-b border-white/[0.06]">
                    {[
                      "ID",
                      "Incident",
                      "System",
                      "Severity",
                      "Status",
                      "Reported",
                      "Updated",
                      "",
                    ].map((h) => (
                      <th
                        key={h}
                        scope="col"
                        className="px-4 py-3 text-left text-[10px] font-semibold text-[rgb(115,115,115)] uppercase tracking-wider"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {isLoading
                    ? Array.from({ length: 5 }).map((_, i) => (
                      <TableRowSkeleton key={i} cols={8} />
                    ))
                    : filtered.map((inc, idx) => {
                      const StatusIcon =
                        STATUS_ICONS[inc.status] ?? ShieldAlert;
                      const isCritical = inc.severity === "CRITICAL";
                      return (
                        <motion.tr
                          key={inc.id}
                          initial={{ opacity: 0, y: 6 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.04, duration: 0.25 }}
                          onClick={() => setSelected(inc)}
                          className={`border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors cursor-pointer ${idx === filtered.length - 1 ? "border-b-0" : ""
                            }`}
                        >
                          <td className="px-4 py-3.5">
                            <span className="text-xs font-mono text-blue-400">
                              {inc.id}
                            </span>
                          </td>
                          <td className="px-4 py-3.5 max-w-xs">
                            <p className="text-sm font-medium text-white line-clamp-2 leading-snug">
                              {inc.title}
                            </p>
                            {inc.affectedUsers && (
                              <p className="text-[10px] text-[rgb(115,115,115)] mt-0.5">
                                {inc.affectedUsers.toLocaleString()} users
                                affected
                              </p>
                            )}
                          </td>
                          <td className="px-4 py-3.5">
                            <span className="text-xs text-[rgb(163,163,163)]">
                              {inc.system}
                            </span>
                          </td>
                          <td className="px-4 py-3.5">
                            <span
                              className={`text-[10px] px-2.5 py-1 rounded-full font-semibold inline-flex items-center gap-1 ${SEVERITY_STYLES[inc.severity]}`}
                            >
                              {isCritical && (
                                <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
                              )}
                              {inc.severity}
                            </span>
                          </td>
                          <td className="px-4 py-3.5">
                            <span
                              className={`text-[10px] px-2.5 py-1 rounded-full font-medium flex items-center gap-1 w-fit ${STATUS_STYLES[inc.status]}`}
                            >
                              <StatusIcon className="w-3 h-3" />
                              {inc.status}
                            </span>
                          </td>
                          <td className="px-4 py-3.5">
                            <span className="text-xs text-[rgb(163,163,163)]">
                              {inc.createdAt}
                            </span>
                          </td>
                          <td className="px-4 py-3.5">
                            <span className="text-xs text-[rgb(163,163,163)]">
                              {inc.updatedAt}
                            </span>
                          </td>
                          <td className="px-4 py-3.5">
                            <button className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition-colors">
                              <Eye className="w-3.5 h-3.5" />
                              View
                            </button>
                          </td>
                        </motion.tr>
                      );
                    })}
                  {!isLoading && !error && filtered.length === 0 && (
                    <tr>
                      <td
                        colSpan={8}
                        className="px-4 py-12 text-center text-sm text-[rgb(115,115,115)]"
                      >
                        No incidents match your filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </div>
    </>
  );
}
