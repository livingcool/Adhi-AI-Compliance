'use client';

import { motion } from 'framer-motion';
import { TrendingDown, TrendingUp } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';
import { AnimatedCounter } from './AnimatedCounter';

// ── Types ─────────────────────────────────────────────────────────────────────

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  trend?: number;
  trendDirection?: 'up' | 'down';
  delay?: number;
  className?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function StatCard({
  icon: Icon,
  label,
  value,
  prefix,
  suffix,
  decimals = 0,
  trend,
  trendDirection = 'up',
  delay = 0,
  className,
}: StatCardProps) {
  const isPositiveTrend = trendDirection === 'up';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut', delay }}
      className={clsx('glass-card p-5 flex flex-col gap-4', className)}
    >
      {/* Header: icon + label */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
          <Icon className="w-4 h-4 text-blue-400" />
        </div>
        <span className="text-sm text-white/55 font-medium leading-tight">{label}</span>
      </div>

      {/* Value + trend */}
      <div className="flex items-end justify-between">
        <span className="text-[2rem] font-bold font-heading text-white leading-none">
          <AnimatedCounter
            value={value}
            prefix={prefix}
            suffix={suffix}
            decimals={decimals}
          />
        </span>

        {trend !== undefined && (
          <div
            className={clsx(
              'flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full',
              isPositiveTrend
                ? 'bg-green-500/10 text-green-400'
                : 'bg-red-500/10 text-red-400'
            )}
          >
            {isPositiveTrend ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
    </motion.div>
  );
}
