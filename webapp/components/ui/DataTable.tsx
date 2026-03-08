'use client';

import { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
}

interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
}

// ── Skeleton row ──────────────────────────────────────────────────────────────

function ShimmerCell({ width }: { width: string }) {
  return (
    <td className="px-4 py-3.5">
      <div
        className="h-3.5 rounded-md bg-white/[0.06] animate-pulse"
        style={{ width }}
      />
    </td>
  );
}

const SHIMMER_WIDTHS = ['72%', '55%', '80%', '45%', '65%', '60%', '70%'];

function ShimmerRow({ cols }: { cols: number }) {
  return (
    <tr>
      {Array.from({ length: cols }).map((_, i) => (
        <ShimmerCell key={i} width={SHIMMER_WIDTHS[i % SHIMMER_WIDTHS.length]} />
      ))}
    </tr>
  );
}

// ── Sort icon ─────────────────────────────────────────────────────────────────

function SortIcon({ active, dir }: { active: boolean; dir: 'asc' | 'desc' }) {
  if (!active) return <ChevronsUpDown className="w-3 h-3 text-white/25" />;
  return dir === 'asc'
    ? <ChevronUp className="w-3 h-3 text-blue-400" />
    : <ChevronDown className="w-3 h-3 text-blue-400" />;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No data available',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const handleSort = (key: string, sortable: boolean) => {
    if (!sortable) return;
    if (sortKey === key) {
      setSortDir(d => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sorted = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (av == null) return 1;
      if (bv == null) return -1;
      const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
  }, [data, sortKey, sortDir]);

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-full table-auto">
        <thead>
          <tr className="border-b border-white/[0.06]">
            {columns.map(col => {
              const canSort = col.sortable !== false;
              const isActive = sortKey === col.key;
              return (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key, canSort)}
                  className={clsx(
                    'px-4 py-3 text-left text-[11px] font-semibold text-white/40 uppercase tracking-wider select-none',
                    canSort && 'cursor-pointer hover:text-white/60 transition-colors'
                  )}
                >
                  <span className="inline-flex items-center gap-1">
                    {col.header}
                    {canSort && (
                      <SortIcon active={isActive} dir={sortDir} />
                    )}
                  </span>
                </th>
              );
            })}
          </tr>
        </thead>

        <tbody>
          {loading ? (
            Array.from({ length: 5 }).map((_, i) => (
              <ShimmerRow key={i} cols={columns.length} />
            ))
          ) : sorted.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="text-center py-14 text-white/30 text-sm"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sorted.map((row, i) => (
              <motion.tr
                key={i}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2, delay: i * 0.03 }}
                className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors duration-150"
              >
                {columns.map(col => (
                  <td key={col.key} className="px-4 py-3.5 text-sm text-white/75">
                    {col.render
                      ? col.render(row)
                      : (row[col.key] as React.ReactNode) ?? '—'}
                  </td>
                ))}
              </motion.tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
