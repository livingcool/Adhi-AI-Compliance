interface RiskBadgeProps {
  level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  size?: "sm" | "md";
}

const config: Record<
  RiskBadgeProps["level"],
  { bg: string; text: string; border: string; dot: string }
> = {
  LOW: {
    bg: "bg-green-500/10",
    text: "text-green-400",
    border: "border-green-500/25",
    dot: "bg-green-400",
  },
  MEDIUM: {
    bg: "bg-yellow-500/10",
    text: "text-yellow-400",
    border: "border-yellow-500/25",
    dot: "bg-yellow-400",
  },
  HIGH: {
    bg: "bg-orange-500/10",
    text: "text-orange-400",
    border: "border-orange-500/25",
    dot: "bg-orange-400",
  },
  CRITICAL: {
    bg: "bg-red-500/10",
    text: "text-red-400",
    border: "border-red-500/25",
    dot: "bg-red-400",
  },
};

export default function RiskBadge({ level, size = "md" }: RiskBadgeProps) {
  const c = config[level];
  const padding = size === "sm" ? "px-2 py-0.5" : "px-2.5 py-1";
  const text = size === "sm" ? "text-[10px]" : "text-xs";

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${padding} rounded-full border font-semibold ${text} ${c.bg} ${c.text} ${c.border}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${c.dot}`} />
      {level}
    </span>
  );
}
