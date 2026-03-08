import useSWR from "swr";
import { fetcher } from "@/lib/fetcher";
import type {
  AISystem,
  Regulation,
  Incident,
  BiasReport,
} from "@/lib/api";

const API = "/api/v1";

// ── Dashboard ─────────────────────────────────────────────────────────────

export interface DashboardStats {
  totalSystems: number;
  compliantSystems: number;
  openIncidents: number;
  upcomingDeadlines: number;
  overallScore: number;
  complianceByCategory: Array<{ label: string; score: number }>;
}

export interface RiskDistributionItem {
  name: string;
  value: number;
  color: string;
}

export interface ActivityItem {
  id: string;
  event: string;
  system: string;
  time: string;
  type: "success" | "warning" | "info" | "error";
}

export function useDashboardStats() {
  return useSWR<DashboardStats>(`${API}/dashboard/stats`, fetcher);
}

export function useDashboardRiskDistribution() {
  return useSWR<RiskDistributionItem[]>(
    `${API}/dashboard/risk-distribution`,
    fetcher
  );
}

export function useRecentActivity() {
  return useSWR<ActivityItem[]>(`${API}/dashboard/recent-activity`, fetcher);
}

// ── AI Systems ────────────────────────────────────────────────────────────

export function useSystems() {
  return useSWR<AISystem[]>(`${API}/ai-systems`, fetcher);
}

export function useSystem(id: string | null) {
  return useSWR<AISystem>(id ? `${API}/ai-systems/${id}` : null, fetcher);
}

// ── Regulations ───────────────────────────────────────────────────────────

export function useRegulations() {
  return useSWR<Regulation[]>(`${API}/regulations`, fetcher);
}

// ── Compliance checks ─────────────────────────────────────────────────────

export interface ComplianceCheck {
  id: string;
  systemId: string;
  systemName: string;
  regulation: string;
  status: "PASS" | "FAIL" | "PENDING";
  checkedAt: string;
  notes?: string;
}

export function useComplianceChecks() {
  return useSWR<ComplianceCheck[]>(`${API}/compliance-checks`, fetcher);
}

// ── Incidents ─────────────────────────────────────────────────────────────

export function useIncidents() {
  return useSWR<Incident[]>(`${API}/incidents`, fetcher);
}

// ── Bias audits ───────────────────────────────────────────────────────────

export function useBiasAudits() {
  return useSWR<BiasReport[]>(`${API}/bias-audits`, fetcher);
}
