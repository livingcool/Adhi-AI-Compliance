'use client';

import { motion, HTMLMotionProps } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface GlassCardProps extends Omit<HTMLMotionProps<'div'>, 'animate' | 'initial'> {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  animate?: boolean;
}

export function GlassCard({
  children,
  className,
  hover = false,
  animate = false,
  ...rest
}: GlassCardProps) {
  return (
    <motion.div
      initial={animate ? { opacity: 0, y: 20 } : false}
      animate={animate ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : undefined}
      className={twMerge(
        clsx(
          'bg-white/[0.06] backdrop-blur-xl border border-white/[0.08] rounded-2xl',
          'transition-colors duration-300',
          hover && [
            'cursor-default',
            'hover:bg-white/[0.09]',
            'hover:border-blue-500/40',
            'hover:shadow-[0_0_24px_rgba(59,130,246,0.12)]',
          ],
          className
        )
      )}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
