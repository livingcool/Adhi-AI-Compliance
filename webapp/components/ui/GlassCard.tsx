"use client";

import { motion } from "framer-motion";
import React, { useRef, useState } from "react";

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  interactive?: boolean;
}

export const GlassCard = ({
  children,
  className = "",
  delay = 0,
  interactive = true,
}: GlassCardProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current || !interactive) return;

    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setPosition({ x, y });
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.6,
        delay,
        ease: [0.23, 1, 0.32, 1]
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`relative overflow-hidden rounded-2xl glass-panel ${interactive ? "glass-panel-hover cursor-pointer" : ""
        } ${className}`}
    >
      {/* Dynamic Glare Effect */}
      {interactive && isHovered && (
        <div
          className="pointer-events-none absolute -inset-px opacity-50 mix-blend-screen transition-opacity duration-300"
          style={{
            background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,0.1), transparent 40%)`,
          }}
        />
      )}

      {/* Content */}
      <div className="relative z-10 h-full">{children}</div>
    </motion.div>
  );
};
