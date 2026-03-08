'use client';

import { useEffect, useRef, useState } from 'react';
import { Search, X } from 'lucide-react';

// ── Types ─────────────────────────────────────────────────────────────────────

interface SearchInputProps {
  placeholder?: string;
  value?: string;
  onChange: (value: string) => void;
  className?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function SearchInput({
  placeholder = 'Search…',
  value: externalValue = '',
  onChange,
  className,
}: SearchInputProps) {
  const [internal, setInternal] = useState(externalValue);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const prevExternal = useRef(externalValue);

  // Sync when parent clears / updates value
  useEffect(() => {
    if (prevExternal.current !== externalValue) {
      prevExternal.current = externalValue;
      setInternal(externalValue);
    }
  }, [externalValue]);

  const handleChange = (newValue: string) => {
    setInternal(newValue);
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => onChange(newValue), 300);
  };

  const handleClear = () => {
    handleChange('');
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return (
    <div className={`relative ${className ?? ''}`}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30 pointer-events-none" />

      <input
        type="search"
        value={internal}
        onChange={e => handleChange(e.target.value)}
        placeholder={placeholder}
        className="
          w-full pl-9 pr-8 py-2.5 text-sm
          bg-white/[0.06] backdrop-blur-xl
          border border-white/[0.08] rounded-xl
          text-white/85 placeholder:text-white/30
          focus:outline-none focus:ring-0
          focus:border-blue-500/50 focus:bg-white/[0.09]
          transition-all duration-200
        "
      />

      {internal && (
        <button
          onClick={handleClear}
          aria-label="Clear search"
          className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
