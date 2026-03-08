
import { Mail, Users, Database, Activity, Zap } from "lucide-react";

// --- Types ---
export interface LedgerItem {
    id: string;
    name: string;
    type: "Strategy" | "Surveillance" | "Communication" | "Financial" | "Legal" | "Technical";
    confidence: string;
    status: "Verified" | "Analyzing" | "Flagged";
    date: string;
}

export interface ClientHealth {
    name: string;
    volume: number;
    status: "Healthy" | "Processing" | "Warning";
    score: number;
    lastUpdate: string;
}

export interface VolumeData {
    month: string;
    docs: number;
    size: number;
}

// --- Data ---

export const MOCK_LEDGER_DATA: LedgerItem[] = [
    { id: "FIN-2025-001", name: "FY25 Strategy Deck.pdf", type: "Strategy", confidence: "98%", status: "Verified", date: "Jan 15, 2025" },
    { id: "IMG-992", name: "Site_B_Drone_Footage.mov", type: "Surveillance", confidence: "92%", status: "Analyzing", date: "Today, 11:45 AM" },
    { id: "EML-442", name: "Re: Merger Negotiation", type: "Communication", confidence: "96%", status: "Verified", date: "Yesterday, 6:15 PM" },
    { id: "INV-X09", name: "Q1_Service_Invoice.pdf", type: "Financial", confidence: "78%", status: "Flagged", date: "Jan 10, 2025" },
    { id: "LEG-771", name: "NDA_Signed_Beta.pdf", type: "Legal", confidence: "100%", status: "Verified", date: "Jan 05, 2025" },
    { id: "API-LOG", name: "Access_Logs_Export.csv", type: "Technical", confidence: "88%", status: "Verified", date: "Today, 08:00 AM" },
    { id: "AUD-REC", name: "Board_Meeting_Audio.mp3", type: "Communication", confidence: "85%", status: "Analyzing", date: "Jan 20, 2025" },
];

export const MOCK_DRAFT_ACTION = {
    id: "draft_1",
    type: "email" as const,
    title: "Urgent: Compliance Violation Detected in Invoice #992",
    recipient: "legal@client-alpha.com",
    content: `Dear Legal Team,\n\nOur automated audit system has detected a critical mismatch between Invoice #992 and the original Purchase Order #331.\n\n- Discrepancy: Unit Price Variance (+15%)\n- Detected: Today, 10:42 AM\n\nPlease review the attached documentation immediately to avoid payment delays.\n\nBest regards,\nADHI Intelligence Agent`,
    context: "Invoice #992 unit price ($150) does not match PO #331 ($130).",
    integration_icon: Mail,
    confidence: 98
};

export const MOCK_CLIENT_HEALTH: ClientHealth[] = [
    { name: "Client Alpha", volume: 45, status: "Healthy", score: 98, lastUpdate: "2m ago" },
    { name: "Client Bravo", volume: 32, status: "Processing", score: 92, lastUpdate: "15m ago" },
    { name: "Client Charlie", volume: 18, status: "Warning", score: 76, lastUpdate: "1h ago" },
    { name: "Client Delta", volume: 64, status: "Healthy", score: 99, lastUpdate: "5m ago" },
];

export const MOCK_VOLUME_DATA: VolumeData[] = [
    { month: "Jan", docs: 45, size: 1.2 },
    { month: "Feb", docs: 52, size: 1.5 },
    { month: "Mar", docs: 38, size: 1.1 },
    { month: "Apr", docs: 65, size: 2.1 },
    { month: "May", docs: 48, size: 1.8 },
    { month: "Jun", docs: 72, size: 2.5 },
];

export const DASHBOARD_STATS = [
    { label: "Active Clients", value: "24", trend: "+3", icon: Users, color: "text-[var(--primary)]" },
    { label: "Neural Index Size", value: "4.2 TB", trend: "+500GB", icon: Database, color: "text-[var(--secondary)]" },
    { label: "Avg. Precision", value: "98.4%", trend: "+1.2%", icon: Zap, color: "text-[var(--primary)]" },
    { label: "System Health", value: "99.9%", trend: "Stable", icon: Activity, color: "text-[var(--success)]" },
];

export const RECENT_LOGS = [
    { type: "success", msg: "Client Delta: Video transcription complete for 'Audit_2024.mp4'", time: "Just now" },
    { type: "warning", msg: "Client Charlie: Vision analysis delayed due to high pixel density on page 42", time: "12m ago" },
    { type: "success", msg: "Client Alpha: Document similarity indexing cross-verified", time: "45m ago" },
];
