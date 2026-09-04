import React from 'react';

interface BrandWordmarkProps {
  className?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showSubtitle?: boolean;
}

/**
 * BrandWordmark — Unified single source of truth for Ayuरक्षा wordmark.
 * Renders "Ayu" (Latin) + "रक्षा" (Devanagari in primary green) as a cohesive, single-layer mark.
 */
export const BrandWordmark: React.FC<BrandWordmarkProps> = ({
  className = '',
  size = 'md',
  showSubtitle = false,
}) => {
  const sizeMap = {
    xs: {
      text: 'text-xs',
      sub: 'text-[8px]'
    },
    sm: {
      text: 'text-sm font-bold',
      sub: 'text-[9px]'
    },
    md: {
      text: 'text-base font-bold',
      sub: 'text-[9px]'
    },
    lg: {
      text: 'text-xl font-extrabold',
      sub: 'text-[9px]'
    },
    xl: {
      text: 'text-2xl sm:text-3xl font-black',
      sub: 'text-[10px]'
    },
  };

  const current = sizeMap[size];

  return (
    <div className={`inline-flex flex-col justify-center select-none ${className}`}>
      <div className="inline-flex items-baseline space-x-1.5 leading-none">
        <span className={`tracking-tight font-display text-slate-900 ${current.text}`}>
          Ayu<span className="text-ayush-forest font-bold">रक्षा</span>
        </span>
      </div>
      {showSubtitle && (
        <span className={`font-bold text-slate-400 tracking-wider uppercase mt-1 leading-none ${current.sub}`}>
          IP-SAKTI Sahayak
        </span>
      )}
    </div>
  );
};
