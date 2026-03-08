'use client';

import { motion } from 'framer-motion';

interface CircularProgressProps {
  value: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

function getColor(value: number): string {
  if (value < 40) return 'rgb(239, 68, 68)';
  if (value < 70) return 'rgb(234, 179, 8)';
  return 'rgb(34, 197, 94)';
}

function getGlow(value: number): string {
  if (value < 40) return 'rgba(239,68,68,0.5)';
  if (value < 70) return 'rgba(234,179,8,0.5)';
  return 'rgba(34,197,94,0.5)';
}

export function CircularProgress({
  value,
  size = 120,
  strokeWidth = 10,
  label,
}: CircularProgressProps) {
  const clamped = Math.min(100, Math.max(0, value));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  const color = getColor(clamped);
  const glow = getGlow(clamped);

  return (
    <div className="relative inline-flex items-center justify-center flex-shrink-0">
      <svg
        width={size}
        height={size}
        style={{ transform: 'rotate(-90deg)' }}
        aria-label={`${clamped}% ${label ?? ''}`}
        role="img"
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress arc */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut', delay: 0.15 }}
          style={{ filter: `drop-shadow(0 0 6px ${glow})` }}
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <span
          className="font-bold font-heading text-white leading-none"
          style={{ fontSize: Math.round(size * 0.18) }}
        >
          {clamped}%
        </span>
        {label && (
          <span
            className="text-white/50 mt-1 text-center leading-tight"
            style={{ fontSize: Math.max(9, Math.round(size * 0.09)) }}
          >
            {label}
          </span>
        )}
      </div>
    </div>
  );
}
