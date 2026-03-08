interface ComplianceScoreProps {
  score: number;
  size?: number;
  label?: string;
}

export default function ComplianceScore({
  score,
  size = 120,
  label = "Compliance Score",
}: ComplianceScoreProps) {
  const radius = size * 0.38;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - score / 100);

  const color =
    score >= 80
      ? "#22c55e"
      : score >= 60
      ? "#eab308"
      : score >= 40
      ? "#f97316"
      : "#ef4444";

  const trackColor = "rgba(255,255,255,0.06)";

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="relative flex items-center justify-center"
        style={{ width: size, height: size }}
      >
        <svg
          width={size}
          height={size}
          style={{ transform: "rotate(-90deg)" }}
        >
          {/* Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={trackColor}
            strokeWidth={size * 0.07}
          />
          {/* Progress */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={size * 0.07}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 1s ease, stroke 0.3s" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-heading font-bold text-white leading-none"
            style={{ fontSize: size * 0.22 }}
          >
            {score}
          </span>
          <span
            className="text-[rgb(163,163,163)] leading-none mt-0.5"
            style={{ fontSize: size * 0.1 }}
          >
            / 100
          </span>
        </div>
      </div>
      {label && (
        <p className="text-xs text-[rgb(163,163,163)] font-medium text-center">
          {label}
        </p>
      )}
    </div>
  );
}
