'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';

// ── Types ─────────────────────────────────────────────────────────────────────

export type TimelineEventType = 'info' | 'warning' | 'error' | 'success';

export interface TimelineEvent {
  date: string;
  title: string;
  description?: string;
  type?: TimelineEventType;
}

interface TimelineProps {
  events: TimelineEvent[];
}

// ── Config ────────────────────────────────────────────────────────────────────

const TYPE_CONFIG: Record<TimelineEventType, { dot: string; connector: string; label: string }> = {
  info: {
    dot: 'bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.7)]',
    connector: 'bg-blue-500/20',
    label: 'text-blue-400',
  },
  warning: {
    dot: 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.7)]',
    connector: 'bg-yellow-500/20',
    label: 'text-yellow-400',
  },
  error: {
    dot: 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.7)]',
    connector: 'bg-red-500/20',
    label: 'text-red-400',
  },
  success: {
    dot: 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.7)]',
    connector: 'bg-green-500/20',
    label: 'text-green-400',
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

export function Timeline({ events }: TimelineProps) {
  return (
    <ol className="flex flex-col">
      {events.map((event, i) => {
        const type = event.type ?? 'info';
        const cfg = TYPE_CONFIG[type];
        const isLast = i === events.length - 1;

        return (
          <motion.li
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.28, delay: i * 0.07 }}
            className="flex gap-4"
          >
            {/* Dot + vertical connector */}
            <div className="flex flex-col items-center flex-shrink-0">
              <span
                className={clsx(
                  'w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0',
                  cfg.dot
                )}
              />
              {!isLast && (
                <div
                  className={clsx('w-px flex-1 mt-1.5 mb-0', cfg.connector)}
                  style={{ minHeight: 28 }}
                />
              )}
            </div>

            {/* Content */}
            <div className={clsx('pb-5 min-w-0', isLast && 'pb-0')}>
              <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5 mb-0.5">
                <span className="text-sm font-medium text-white leading-snug">
                  {event.title}
                </span>
                <span className="text-[11px] text-white/35 flex-shrink-0">
                  {event.date}
                </span>
              </div>
              {event.description && (
                <p className="text-xs text-white/45 leading-relaxed">
                  {event.description}
                </p>
              )}
            </div>
          </motion.li>
        );
      })}
    </ol>
  );
}
