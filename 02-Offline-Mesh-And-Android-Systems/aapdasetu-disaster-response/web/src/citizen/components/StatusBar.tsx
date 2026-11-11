import React from 'react';

interface StatusBarProps {
  dark?: boolean;
}

export const StatusBar: React.FC<StatusBarProps> = ({ dark = false }) => {
  return (
    <header
      className={`w-full pt-3 px-7 pb-1 flex justify-between items-center text-xs font-semibold select-none z-30 shrink-0 ${
        dark ? 'text-white' : 'text-slate-900'
      }`}
    >
      <span className="font-semibold text-sm tracking-tight">9:41</span>
      <div className="flex items-center space-x-1.5" aria-label="Status Indicators">
        {/* Signal Bars */}
        <svg className="w-4 h-3.5 fill-current" viewBox="0 0 17 12">
          <rect x="0.5" y="8" width="2.5" height="4" rx="0.7" />
          <rect x="4.5" y="5.5" width="2.5" height="6.5" rx="0.7" />
          <rect x="8.5" y="3" width="2.5" height="9" rx="0.7" />
          <rect x="12.5" y="0.5" width="2.5" height="11.5" rx="0.7" />
        </svg>
        {/* Wifi Icon */}
        <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 16 12">
          <path d="M8 2.8C5.2 2.8 2.7 3.9 0.8 5.7L0 4.9C2.1 2.8 5 1.5 8 1.5C11 1.5 13.9 2.8 16 4.9L15.2 5.7C13.3 3.9 10.8 2.8 8 2.8ZM8 5.6C6.1 5.6 4.3 6.3 3 7.6L2.2 6.8C3.7 5.3 5.8 4.3 8 4.3C10.2 4.3 12.3 5.3 13.8 6.8L13 7.6C11.7 6.3 9.9 5.6 8 5.6ZM8 8.4C6.9 8.4 6 9.3 6 10.4C6 11 6.3 11.5 6.7 11.8L8 13.1L9.3 11.8C9.7 11.5 10 11 10 10.4C10 9.3 9.1 8.4 8 8.4Z" />
        </svg>
        {/* Battery Icon */}
        <div className="flex items-center">
          <div
            className={`w-5 h-2.5 border-[1.5px] rounded-[3px] p-0.5 flex items-center ${
              dark ? 'border-white' : 'border-slate-900'
            }`}
          >
            <div
              className={`h-full w-full rounded-[1px] ${
                dark ? 'bg-white' : 'bg-slate-900'
              }`}
            />
          </div>
          <div
            className={`w-0.5 h-1 rounded-r-[1px] ml-[0.5px] ${
              dark ? 'bg-white' : 'bg-slate-900'
            }`}
          />
        </div>
      </div>
    </header>
  );
};
