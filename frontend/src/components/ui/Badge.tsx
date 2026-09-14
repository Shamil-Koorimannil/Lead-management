import React from 'react';
import { QualificationStatus, SalesStatus } from '../../types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'qualified' | 'review' | 'not_qualified' | 'info' | 'secondary' | 'outline' | 'danger';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const baseStyle = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide transition-colors";
  
  const variants = {
    default: "bg-slate-100 text-slate-800 border border-slate-200",
    qualified: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    review: "bg-amber-50 text-amber-700 border border-amber-200",
    not_qualified: "bg-rose-50 text-rose-700 border border-rose-200",
    info: "bg-sky-50 text-sky-700 border border-sky-200",
    secondary: "bg-indigo-50 text-indigo-700 border border-indigo-200",
    outline: "border border-slate-300 text-slate-700",
    danger: "bg-rose-100 text-rose-800 border border-rose-300",
  };

  return (
    <span className={`${baseStyle} ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

export const QualificationBadge: React.FC<{ status: QualificationStatus; score?: number }> = ({ status, score }) => {
  if (status === 'QUALIFIED') {
    return <Badge variant="qualified">QUALIFIED {score !== undefined ? `(${score})` : ''}</Badge>;
  }
  if (status === 'REVIEW') {
    return <Badge variant="review">NEEDS REVIEW {score !== undefined ? `(${score})` : ''}</Badge>;
  }
  return <Badge variant="not_qualified">NOT QUALIFIED {score !== undefined ? `(${score})` : ''}</Badge>;
};

export const SalesStatusBadge: React.FC<{ status: SalesStatus }> = ({ status }) => {
  const styles: Record<SalesStatus, 'default' | 'info' | 'review' | 'qualified' | 'danger'> = {
    NEW: 'default',
    CONTACTED: 'info',
    FOLLOW_UP: 'review',
    MEETING: 'info',
    NEGOTIATION: 'review',
    CONVERTED: 'qualified',
    LOST: 'danger',
  };
  return <Badge variant={styles[status] || 'default'}>{status.replace('_', ' ')}</Badge>;
};

export const TemperatureBadge: React.FC<{ temperature?: string | null }> = ({ temperature }) => {
  if (!temperature) {
    return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-500 border border-slate-200">Not Yet Classified</span>;
  }

  const styles: Record<string, string> = {
    HOT: "bg-amber-500 text-white font-bold border border-amber-600 shadow-sm",
    WARM: "bg-amber-100 text-amber-800 font-semibold border border-amber-300",
    COLD: "bg-sky-100 text-sky-800 font-semibold border border-sky-300",
    LONG_TERM: "bg-purple-100 text-purple-800 font-semibold border border-purple-300",
    DISQUALIFIED: "bg-rose-100 text-rose-800 font-semibold border border-rose-300",
  };

  const labels: Record<string, string> = {
    HOT: "🔥 HOT",
    WARM: "🟠 WARM",
    COLD: "🔵 COLD",
    LONG_TERM: "🟣 LONG TERM",
    DISQUALIFIED: "🔴 DISQUALIFIED",
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs tracking-wide transition-colors ${styles[temperature] || 'bg-slate-100 text-slate-800'}`}>
      {labels[temperature] || temperature}
    </span>
  );
};

