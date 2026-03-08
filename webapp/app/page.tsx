"use client";

import { motion } from "framer-motion";
import {
  Cpu,
  ShieldCheck,
  AlertTriangle,
  Calendar,
  TrendingUp,
  TrendingDown,
  Activity,
  ChevronRight,
  RefreshCw,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import ComplianceScore from "@/components/ComplianceScore";
import RiskBadge from "@/components/RiskBadge";
import ErrorState from "@/components/ErrorState";
import { StatCardSkeleton, Skeleton } from "@/components/Skeleton";
import DashboardNavigation from "@/components/DashboardNavigation";
import {
  useDashboardStats,
  useDashboardRiskDistribution,
  useRecentActivity,
  useSystems,
} from "@/lib/hooks";
import type { RiskLevel } from "@/lib/api";

// ── Animation variants ────────────────────────────────────────────────────
const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.07, duration: 0.35, ease: "easeOut" as const },
  }),
};

// ── Custom tooltip for pie chart ──────────────────────────────────────────
function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: { color: string } }>;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass px-3 py-2 rounded-lg text-xs">
      <p className="font-semibold text-white">{payload[0].name} Risk</p>
      <p style={{ color: payload[0].payload.color }}>
        {payload[0].value} system{payload[0].value !== 1 ? "s" : ""}
      </p>
    </div>
  );
}

const activityDotColor: Record<string, string> = {
  success: "bg-green-400",
  warning: "bg-orange-400",
  info: "bg-blue-400",
  error: "bg-red-400",
};

const DEFAULT_RISK_DIST = [
  { name: "Low", value: 4, color: "#22c55e" },
  { name: "Medium", value: 5, color: "#eab308" },
  { name: "High", value: 2, color: "#f97316" },
  { name: "Critical", value: 1, color: "#ef4444" },
];

// ── Page ─────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const {
    data: stats,
    error: statsError,
    isLoading: statsLoading,
    mutate: mutateStats,
  } = useDashboardStats();
  const { data: riskDist, isLoading: riskLoading } =
    useDashboardRiskDistribution();
  const { data: activity, isLoading: activityLoading } = useRecentActivity();
  const { data: systems, isLoading: systemsLoading } = useSystems();

  const handleRefresh = () => {
    mutateStats();
  };

  // Build stat cards from API data
  const statCards = stats
    ? [
        {
          label: "Total AI Systems",
          value: stats.totalSystems,
          sub: `${systems?.length ?? stats.totalSystems} registered`,
          trend: "up" as const,
          icon: Cpu,
          color: "text-blue-400",
          bg: "bg-blue-500/10",
        },
        {
          label: "Compliant",
          value: stats.compliantSystems,
          sub: `${Math.round((stats.compliantSystems / Math.max(stats.totalSystems, 1)) * 100)}% compliance rate`,
          trend: "up" as const,
          icon: ShieldCheck,
          color: "text-green-400",
          bg: "bg-green-500/10",
        },
        {
          label: "Open Incidents",
          value: stats.openIncidents,
          sub: "Requires attention",
          trend: "down" as const,
          icon: AlertTriangle,
          color: "text-orange-400",
          bg: "bg-orange-500/10",
        },
        {
          label: "Upcoming Deadlines",
          value: stats.upcomingDeadlines,
          sub: "Regulatory deadlines",
          trend: "neutral" as const,
          icon: Calendar,
          color: "text-purple-400",
          bg: "bg-purple-500/10",
        },
      ]
    : null;

  const riskData = riskDist ?? DEFAULT_RISK_DIST;
  const overallScore = stats?.overallScore ?? 78;
  const complianceByCategory = stats?.complianceByCategory ?? [
    { label: "Documentation", score: 85 },
    { label: "Data Governance", score: 72 },
    { label: "Bias & Fairness", score: 68 },
    { label: "Transparency", score: 90 },
  ];

  const recentSystems = systems?.slice(0, 4) ?? [];

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
            Compliance Dashboard
          </h1>
          <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
            AI governance overview
          </p>
        </motion.div>
        <motion.button
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleRefresh}
          aria-label="Refresh dashboard"
          className="btn-pill btn-ghost flex items-center gap-2 text-sm"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Refresh</span>
        </motion.button>
      </div>

      {/* Dashboard Navigation Hub */}
      <DashboardNavigation />

      {/* Stat cards */}
      {statsError ? (
        <ErrorState
          title="Could not load dashboard stats"
          onRetry={handleRefresh}
        />
      ) : statsLoading || !statCards ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {statCards.map((s, i) => {
            const Icon = s.icon;
            return (
              <motion.div
                key={s.label}
                custom={i}
                variants={fadeUp}
                initial="hidden"
                animate="visible"
                whileHover={{ scale: 1.02, transition: { duration: 0.15 } }}
                className="glass-card p-5 cursor-default"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className={`p-2 rounded-lg ${s.bg}`}>
                    <Icon className={`w-4 h-4 ${s.color}`} />
                  </div>
                  {s.trend === "up" && (
                    <TrendingUp className="w-3.5 h-3.5 text-green-400" />
                  )}
                  {s.trend === "down" && (
                    <TrendingDown className="w-3.5 h-3.5 text-red-400" />
                  )}
                </div>
                <p className="font-heading font-bold text-3xl text-white">
                  {s.value}
                </p>
                <p className="text-xs font-medium text-[rgb(163,163,163)] mt-0.5">
                  {s.label}
                </p>
                <p className="text-[10px] text-[rgb(115,115,115)] mt-1">
                  {s.sub}
                </p>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Middle row: score + risk distribution + top systems */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Overall score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.35 }}
          className="glass-card p-6 flex flex-col items-center justify-center gap-4"
        >
          <ComplianceScore
            score={overallScore}
            size={140}
            label="Overall Compliance Score"
          />
          <div className="w-full space-y-2">
            {complianceByCategory.map((item, i) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.06, duration: 0.3 }}
                className="flex items-center gap-2 text-xs"
              >
                <span className="text-[rgb(163,163,163)] w-32 flex-shrink-0 text-[11px]">
                  {item.label}
                </span>
                <div className="flex-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.score}%` }}
                    transition={{ delay: 0.4 + i * 0.06, duration: 0.6, ease: "easeOut" }}
                    className="h-1 rounded-full"
                    style={{
                      background:
                        item.score >= 80
                          ? "#22c55e"
                          : item.score >= 60
                          ? "#eab308"
                          : "#ef4444",
                    }}
                  />
                </div>
                <span className="text-white font-medium w-8 text-right">
                  {item.score}%
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Risk distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.35 }}
          className="glass-card p-6"
        >
          <h2 className="font-heading font-bold text-white text-sm mb-4">
            Risk Distribution
          </h2>
          {riskLoading ? (
            <div className="space-y-3">
              <Skeleton className="w-full h-40 rounded-xl" />
              <div className="grid grid-cols-2 gap-2">
                {[0, 1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-5 rounded" />
                ))}
              </div>
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={riskData as unknown[] as never[]}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                    animationBegin={200}
                    animationDuration={800}
                  >
                    {riskData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {riskData.map((d) => (
                  <div key={d.name} className="flex items-center gap-2 text-xs">
                    <span
                      className="w-2 h-2 rounded-full flex-shrink-0"
                      style={{ background: d.color }}
                    />
                    <span className="text-[rgb(163,163,163)]">{d.name}</span>
                    <span className="text-white font-semibold ml-auto">
                      {d.value}
                    </span>
                  </div>
                ))}
              </div>
            </>
          )}
        </motion.div>

        {/* Top systems */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35, duration: 0.35 }}
          className="glass-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-bold text-white text-sm">
              Recent Systems
            </h2>
            <a
              href="/systems"
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-0.5 transition-colors"
            >
              View all <ChevronRight className="w-3 h-3" />
            </a>
          </div>
          {systemsLoading ? (
            <div className="space-y-4">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-3.5 w-36 rounded" />
                    <Skeleton className="h-1.5 w-full rounded-full" />
                  </div>
                  <Skeleton className="h-5 w-14 rounded-full" />
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {recentSystems.map((sys, i) => (
                <motion.a
                  key={sys.id}
                  href={`/systems/${sys.id}`}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.07, duration: 0.3 }}
                  className="flex items-center gap-3 group"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-white group-hover:text-blue-400 transition-colors truncate">
                      {sys.name}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <div className="flex-1 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                        <div
                          className="h-1 rounded-full"
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
                      <span className="text-[10px] text-[rgb(163,163,163)] w-8 text-right">
                        {sys.complianceScore}%
                      </span>
                    </div>
                  </div>
                  <RiskBadge level={sys.risk as RiskLevel} size="sm" />
                </motion.a>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Activity feed */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.35 }}
        className="glass-card p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading font-bold text-white text-sm flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            Recent Activity
          </h2>
        </div>
        {activityLoading ? (
          <div className="space-y-4">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="flex items-start gap-4">
                <Skeleton className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" />
                <div className="flex-1 space-y-1.5">
                  <Skeleton className="h-3.5 w-48 rounded" />
                  <Skeleton className="h-3 w-32 rounded" />
                </div>
                <Skeleton className="h-3 w-16 rounded flex-shrink-0" />
              </div>
            ))}
          </div>
        ) : activity && activity.length > 0 ? (
          <div className="space-y-0">
            {activity.map((item, idx) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.45 + idx * 0.05, duration: 0.25 }}
                className={`flex items-start gap-4 py-3 ${
                  idx < activity.length - 1
                    ? "border-b border-white/[0.05]"
                    : ""
                }`}
              >
                <div className="flex flex-col items-center mt-1.5 flex-shrink-0">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      activityDotColor[item.type]
                    }`}
                  />
                  {idx < activity.length - 1 && (
                    <div className="w-px h-6 bg-white/[0.06] mt-1" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-white">
                    {item.event}
                  </p>
                  <p className="text-[11px] text-[rgb(163,163,163)] mt-0.5">
                    {item.system}
                  </p>
                </div>
                <span className="text-[10px] text-[rgb(115,115,115)] flex-shrink-0 mt-0.5">
                  {item.time}
                </span>
              </motion.div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-[rgb(115,115,115)] text-center py-8">
            No recent activity
          </p>
        )}
      </motion.div>
    </div>
  );
}
