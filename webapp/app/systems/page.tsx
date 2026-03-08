"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Search, Plus, Filter } from "lucide-react";
import RiskBadge from "@/components/RiskBadge";
import ErrorState from "@/components/ErrorState";
import { TableRowSkeleton } from "@/components/Skeleton";
import { useSystems } from "@/lib/hooks";
import type { RiskLevel, ComplianceStatus } from "@/lib/api";

const statusStyles: Record<ComplianceStatus, string> = {
  COMPLIANT: "text-green-400",
  NON_COMPLIANT: "text-red-400",
  REVIEW: "text-yellow-400",
};

const statusLabel: Record<ComplianceStatus, string> = {
  COMPLIANT: "Compliant",
  NON_COMPLIANT: "Non-Compliant",
  REVIEW: "In Review",
};

type FilterRisk = "ALL" | RiskLevel;
type FilterStatus = "ALL" | ComplianceStatus;

export default function SystemsPage() {
  const { data: systems, error, isLoading, mutate } = useSystems();
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState<FilterRisk>("ALL");
  const [statusFilter, setStatusFilter] = useState<FilterStatus>("ALL");

  const filtered = (systems ?? []).filter((s) => {
    const matchSearch =
      search === "" ||
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.type.toLowerCase().includes(search.toLowerCase()) ||
      s.department.toLowerCase().includes(search.toLowerCase());
    const matchRisk = riskFilter === "ALL" || s.risk === riskFilter;
    const matchStatus =
      statusFilter === "ALL" || s.status === statusFilter;
    return matchSearch && matchRisk && matchStatus;
  });

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="font-heading font-bold text-xl sm:text-2xl text-white">
            AI System Registry
          </h1>
          <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
            {systems ? `${systems.length} registered AI systems` : "Loading…"}
          </p>
        </motion.div>
        <motion.button
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          whileTap={{ scale: 0.95 }}
          whileHover={{ scale: 1.02 }}
          className="btn-pill btn-primary flex items-center gap-2 text-sm"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Register System</span>
        </motion.button>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="glass-card p-4 flex flex-wrap items-center gap-3"
      >
        {/* Search */}
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)]" />
          <input
            type="text"
            placeholder="Search systems…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search AI systems"
            className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>

        {/* Risk filter */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <Filter className="w-3.5 h-3.5 text-[rgb(115,115,115)]" aria-hidden="true" />
          {(["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"] as FilterRisk[]).map(
            (r) => (
              <button
                key={r}
                onClick={() => setRiskFilter(r)}
                aria-pressed={riskFilter === r}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  riskFilter === r
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05] border border-transparent"
                }`}
              >
                {r === "ALL" ? "All Risks" : r}
              </button>
            )
          )}
        </div>

        {/* Status filter */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {(
            ["ALL", "COMPLIANT", "NON_COMPLIANT", "REVIEW"] as FilterStatus[]
          ).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              aria-pressed={statusFilter === s}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                statusFilter === s
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05] border border-transparent"
              }`}
            >
              {s === "ALL"
                ? "All Statuses"
                : s === "NON_COMPLIANT"
                ? "Non-Compliant"
                : s === "REVIEW"
                ? "In Review"
                : "Compliant"}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.3 }}
        className="glass-card overflow-hidden"
      >
        {error ? (
          <ErrorState
            title="Could not load AI systems"
            onRetry={() => mutate()}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px]">
              <thead>
                <tr className="border-b border-white/[0.06]">
                  {[
                    "System",
                    "Type",
                    "Risk Level",
                    "Status",
                    "Score",
                    "Owner",
                    "Last Audit",
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
                  ? Array.from({ length: 6 }).map((_, i) => (
                      <TableRowSkeleton key={i} cols={8} />
                    ))
                  : filtered.map((sys, idx) => (
                      <motion.tr
                        key={sys.id}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{
                          delay: idx * 0.04,
                          duration: 0.25,
                        }}
                        className={`border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors ${
                          idx === filtered.length - 1 ? "border-b-0" : ""
                        }`}
                      >
                        <td className="px-4 py-3.5">
                          <div>
                            <p className="text-sm font-medium text-white">
                              {sys.name}
                            </p>
                            <p className="text-[11px] text-[rgb(115,115,115)]">
                              {sys.department}
                            </p>
                          </div>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className="text-xs text-[rgb(163,163,163)]">
                            {sys.type}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <RiskBadge level={sys.risk as RiskLevel} size="sm" />
                        </td>
                        <td className="px-4 py-3.5">
                          <span
                            className={`text-xs font-medium ${
                              statusStyles[sys.status as ComplianceStatus] ??
                              "text-[rgb(163,163,163)]"
                            }`}
                          >
                            {statusLabel[sys.status as ComplianceStatus] ??
                              sys.status}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                              <div
                                className="h-1.5 rounded-full"
                                style={{
                                  width: `${sys.complianceScore}%`,
                                  background:
                                    sys.complianceScore >= 80
                                      ? "#22c55e"
                                      : sys.complianceScore >= 60
                                      ? "#eab308"
                                      : "#ef4444",
                                }}
                              />
                            </div>
                            <span className="text-xs text-white font-medium">
                              {sys.complianceScore}%
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className="text-xs text-[rgb(163,163,163)]">
                            {sys.owner}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <span className="text-xs text-[rgb(163,163,163)]">
                            {sys.lastAudit}
                          </span>
                        </td>
                        <td className="px-4 py-3.5">
                          <Link
                            href={`/systems/${sys.id}`}
                            className="text-xs text-blue-400 hover:text-blue-300 font-medium transition-colors"
                          >
                            View →
                          </Link>
                        </td>
                      </motion.tr>
                    ))}
                {!isLoading && !error && filtered.length === 0 && (
                  <tr>
                    <td
                      colSpan={8}
                      className="px-4 py-12 text-center text-sm text-[rgb(115,115,115)]"
                    >
                      No systems match your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
