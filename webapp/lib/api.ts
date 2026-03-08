import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Legacy interfaces (kept for backwards compatibility) ──────────────────
export interface Organization {
  id: string;
  name: string;
  slug: string;
}

export interface QueryRequest {
  query: string;
  organization_id?: string;
  top_k?: number;
}

export interface SourceChunk {
  source_file: string;
  chunk_text: string;
  start_time?: number;
  end_time?: number;
  score: number;
  image_path?: string;
  chunk_type: string;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
  query_id: string;
  viz_data?: {
    type: "bar" | "line" | "pie" | "table";
    title: string;
    data: Record<string, unknown>[];
    config?: { xKey?: string; yKey?: string };
  };
}

// ── Compliance domain types ──────────────────────────────────────────────

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ComplianceStatus = "COMPLIANT" | "NON_COMPLIANT" | "REVIEW";
export type RegulationStatus = "ACTIVE" | "UPCOMING" | "DRAFT";

export interface Company {
  id: string;
  name: string;
  industry: string;
  jurisdiction: string;
  overallScore: number;
  totalSystems: number;
  compliantSystems: number;
  openIncidents: number;
  upcomingDeadlines: number;
}

export interface AISystem {
  id: string;
  name: string;
  type: string;
  description: string;
  risk: RiskLevel;
  status: ComplianceStatus;
  complianceScore: number;
  owner: string;
  department: string;
  lastAudit: string;
  nextAudit: string;
  applicableRegulations: string[];
  checklistItems: ChecklistItem[];
}

export interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
  required: boolean;
  regulation?: string;
}

export interface Regulation {
  id: string;
  name: string;
  shortName: string;
  jurisdiction: string;
  effectiveDate: string;
  description: string;
  status: RegulationStatus;
  applicableSystems: number;
  requirements: string[];
  tags: string[];
}

export interface Incident {
  id: string;
  title: string;
  system: string;
  severity: RiskLevel;
  status: "OPEN" | "INVESTIGATING" | "RESOLVED";
  createdAt: string;
  resolvedAt?: string;
  description: string;
}

export interface BiasReport {
  id: string;
  systemId: string;
  systemName: string;
  runDate: string;
  overallScore: number;
  metrics: BiasMetric[];
  status: "PASS" | "WARN" | "FAIL";
}

export interface BiasMetric {
  name: string;
  value: number;
  threshold: number;
  status: "PASS" | "WARN" | "FAIL";
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  citations?: string[];
}

// ── Company endpoints ─────────────────────────────────────────────────────
export const getCompany = async (): Promise<Company> => {
  const response = await api.get<Company>("/compliance/company");
  return response.data;
};

// ── AI Systems endpoints ──────────────────────────────────────────────────
export const getSystems = async (): Promise<AISystem[]> => {
  const response = await api.get<AISystem[]>("/compliance/systems");
  return response.data;
};

export const getSystemById = async (id: string): Promise<AISystem> => {
  const response = await api.get<AISystem>(`/compliance/systems/${id}`);
  return response.data;
};

export const createSystem = async (
  payload: Omit<AISystem, "id" | "checklistItems">
): Promise<AISystem> => {
  const response = await api.post<AISystem>("/compliance/systems", payload);
  return response.data;
};

export const updateSystemChecklist = async (
  systemId: string,
  items: ChecklistItem[]
): Promise<AISystem> => {
  const response = await api.patch<AISystem>(
    `/compliance/systems/${systemId}/checklist`,
    { items }
  );
  return response.data;
};

// ── Regulations endpoints ─────────────────────────────────────────────────
export const getRegulations = async (params?: {
  jurisdiction?: string;
  status?: RegulationStatus;
  search?: string;
}): Promise<Regulation[]> => {
  const response = await api.get<Regulation[]>("/compliance/regulations", {
    params,
  });
  return response.data;
};

export const getRegulationById = async (id: string): Promise<Regulation> => {
  const response = await api.get<Regulation>(`/compliance/regulations/${id}`);
  return response.data;
};

// ── Compliance summary ────────────────────────────────────────────────────
export const getComplianceSummary = async () => {
  const response = await api.get("/compliance/summary");
  return response.data;
};

// ── Incidents endpoints ───────────────────────────────────────────────────
export const getIncidents = async (): Promise<Incident[]> => {
  const response = await api.get<Incident[]>("/compliance/incidents");
  return response.data;
};

export const createIncident = async (
  payload: Omit<Incident, "id" | "createdAt">
): Promise<Incident> => {
  const response = await api.post<Incident>("/compliance/incidents", payload);
  return response.data;
};

export const resolveIncident = async (id: string): Promise<Incident> => {
  const response = await api.patch<Incident>(
    `/compliance/incidents/${id}/resolve`
  );
  return response.data;
};

// ── Bias auditor endpoints ────────────────────────────────────────────────
export const getBiasReports = async (): Promise<BiasReport[]> => {
  const response = await api.get<BiasReport[]>("/compliance/bias");
  return response.data;
};

export const runBiasAudit = async (systemId: string): Promise<BiasReport> => {
  const response = await api.post<BiasReport>("/compliance/bias/run", {
    systemId,
  });
  return response.data;
};

// ── Compliance chat ───────────────────────────────────────────────────────
export const sendComplianceChat = async (
  message: string,
  history: ChatMessage[]
): Promise<ChatMessage> => {
  const response = await api.post<ChatMessage>("/compliance/chat", {
    message,
    history,
  });
  return response.data;
};

// ── Legacy helpers (kept for existing code that imports them) ─────────────
export const getOrganizations = async (): Promise<Organization[]> => {
  const response = await api.get<Organization[]>("/organizations");
  return response.data;
};

export const createOrganization = async (
  name: string,
  slug: string
): Promise<Organization> => {
  const response = await api.post<Organization>("/organizations", null, {
    params: { name, slug: slug.toLowerCase() },
  });
  return response.data;
};
