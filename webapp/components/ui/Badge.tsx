'use client';

import { clsx } from 'clsx';

// ── Types ─────────────────────────────────────────────────────────────────────

type RiskValue = 'unacceptable' | 'high' | 'limited' | 'minimal';
type StatusValue = 'compliant' | 'non-compliant' | 'partial' | 'pending';
type SeverityValue = 'critical' | 'high' | 'medium' | 'low';

interface BadgeProps {
  variant: 'risk' | 'status' | 'severity';
  value: RiskValue | StatusValue | SeverityValue;
  pulse?: boolean;
  size?: 'sm' | 'md';
}

// ── Config ────────────────────────────────────────────────────────────────────

const CONFIG: Record<string, Record<string, { label: string; classes: string; dot: string }>> = {
  risk: {
    unacceptable: {
      label: 'Unacceptable',
      classes: 'bg-red-500/15 text-red-400 border-red-500/25',
      dot: 'bg-red-500',
    },
    high: {
      label: 'High Risk',
      classes: 'bg-orange-500/15 text-orange-400 border-orange-500/25',
      dot: 'bg-orange-500',
    },
    limited: {
      label: 'Limited',
      classes: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/25',
      dot: 'bg-yellow-500',
    },
    minimal: {
      label: 'Minimal',
      classes: 'bg-green-500/15 text-green-400 border-green-500/25',
      dot: 'bg-green-500',
    },
  },
  status: {
    compliant: {
      label: 'Compliant',
      classes: 'bg-green-500/15 text-green-400 border-green-500/25',
      dot: 'bg-green-500',
    },
    'non-compliant': {
      label: 'Non-Compliant',
      classes: 'bg-red-500/15 text-red-400 border-red-500/25',
      dot: 'bg-red-500',
    },
    partial: {
      label: 'Partial',
      classes: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/25',
      dot: 'bg-yellow-500',
    },
    pending: {
      label: 'Pending',
      classes: 'bg-blue-500/15 text-blue-400 border-blue-500/25',
      dot: 'bg-blue-500',
    },
  },
  severity: {
    critical: {
      label: 'Critical',
      classes: 'bg-red-500/15 text-red-400 border-red-500/25',
      dot: 'bg-red-500',
    },
    high: {
      label: 'High',
      classes: 'bg-orange-500/15 text-orange-400 border-orange-500/25',
      dot: 'bg-orange-500',
    },
    medium: {
      label: 'Medium',
      classes: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/25',
      dot: 'bg-yellow-500',
    },
    low: {
      label: 'Low',
      classes: 'bg-green-500/15 text-green-400 border-green-500/25',
      dot: 'bg-green-500',
    },
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

export function Badge({ variant, value, pulse = false, size = 'sm' }: BadgeProps) {
  const entry = CONFIG[variant]?.[value] ?? {
    label: value,
    classes: 'bg-white/10 text-white/60 border-white/10',
    dot: 'bg-white/40',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 border font-medium rounded-full',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
        entry.classes
      )}
    >
      {pulse ? (
        <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
          <span
            className={clsx(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              entry.dot
            )}
          />
          <span className={clsx('relative inline-flex rounded-full h-1.5 w-1.5', entry.dot)} />
        </span>
      ) : null}
      {entry.label}
    </span>
  );
}
