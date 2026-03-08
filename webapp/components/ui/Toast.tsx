'use client';

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react';
import { clsx } from 'clsx';

// ── Types ─────────────────────────────────────────────────────────────────────

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextValue {
  toast: (type: ToastType, message: string) => void;
}

// ── Config ────────────────────────────────────────────────────────────────────

const TOAST_CONFIG = {
  success: {
    icon: CheckCircle2,
    wrapper: 'border-green-500/30 bg-[rgba(34,197,94,0.08)]',
    iconClass: 'text-green-400',
  },
  error: {
    icon: XCircle,
    wrapper: 'border-red-500/30 bg-[rgba(239,68,68,0.08)]',
    iconClass: 'text-red-400',
  },
  warning: {
    icon: AlertTriangle,
    wrapper: 'border-yellow-500/30 bg-[rgba(234,179,8,0.08)]',
    iconClass: 'text-yellow-400',
  },
  info: {
    icon: Info,
    wrapper: 'border-blue-500/30 bg-[rgba(59,130,246,0.08)]',
    iconClass: 'text-blue-400',
  },
} as const;

const AUTO_DISMISS_MS = 5000;

// ── Context ───────────────────────────────────────────────────────────────────

const ToastContext = createContext<ToastContextValue | null>(null);

// ── Provider ──────────────────────────────────────────────────────────────────

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const toast = useCallback(
    (type: ToastType, message: string) => {
      const id = Math.random().toString(36).slice(2, 9);
      setToasts(prev => [...prev, { id, type, message }]);
      setTimeout(() => dismiss(id), AUTO_DISMISS_MS);
    },
    [dismiss]
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}

      {/* Toast stack */}
      <div
        aria-live="polite"
        aria-atomic="false"
        className="fixed bottom-5 right-5 z-[200] flex flex-col gap-2.5 pointer-events-none"
      >
        <AnimatePresence mode="popLayout">
          {toasts.map(t => {
            const cfg = TOAST_CONFIG[t.type];
            const Icon = cfg.icon;
            return (
              <motion.div
                key={t.id}
                role="alert"
                initial={{ opacity: 0, x: 56, scale: 0.92 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 56, scale: 0.92 }}
                transition={{ duration: 0.22, ease: 'easeOut' }}
                layout
                className={clsx(
                  'flex items-start gap-3 w-[300px] max-w-sm px-4 py-3 rounded-xl',
                  'border backdrop-blur-xl pointer-events-auto',
                  'shadow-[0_8px_32px_rgba(0,0,0,0.5)]',
                  cfg.wrapper
                )}
              >
                <Icon className={clsx('w-4 h-4 mt-0.5 flex-shrink-0', cfg.iconClass)} />
                <span className="text-sm text-white/85 flex-1 leading-snug">
                  {t.message}
                </span>
                <button
                  onClick={() => dismiss(t.id)}
                  className="text-white/25 hover:text-white/60 transition-colors ml-1 flex-shrink-0 mt-0.5"
                  aria-label="Dismiss"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>');
  return ctx;
}
