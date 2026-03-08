'use client';

import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

// ── Types ─────────────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="flex flex-col items-center justify-center py-16 px-6 text-center"
    >
      {/* Icon container */}
      <div className="w-16 h-16 rounded-2xl bg-white/[0.04] border border-white/[0.06] flex items-center justify-center mb-5">
        <Icon className="w-7 h-7 text-white/20" strokeWidth={1.5} />
      </div>

      {/* Text */}
      <h3 className="text-[15px] font-semibold font-heading text-white/60 mb-1.5">
        {title}
      </h3>
      {description && (
        <p className="text-sm text-white/35 max-w-xs leading-relaxed">
          {description}
        </p>
      )}

      {/* Action */}
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-5 btn-pill btn-primary text-sm"
        >
          {actionLabel}
        </button>
      )}
    </motion.div>
  );
}
