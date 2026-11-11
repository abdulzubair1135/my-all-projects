import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: number | string;
  subtext?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant: 'positive' | 'negative' | 'neutral' | 'primary';
  };
  onClick?: () => void;
  colorScheme?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'default';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  badge,
  onClick,
  colorScheme = 'default',
}) => {
  const colorMap = {
    primary: {
      bg: 'bg-[#8B5CF6]/10',
      text: 'text-[#8B5CF6]',
      border: 'hover:border-[#8B5CF6]/50',
    },
    secondary: {
      bg: 'bg-[#6366F1]/10',
      text: 'text-[#6366F1]',
      border: 'hover:border-[#6366F1]/50',
    },
    success: {
      bg: 'bg-[#22C55E]/10',
      text: 'text-[#22C55E]',
      border: 'hover:border-[#22C55E]/50',
    },
    danger: {
      bg: 'bg-[#EF4444]/10',
      text: 'text-[#EF4444]',
      border: 'hover:border-[#EF4444]/50',
    },
    warning: {
      bg: 'bg-[#F59E0B]/10',
      text: 'text-[#F59E0B]',
      border: 'hover:border-[#F59E0B]/50',
    },
    default: {
      bg: 'bg-[#10141D]',
      text: 'text-[#94A3B8]',
      border: 'hover:border-[#8B5CF6]/40',
    },
  };

  const currentTheme = colorMap[colorScheme] || colorMap.default;

  return (
    <div
      onClick={onClick}
      className={`bg-[#151B27] border border-[#252B38] rounded-2xl p-5 transition-all duration-200 relative overflow-hidden ${
        onClick ? `cursor-pointer ${currentTheme.border} hover:-translate-y-0.5 hover:shadow-xl` : ''
      }`}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-[#94A3B8]">{title}</span>
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${currentTheme.bg} ${currentTheme.text}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-extrabold text-[#F8FAFC] tracking-tight">{value}</span>
        {badge && (
          <span
            className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              badge.variant === 'positive'
                ? 'bg-[#22C55E]/15 text-[#22C55E]'
                : badge.variant === 'negative'
                ? 'bg-[#EF4444]/15 text-[#EF4444]'
                : badge.variant === 'primary'
                ? 'bg-[#8B5CF6]/15 text-[#8B5CF6]'
                : 'bg-[#252B38] text-[#94A3B8]'
            }`}
          >
            {badge.text}
          </span>
        )}
      </div>

      {subtext && <p className="text-xs text-[#94A3B8] mt-2 font-normal">{subtext}</p>}
    </div>
  );
};
