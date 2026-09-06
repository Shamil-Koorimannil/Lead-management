import React from 'react';

export const LoadingSkeleton: React.FC<{ rows?: number }> = ({ rows = 4 }) => (
  <div className="space-y-3 animate-pulse p-4">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="h-10 bg-slate-200/70 rounded-lg w-full" />
    ))}
  </div>
);

export const LoadingSpinner: React.FC<{ text?: string }> = ({ text = "Loading data..." }) => (
  <div className="flex flex-col items-center justify-center p-12 space-y-3">
    <div className="w-8 h-8 border-4 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
    <p className="text-sm font-medium text-slate-500">{text}</p>
  </div>
);
