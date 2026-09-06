import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Clock, CheckCircle2, AlertTriangle, Eye } from 'lucide-react';
import { leadsService } from '../../services/leads';
import { Lead } from '../../types';
import { QualificationBadge, SalesStatusBadge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { EmptyState } from '../../components/ui/EmptyState';

export const FollowUpsPage: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overdue' | 'upcoming'>('overdue');
  const navigate = useNavigate();

  const loadFollowUps = async () => {
    setLoading(true);
    try {
      const res = await leadsService.getLeads({ follow_up_required: true });
      setLeads(res.results);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFollowUps();
  }, []);

  const handleComplete = async (id: number) => {
    try {
      await leadsService.completeFollowUp(id);
      loadFollowUps();
    } catch {
      alert('Error completing follow-up.');
    }
  };

  const now = new Date();
  const overdueList = leads.filter((l) => l.next_follow_up_at && new Date(l.next_follow_up_at) < now);
  const upcomingList = leads.filter((l) => l.next_follow_up_at && new Date(l.next_follow_up_at) >= now);

  const currentList = activeTab === 'overdue' ? overdueList : upcomingList;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Follow-Up Action Center</h2>
        <p className="text-sm text-slate-500">Track and execute scheduled customer follow-up calls, meetings, and emails.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-2 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('overdue')}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
            activeTab === 'overdue' ? 'bg-rose-600 text-white shadow-sm' : 'bg-white text-slate-700 hover:bg-slate-50'
          }`}
        >
          <AlertTriangle className="h-4 w-4" /> Overdue / Due Now ({overdueList.length})
        </button>
        <button
          onClick={() => setActiveTab('upcoming')}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
            activeTab === 'upcoming' ? 'bg-purple-600 text-white shadow-sm' : 'bg-white text-slate-700 hover:bg-slate-50'
          }`}
        >
          <Clock className="h-4 w-4" /> Upcoming Follow-ups ({upcomingList.length})
        </button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <LoadingSpinner text="Loading follow-up tasks..." />
          ) : currentList.length === 0 ? (
            <EmptyState title="No follow-ups" description={`No ${activeTab} follow-ups scheduled.`} />
          ) : (
            <div className="divide-y divide-slate-100">
              {currentList.map((lead) => (
                <div key={lead.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-sky-700">{lead.lead_number}</span>
                      <span className="font-semibold text-slate-900 text-sm">{lead.name}</span>
                      <QualificationBadge status={lead.qualification_status} />
                      <SalesStatusBadge status={lead.sales_status} />
                    </div>
                    <p className="text-xs text-slate-600">
                      Scheduled: <strong className="font-mono">{lead.next_follow_up_at ? new Date(lead.next_follow_up_at).toLocaleString() : ''}</strong> ({lead.follow_up_type})
                    </p>
                    {lead.follow_up_note && (
                      <p className="text-xs text-slate-500 bg-slate-50 p-2 rounded border border-slate-200/60 max-w-xl">
                        "{lead.follow_up_note}"
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleComplete(lead.id)}
                      icon={<CheckCircle2 className="h-4 w-4" />}
                    >
                      Complete
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/sales/leads/${lead.id}`)}
                      icon={<Eye className="h-3.5 w-3.5" />}
                    >
                      View
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
