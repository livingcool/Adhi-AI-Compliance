'use client';

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// ── Types & defaults ──────────────────────────────────────────────────────────

export interface ScoreDataPoint {
  date: string;
  score: number;
}

const DEFAULT_DATA: ScoreDataPoint[] = [
  { date: 'Jan', score: 61 },
  { date: 'Feb', score: 58 },
  { date: 'Mar', score: 65 },
  { date: 'Apr', score: 72 },
  { date: 'May', score: 69 },
  { date: 'Jun', score: 78 },
  { date: 'Jul', score: 82 },
  { date: 'Aug', score: 80 },
  { date: 'Sep', score: 86 },
  { date: 'Oct', score: 88 },
  { date: 'Nov', score: 91 },
  { date: 'Dec', score: 94 },
];

// ── Custom tooltip ────────────────────────────────────────────────────────────

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[rgb(14,14,14)] border border-white/10 rounded-xl px-3.5 py-2.5 shadow-xl">
      <p className="text-xs text-white/45 mb-0.5">{label}</p>
      <p className="text-sm font-semibold text-blue-400">{payload[0].value}%</p>
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

interface ComplianceScoreChartProps {
  data?: ScoreDataPoint[];
  height?: number;
}

export function ComplianceScoreChart({
  data = DEFAULT_DATA,
  height = 220,
}: ComplianceScoreChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
        {/* Gradient fill definition */}
        <defs>
          <linearGradient id="blueGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(59,130,246)" stopOpacity={0.28} />
            <stop offset="100%" stopColor="rgb(59,130,246)" stopOpacity={0} />
          </linearGradient>
        </defs>

        <CartesianGrid
          strokeDasharray="3 3"
          stroke="rgba(255,255,255,0.04)"
          vertical={false}
        />

        <XAxis
          dataKey="date"
          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />

        <YAxis
          domain={[40, 100]}
          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={v => `${v}%`}
        />

        <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(59,130,246,0.3)', strokeWidth: 1 }} />

        <Area
          type="monotone"
          dataKey="score"
          stroke="rgb(59,130,246)"
          strokeWidth={2}
          fill="url(#blueGradient)"
          dot={false}
          activeDot={{
            r: 4,
            fill: 'rgb(59,130,246)',
            stroke: 'rgb(255,255,255)',
            strokeWidth: 1.5,
          }}
          animationDuration={1200}
          animationEasing="ease-out"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
