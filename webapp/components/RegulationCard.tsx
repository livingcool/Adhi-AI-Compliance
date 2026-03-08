import { ExternalLink, Calendar, Globe } from "lucide-react";

interface RegulationCardProps {
  name: string;
  jurisdiction: string;
  effectiveDate: string;
  description: string;
  status: "ACTIVE" | "UPCOMING" | "DRAFT";
  applicableSystems?: number;
  onClick?: () => void;
}

const statusStyles: Record<RegulationCardProps["status"], string> = {
  ACTIVE: "bg-green-500/10 text-green-400 border-green-500/25",
  UPCOMING: "bg-blue-500/10 text-blue-400 border-blue-500/25",
  DRAFT: "bg-white/5 text-[rgb(163,163,163)] border-white/10",
};

export default function RegulationCard({
  name,
  jurisdiction,
  effectiveDate,
  description,
  status,
  applicableSystems = 0,
  onClick,
}: RegulationCardProps) {
  return (
    <div
      onClick={onClick}
      className="glass-card p-5 hover:border-blue-500/20 cursor-pointer group"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <h3 className="font-heading font-bold text-white text-sm group-hover:text-blue-400 transition-colors">
              {name}
            </h3>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${statusStyles[status]}`}
            >
              {status}
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] text-[rgb(163,163,163)]">
            <span className="flex items-center gap-1">
              <Globe className="w-3 h-3" />
              {jurisdiction}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {effectiveDate}
            </span>
          </div>
        </div>
        <ExternalLink className="w-3.5 h-3.5 text-[rgb(115,115,115)] group-hover:text-blue-400 transition-colors flex-shrink-0 ml-2 mt-0.5" />
      </div>

      <p className="text-[11px] text-[rgb(163,163,163)] line-clamp-2 mb-3 leading-relaxed">
        {description}
      </p>

      {applicableSystems > 0 && (
        <div className="text-[11px] text-[rgb(115,115,115)]">
          Applies to{" "}
          <span className="text-white font-semibold">{applicableSystems}</span>{" "}
          system{applicableSystems !== 1 ? "s" : ""}
        </div>
      )}
    </div>
  );
}
