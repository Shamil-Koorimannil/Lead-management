import React from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No data found",
  description = "There are no records to display right now.",
  action,
  icon = <Inbox className="h-10 w-10 text-slate-400" />,
}) => (
  <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200 my-4">
    <div className="p-3 bg-white rounded-full shadow-xs mb-3 border border-slate-100">
      {icon}
    </div>
    <h4 className="text-base font-semibold text-slate-800 mb-1">{title}</h4>
    <p className="text-sm text-slate-500 max-w-sm mb-4">{description}</p>
    {action && <div>{action}</div>}
  </div>
);
