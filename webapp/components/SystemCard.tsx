import Link from "next/link";
import { CheckCircle2, XCircle, Clock, ArrowRight } from "lucide-react";
import RiskBadge from "./RiskBadge";

interface SystemCardProps {
  id: string;
  name: string;
  type: string;
  risk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  complianceScore: number;
  status: "COMPLIANT" | "NON_COMPLIANT" | "REVIEW";
  owner: string;
  lastAudit: string;
}

const statusConfig = {
  COMPLIANT: {
    icon: CheckCircle2,
    label: "Compliant",
    color: "text-green-400",
  },
  NON_COMPLIANT: {
    icon: XCircle,
    label: "Non-Compliant",
    color: "text-red-400",
  },
  REVIEW: {
    icon: Clock,
    label: "In Review",
    color: "text-yellow-400",
  },
};

export default function SystemCard({
  id,
  name,
  type,
  risk,
  complianceScore,
  status,
  owner,
  lastAudit,
}: SystemCardProps) {
  const sc = statusConfig[status];
  const StatusIcon = sc.icon;

  return (
    <Link href={`/systems/${id}`}>
      <div className="glass-card p-5 hover:border-blue-500/20 cursor-pointer group h-full">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0 mr-2">
            <h3 className="font-heading font-bold text-white text-sm group-hover:text-blue-400 transition-colors truncate">
              {name}
            </h3>
            <p className="text-[11px] text-[rgb(163,163,163)] mt-0.5">{type}</p>
          </div>
          <RiskBadge level={risk} />
        </div>

        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-1.5 text-xs">
            <StatusIcon className={`w-3.5 h-3.5 ${sc.color}`} />
            <span className={sc.color + " font-medium"}>{sc.label}</span>
          </div>
          <div className="text-xs text-[rgb(163,163,163)]">
            <span className="text-white font-semibold">{complianceScore}%</span>
          </div>
        </div>

        {/* Score bar */}
        <div className="w-full h-1 bg-white/[0.06] rounded-full mb-3">
          <div
            className="h-1 rounded-full transition-all duration-700"
            style={{
              width: `${complianceScore}%`,
              background:
                complianceScore >= 80
                  ? "#22c55e"
                  : complianceScore >= 60
                  ? "#eab308"
                  : "#ef4444",
            }}
          />
        </div>

        <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-[rgb(115,115,115)]">
          <span>{owner}</span>
          <span>Audited {lastAudit}</span>
        </div>

        <div className="flex items-center justify-end mt-2 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity text-xs gap-1">
          View details <ArrowRight className="w-3 h-3" />
        </div>
      </div>
    </Link>
  );
}
