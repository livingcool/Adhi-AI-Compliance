"use client";

import { use } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  AlertCircle,
  Building2,
  Calendar,
  User,
} from "lucide-react";
import RiskBadge from "@/components/RiskBadge";
import ComplianceScore from "@/components/ComplianceScore";
import ErrorState from "@/components/ErrorState";
import { Skeleton, CardSkeleton } from "@/components/Skeleton";
import { useSystem } from "@/lib/hooks";
import type { RiskLevel, ComplianceStatus } from "@/lib/api";

const statusLabel: Record<ComplianceStatus, string> = {
  COMPLIANT: "Compliant",
  NON_COMPLIANT: "Non-Compliant",
  REVIEW: "Under Review",
};

const statusColor: Record<ComplianceStatus, string> = {
  COMPLIANT: "text-green-400",
  NON_COMPLIANT: "text-red-400",
  REVIEW: "text-yellow-400",
};

export default function SystemDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: system, error, isLoading, mutate } = useSystem(id);

  const checklist = system?.checklistItems ?? [];
  const completed = checklist.filter((c) => c.completed).length;
  const total = checklist.length;

  return (
    <div className="p-4 sm:p-6 max-w-5xl mx-auto space-y-6">
      {/* Back link */}
      <motion.div
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.25 }}
      >
        <Link
          href="/systems"
          className="inline-flex items-center gap-1.5 text-sm text-[rgb(163,163,163)] hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          AI System Registry
        </Link>
      </motion.div>

      {error ? (
        <ErrorState
          title="Could not load system details"
          onRetry={() => mutate()}
        />
      ) : isLoading || !system ? (
        <>
          <div className="glass-card p-6 space-y-4">
            <div className="flex justify-between">
              <div className="space-y-2 flex-1">
                <Skeleton className="w-64 h-7 rounded" />
                <Skeleton className="w-40 h-4 rounded" />
                <Skeleton className="w-full h-3.5 rounded" />
                <Skeleton className="w-3/4 h-3.5 rounded" />
              </div>
              <Skeleton className="w-24 h-24 rounded-full flex-shrink-0" />
            </div>
            <div className="grid grid-cols-4 gap-4 pt-4 border-t border-white/[0.06]">
              {[0, 1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-10 rounded" />
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-2">
              <CardSkeleton lines={6} />
            </div>
            <CardSkeleton lines={4} />
          </div>
        </>
      ) : (
        <>
          {/* Header card */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="glass-card p-6"
          >
            <div className="flex items-start justify-between flex-wrap gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 flex-wrap mb-1">
                  <h1 className="font-heading font-bold text-2xl text-white">
                    {system.name}
                  </h1>
                  <RiskBadge level={system.risk as RiskLevel} />
                </div>
                <p className="text-sm text-[rgb(163,163,163)]">{system.type}</p>
                <p className="text-sm text-[rgb(163,163,163)] mt-2 max-w-2xl leading-relaxed">
                  {system.description}
                </p>
              </div>
              <ComplianceScore score={system.complianceScore} size={100} />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5 pt-5 border-t border-white/[0.06]">
              {[
                { icon: User, label: "Owner", value: system.owner },
                { icon: Building2, label: "Department", value: system.department },
                { icon: Calendar, label: "Last Audit", value: system.lastAudit },
                { icon: Calendar, label: "Next Audit", value: system.nextAudit },
              ].map((meta) => (
                <div key={meta.label} className="flex items-start gap-2">
                  <meta.icon className="w-3.5 h-3.5 text-[rgb(115,115,115)] mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-[10px] text-[rgb(115,115,115)] uppercase tracking-wider font-medium">
                      {meta.label}
                    </p>
                    <p className="text-xs text-white font-medium mt-0.5">
                      {meta.value}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 mt-4">
              <span
                className={`text-sm font-semibold ${
                  statusColor[system.status as ComplianceStatus] ?? "text-[rgb(163,163,163)]"
                }`}
              >
                {statusLabel[system.status as ComplianceStatus] ?? system.status}
              </span>
              <span className="text-[rgb(115,115,115)] text-xs">·</span>
              <span className="text-xs text-[rgb(163,163,163)]">
                {completed}/{total} checklist items complete
              </span>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Compliance checklist */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.3 }}
              className="glass-card p-6 md:col-span-2"
            >
              <h2 className="font-heading font-bold text-white text-sm mb-4">
                Compliance Checklist
              </h2>
              <div className="space-y-2">
                {checklist.map((item, i) => (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.05, duration: 0.25 }}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-colors ${
                      item.completed
                        ? "border-green-500/15 bg-green-500/[0.04]"
                        : item.required
                        ? "border-red-500/15 bg-red-500/[0.04]"
                        : "border-white/[0.06] bg-white/[0.02]"
                    }`}
                  >
                    {item.completed ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{
                          delay: 0.2 + i * 0.05,
                          type: "spring",
                          stiffness: 300,
                        }}
                      >
                        <CheckCircle2 className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                      </motion.div>
                    ) : item.required ? (
                      <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <Circle className="w-4 h-4 text-[rgb(115,115,115)] flex-shrink-0 mt-0.5" />
                    )}
                    <div className="flex-1 min-w-0">
                      <p
                        className={`text-xs font-medium ${
                          item.completed
                            ? "text-white"
                            : item.required
                            ? "text-red-300"
                            : "text-[rgb(163,163,163)]"
                        }`}
                      >
                        {item.label}
                      </p>
                      {item.regulation && (
                        <p className="text-[10px] text-[rgb(115,115,115)] mt-0.5">
                          {item.regulation}
                        </p>
                      )}
                    </div>
                    {item.required && !item.completed && (
                      <span className="text-[10px] bg-red-500/10 text-red-400 border border-red-500/20 px-1.5 py-0.5 rounded-full font-semibold flex-shrink-0">
                        REQUIRED
                      </span>
                    )}
                  </motion.div>
                ))}
                {checklist.length === 0 && (
                  <p className="text-sm text-[rgb(115,115,115)] py-4 text-center">
                    No checklist items found
                  </p>
                )}
              </div>
            </motion.div>

            {/* Applicable regulations */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.3 }}
              className="glass-card p-6"
            >
              <h2 className="font-heading font-bold text-white text-sm mb-4">
                Applicable Regulations
              </h2>
              <div className="space-y-2">
                {(system.applicableRegulations ?? []).map((reg) => (
                  <div
                    key={reg}
                    className="flex items-center gap-2 p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-blue-500/20 transition-colors cursor-pointer group"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                    <span className="text-xs text-[rgb(163,163,163)] group-hover:text-white transition-colors">
                      {reg}
                    </span>
                  </div>
                ))}
              </div>

              {total > 0 && (
                <div className="mt-6 pt-4 border-t border-white/[0.06]">
                  <p className="text-[10px] text-[rgb(115,115,115)] uppercase tracking-wider font-medium mb-3">
                    Checklist Progress
                  </p>
                  <div className="relative pt-1">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs text-white font-semibold">
                        {Math.round((completed / total) * 100)}%
                      </span>
                      <span className="text-[11px] text-[rgb(115,115,115)]">
                        {completed}/{total}
                      </span>
                    </div>
                    <div className="w-full h-2 bg-white/[0.06] rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(completed / total) * 100}%` }}
                        transition={{
                          delay: 0.3,
                          duration: 0.7,
                          ease: "easeOut",
                        }}
                        className="h-2 rounded-full"
                        style={{
                          background:
                            completed / total >= 0.8
                              ? "#22c55e"
                              : completed / total >= 0.6
                              ? "#eab308"
                              : "#ef4444",
                        }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </div>
  );
}
