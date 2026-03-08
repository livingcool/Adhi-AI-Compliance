"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Search, Filter } from "lucide-react";
import RegulationCard from "@/components/RegulationCard";
import ErrorState from "@/components/ErrorState";
import { CardSkeleton } from "@/components/Skeleton";
import { useRegulations } from "@/lib/hooks";
import type { RegulationStatus } from "@/lib/api";

const JURISDICTIONS = [
  "All",
  "European Union",
  "United States",
  "United Kingdom",
  "India",
  "International",
  "California, US",
];

export default function RegulationsPage() {
  const { data: regulations, error, isLoading, mutate } = useRegulations();
  const [search, setSearch] = useState("");
  const [jurisdiction, setJurisdiction] = useState("All");
  const [statusFilter, setStatusFilter] = useState<"ALL" | RegulationStatus>("ALL");

  const regs = regulations ?? [];

  const filtered = regs.filter((r) => {
    const matchSearch =
      search === "" ||
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.description.toLowerCase().includes(search.toLowerCase()) ||
      (r.tags ?? []).some((t) => t.toLowerCase().includes(search.toLowerCase()));
    const matchJurisdiction =
      jurisdiction === "All" || r.jurisdiction === jurisdiction;
    const matchStatus = statusFilter === "ALL" || r.status === statusFilter;
    return matchSearch && matchJurisdiction && matchStatus;
  });

  const activeCount = regs.filter((r) => r.status === "ACTIVE").length;
  const upcomingCount = regs.filter((r) => r.status === "UPCOMING").length;

  return (
    <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          <h1 className="font-heading font-bold text-xl sm:text-2xl text-white">
            Regulation Library
          </h1>
          <p className="text-sm text-[rgb(163,163,163)] mt-0.5">
            {isLoading
              ? "Loading…"
              : `${activeCount} active · ${upcomingCount} upcoming`}
          </p>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-3"
        >
          <div className="glass-card px-3 py-2 text-xs flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-green-400" />
            <span className="text-[rgb(163,163,163)]">Active</span>
            <span className="text-white font-bold ml-1">{activeCount}</span>
          </div>
          <div className="glass-card px-3 py-2 text-xs flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-400" />
            <span className="text-[rgb(163,163,163)]">Upcoming</span>
            <span className="text-white font-bold ml-1">{upcomingCount}</span>
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="glass-card p-4 flex flex-wrap gap-3 items-center"
      >
        <div className="relative flex-1 min-w-48">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[rgb(115,115,115)]" />
          <input
            type="text"
            placeholder="Search regulations, tags…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search regulations"
            className="w-full bg-white/[0.05] border border-white/[0.08] rounded-xl pl-9 pr-3 py-2 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/50 transition-colors"
          />
        </div>

        <div className="flex items-center gap-1.5 flex-wrap">
          <Filter className="w-3.5 h-3.5 text-[rgb(115,115,115)] flex-shrink-0" aria-hidden="true" />
          {JURISDICTIONS.map((j) => (
            <button
              key={j}
              onClick={() => setJurisdiction(j)}
              aria-pressed={jurisdiction === j}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                jurisdiction === j
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05] border border-transparent"
              }`}
            >
              {j}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1.5">
          {(["ALL", "ACTIVE", "UPCOMING", "DRAFT"] as const).map((s) => (
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
              {s === "ALL" ? "All Statuses" : s}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Content */}
      {error ? (
        <ErrorState
          title="Could not load regulations"
          onRetry={() => mutate()}
        />
      ) : isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <CardSkeleton key={i} lines={4} />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((reg, i) => (
            <motion.div
              key={reg.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              whileHover={{ scale: 1.01, transition: { duration: 0.15 } }}
            >
              <RegulationCard
                name={reg.name}
                jurisdiction={reg.jurisdiction}
                effectiveDate={reg.effectiveDate}
                description={reg.description}
                status={reg.status}
                applicableSystems={reg.applicableSystems}
              />
              {reg.tags && reg.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2 px-1">
                  {reg.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.05] text-[rgb(115,115,115)] border border-white/[0.06]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="glass-card p-12 text-center">
          <p className="text-sm text-[rgb(115,115,115)]">
            No regulations match your filters.
          </p>
        </div>
      )}
    </div>
  );
}
