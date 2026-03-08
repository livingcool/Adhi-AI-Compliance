'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface TabItem {
  id: string;
  label: string;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: TabItem[];
  defaultTab?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function Tabs({ tabs, defaultTab }: TabsProps) {
  const [activeId, setActiveId] = useState<string>(defaultTab ?? tabs[0]?.id ?? '');

  const activeTab = tabs.find(t => t.id === activeId);

  return (
    <div>
      {/* Tab bar */}
      <div
        role="tablist"
        className="flex items-center gap-1 p-1 bg-white/[0.04] border border-white/[0.06] rounded-xl w-fit"
      >
        {tabs.map(tab => {
          const isActive = tab.id === activeId;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`tab-panel-${tab.id}`}
              id={`tab-${tab.id}`}
              onClick={() => setActiveId(tab.id)}
              className={clsx(
                'relative px-4 py-2 text-sm font-medium rounded-lg z-10',
                'transition-colors duration-200 outline-none',
                isActive ? 'text-white' : 'text-white/45 hover:text-white/75'
              )}
            >
              {/* Animated pill indicator */}
              {isActive && (
                <motion.span
                  layoutId="tab-pill"
                  className="absolute inset-0 rounded-lg bg-blue-500/20 border border-blue-500/30"
                  transition={{ type: 'spring', bounce: 0.18, duration: 0.38 }}
                />
              )}
              <span className="relative z-10">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      {activeTab && (
        <div
          role="tabpanel"
          id={`tab-panel-${activeTab.id}`}
          aria-labelledby={`tab-${activeTab.id}`}
          className="mt-4 outline-none"
        >
          <motion.div
            key={activeId}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.22 }}
          >
            {activeTab.content}
          </motion.div>
        </div>
      )}
    </div>
  );
}
