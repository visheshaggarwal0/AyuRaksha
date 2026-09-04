import React from 'react';
import { BrandWordmark } from './BrandWordmark';

interface BrandLogoProps {
  className?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  showSubtitle?: boolean;
  iconOnly?: boolean;
  onClick?: () => void;
}

/**
 * BrandLogo — Unified single source of truth for Ayuरक्षा Shield Icon + Wordmark.
 * Uses clean cropped shield icon (zero embedded text) + live BrandWordmark typography.
 */
export const BrandLogo: React.FC<BrandLogoProps> = ({
  className = '',
  size = 'md',
  showSubtitle = false,
  iconOnly = false,
  onClick,
}) => {
  const iconSizes = {
    xs: 'h-5 w-auto',
    sm: 'h-6 w-auto',
    md: 'h-8 w-auto',
    lg: 'h-9 w-auto',
    xl: 'h-11 w-auto',
  };

  return (
    <div
      onClick={onClick}
      className={`inline-flex items-center space-x-2.5 ${
        onClick ? 'cursor-pointer transition-opacity hover:opacity-90 select-none' : 'select-none'
      } ${className}`}
      title="Ayuरक्षा"
    >
      <img
        src="/branding/ayuraksha-icon.png"
        alt="Ayuरक्षा"
        className={`${iconSizes[size]} object-contain shrink-0`}
      />
      {!iconOnly && (
        <BrandWordmark
          size={size}
          showSubtitle={showSubtitle}
        />
      )}
    </div>
  );
};
