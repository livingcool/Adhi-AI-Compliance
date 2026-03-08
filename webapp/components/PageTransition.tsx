'use client';

import { motion } from 'framer-motion';

// ── Types ─────────────────────────────────────────────────────────────────────

interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

// ── Variants ──────────────────────────────────────────────────────────────────

const variants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
};

// ── Component ─────────────────────────────────────────────────────────────────

/**
 * Wrap page content with this component for a smooth fade+slide entrance.
 *
 * Usage in layout.tsx (App Router):
 *   Wrap children inside <AnimatePresence mode="wait"> and add a unique `key`
 *   prop tied to the current pathname.
 *
 * Example:
 *   <AnimatePresence mode="wait">
 *     <PageTransition key={pathname}>{children}</PageTransition>
 *   </AnimatePresence>
 */
export function PageTransition({ children, className }: PageTransitionProps) {
  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{ duration: 0.32, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
