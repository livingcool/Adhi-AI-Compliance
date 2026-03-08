'use client';

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// ── Types & defaults ──────────────────────────────────────────────────────────

export interface RiskDataItem {
  name: string;
  value: number;
}

const DEFAULT_DATA: RiskDataItem[] = [
  { name: 'Unacceptable', value: 4 },
  { name: 'High Risk', value: 12 },
  { name: 'Limited', value: 23 },
  { name: 'Minimal', value: 41 },
];

const RISK_COLORS: Record<string, string> = {
  Unacceptable: '#ef4444',
  'High Risk': '#f97316',
  Limited: '#eab308',
  Minimal: '#22c55e',
};

const FALLBACK_COLOR = '#6b7280';

// ── Custom tooltip ────────────────────────────────────────────────────────────

interface TooltipPayload {
  name: string;
  value: number;
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayload[];
}) {
  if (!active || !payload?.length) return null;
  const item = payload[0];
  const color = RISK_COLORS[item.name] ?? FALLBACK_COLOR;

  return (
    <div className="bg-[rgb(14,14,14)] border border-white/10 rounded-xl px-3.5 py-2.5 shadow-xl">
      <div className="flex items-center gap-2 mb-0.5">
        <div className="w-2 h-2 rounded-full" style={{ background: color }} />
        <span className="text-sm font-medium text-white">{item.name}</span>
      </div>
      <span className="text-xs text-white/50">{item.value} systems</span>
    </div>
  );
}

// ── Custom label inside arcs ──────────────────────────────────────────────────

const RADIAN = Math.PI / 180;

function ArcLabel({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
}: {
  cx: number;
  cy: number;
  midAngle: number;
  innerRadius: number;
  outerRadius: number;
  percent: number;
}) {
  if (percent < 0.06) return null;
  const r = innerRadius + (outerRadius - innerRadius) * 0.55;
  const x = cx + r * Math.cos(-midAngle * RADIAN);
  const y = cy + r * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontWeight={600}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

interface RiskDistributionChartProps {
  data?: RiskDataItem[];
}

export function RiskDistributionChart({
  data = DEFAULT_DATA,
}: RiskDistributionChartProps) {
  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="w-full">
      {/* Donut + center label */}
      <div className="relative">
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={data as unknown[] as never[]}
              cx="50%"
              cy="50%"
              innerRadius={62}
              outerRadius={100}
              paddingAngle={3}
              dataKey="value"
              animationBegin={0}
              animationDuration={900}
              labelLine={false}
              label={ArcLabel as unknown as boolean}
            >
              {data.map(entry => (
                <Cell
                  key={entry.name}
                  fill={RISK_COLORS[entry.name] ?? FALLBACK_COLOR}
                  stroke="transparent"
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center text overlay */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold font-heading text-white leading-none">
            {total}
          </span>
          <span className="text-[11px] text-white/40 mt-0.5">Systems</span>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-x-5 gap-y-2 mt-2">
        {data.map(d => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs text-white/55">
            <div
              className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ background: RISK_COLORS[d.name] ?? FALLBACK_COLOR }}
            />
            <span>{d.name}</span>
            <span className="text-white/35">({d.value})</span>
          </div>
        ))}
      </div>
    </div>
  );
}
