'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts';

// ── Types & defaults ──────────────────────────────────────────────────────────

export interface CoverageDataItem {
  jurisdiction: string;
  coverage: number;
}

const DEFAULT_DATA: CoverageDataItem[] = [
  { jurisdiction: 'EU AI Act', coverage: 87 },
  { jurisdiction: 'GDPR', coverage: 94 },
  { jurisdiction: 'NIST AI RMF', coverage: 71 },
  { jurisdiction: 'ISO 42001', coverage: 63 },
  { jurisdiction: 'UK AIRA', coverage: 58 },
  { jurisdiction: 'Canada AIDA', coverage: 45 },
];

function barColor(coverage: number): string {
  if (coverage >= 80) return '#22c55e';
  if (coverage >= 60) return '#eab308';
  return '#f97316';
}

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
  const val = payload[0].value;
  return (
    <div className="bg-[rgb(14,14,14)] border border-white/10 rounded-xl px-3.5 py-2.5 shadow-xl">
      <p className="text-xs text-white/45 mb-0.5">{label}</p>
      <p className="text-sm font-semibold" style={{ color: barColor(val) }}>
        {val}% coverage
      </p>
    </div>
  );
}

// ── Custom label on bar ends ──────────────────────────────────────────────────

function BarEndLabel({
  x,
  y,
  width,
  height,
  value,
}: {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  value?: number;
}) {
  if (value == null || x == null || y == null || width == null || height == null) return null;
  return (
    <text
      x={x + width + 6}
      y={y + height / 2}
      dominantBaseline="middle"
      fontSize={11}
      fontWeight={600}
      fill={barColor(value)}
    >
      {value}%
    </text>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

interface RegulationCoverageChartProps {
  data?: CoverageDataItem[];
}

export function RegulationCoverageChart({
  data = DEFAULT_DATA,
}: RegulationCoverageChartProps) {
  const barHeight = 32;
  const chartHeight = data.length * barHeight + (data.length - 1) * 8 + 24;

  return (
    <ResponsiveContainer width="100%" height={Math.max(chartHeight, 180)}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 0, right: 44, left: 0, bottom: 0 }}
        barSize={14}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          stroke="rgba(255,255,255,0.04)"
          horizontal={false}
        />

        <XAxis
          type="number"
          domain={[0, 100]}
          tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          tickFormatter={v => `${v}%`}
        />

        <YAxis
          type="category"
          dataKey="jurisdiction"
          width={90}
          tick={{ fill: 'rgba(255,255,255,0.55)', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />

        <Tooltip
          content={<CustomTooltip />}
          cursor={{ fill: 'rgba(255,255,255,0.03)' }}
        />

        <Bar
          dataKey="coverage"
          radius={[0, 6, 6, 0]}
          label={<BarEndLabel />}
          animationDuration={900}
          animationEasing="ease-out"
        >
          {data.map((entry, i) => (
            <Cell key={i} fill={barColor(entry.coverage)} opacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
