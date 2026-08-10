'use client';

/**
 * LucideIcon — renders any Lucide icon by string name.
 *
 * Usage:
 *   <LucideIcon name="Wheat" />
 *   <LucideIcon name="Coffee" className="text-amber-500" size={20} />
 *
 * Falls back to a small square placeholder if the icon name is not found.
 * Icon names must match Lucide's PascalCase export names (e.g. "GlassWater", "ShieldCheck").
 */

import { type LucideProps } from 'lucide-react';
import * as icons from 'lucide-react';

type IconName = keyof typeof icons;

interface LucideIconProps extends LucideProps {
  /** PascalCase Lucide icon name, e.g. "Wheat", "Coffee", "Droplets" */
  name: string;
  /** Tailwind color class or any CSS color class. Defaults to "text-white". */
  className?: string;
  size?: number;
}

export function LucideIcon({ name, className = 'text-white', size = 18, ...rest }: LucideIconProps) {
  const Icon = icons[name as IconName] as React.ComponentType<LucideProps> | undefined;

  if (!Icon) {
    // Fallback: tiny rounded square so layout doesn't break
    return (
      <span
        className={`inline-block rounded bg-current opacity-30 ${className}`}
        style={{ width: size, height: size }}
        aria-hidden
      />
    );
  }

  return <Icon size={size} className={className} strokeWidth={1.75} {...rest} />;
}
