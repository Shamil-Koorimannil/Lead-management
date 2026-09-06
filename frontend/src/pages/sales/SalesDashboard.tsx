import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  Clock, AlertTriangle, CheckCircle2, Phone, Calendar,
  ArrowRight, Users, Star, Eye
} from 'lucide-react';
import { dashboardService } from '../../services/dashboard';
import { leadsService } from '../../services/leads';
import { SalesDashboardData, Lead } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { QualificationBadge, SalesStatusBadge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';

export const SalesDashboard: React.FC = () => {
  const [data, setData] = useState<SalesDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await dashboardService.getSalesDashboard();
      setData(res);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCompleteFollowUp = async (leadId: number) => {
    try {
      await leadsService.completeFollowUp(leadId);
      loadData();
    } catch {
      alert('Error completing follow-up.');
    }
  };

  if (loading) return <LoadingSpinner text="Loading Sales Action Dashboard..." />;
  if (!data) return <div className="text-slate-500">Failed to load sales dashboard.</div>;

  return (
    <div className="space-y-8">
      {/* Action Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Today's Sales Action Center</h2>
        <p className="text-sm text-slate-500 mt-1">Operational view of assigned leads requiring contact, follow-ups due today, and recently qualified prospects.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Overdue / Due Today</span>
              <AlertTriangle className="h-4 w-4 text-amber-600" />
            </div>
            <p className="text-2xl font-bold text-amber-700 mt-2">{data.metrics.followups_due}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Qualified Leads</span>
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            </div>
            <p className="text-2xl font-bold text-emerald-700 mt-2">{data.metrics.qualified_leads}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-sky-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider">New Leads</span>
              <Users className="h-4 w-4 text-sky-600" />
            </div>
            <p className="text-2xl font-bold text-sky-700 mt-2">{data.metrics.new_leads}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-indigo-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Meetings</span>
              <Calendar className="h-4 w-4 text-indigo-600" />
            </div>
            <p className="text-2xl font-bold text-indigo-700 mt-2">{data.metrics.meetings_today}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Priority Leads</span>
              <Star className="h-4 w-4 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-purple-700 mt-2">{data.metrics.priority_leads}</p>
          </CardContent>
        </Card>
      </div>

      {/* Grid: Overdue Follow-ups & Priority Qualified Leads */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overdue Follow-ups */}
        <Card className="border-t-4 border-t-rose-600">
          <CardHeader>
            <CardTitle className="text-sm flex items-center justify-between">
              <span className="flex items-center gap-2 text-rose-700 font-bold">
                <AlertTriangle className="h-4 w-4" /> Overdue Follow-ups ({data.overdue_followups.length})
              </span>
              <button
                onClick={() => navigate('/sales/followups')}
                className="text-xs text-sky-600 hover:underline font-normal"
              >
                View all
              </button>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {data.overdue_followups.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 italic">Great job! No overdue follow-ups.</div>
            ) : (
              <div className="divide-y divide-slate-100">
                {data.overdue_followups.map((lead) => (
                  <div key={lead.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-sky-700">{lead.lead_number}</span>
                        <span className="font-semibold text-slate-900 text-sm">{lead.name}</span>
                        <QualificationBadge status={lead.qualification_status} />
                      </div>
                      <p className="text-xs text-slate-500">
                        Scheduled: <strong className="text-rose-600">{lead.next_follow_up_at ? new Date(lead.next_follow_up_at).toLocaleString() : 'N/A'}</strong> ({lead.follow_up_type})
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => handleCompleteFollowUp(lead.id)}
                      >
                        Complete
                      </Button>
                      <button
                        onClick={() => navigate(`/sales/leads/${lead.id}`)}
                        className="p-1.5 text-slate-400 hover:text-slate-700"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recently Qualified Assigned Leads */}
        <Card className="border-t-4 border-t-emerald-600">
          <CardHeader>
            <CardTitle className="text-sm flex items-center justify-between">
              <span className="flex items-center gap-2 text-emerald-700 font-bold">
                <CheckCircle2 className="h-4 w-4" /> High-Priority Qualified Leads
              </span>
              <button
                onClick={() => navigate('/sales/leads')}
                className="text-xs text-sky-600 hover:underline font-normal"
              >
                View all
              </button>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {data.recently_qualified.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 italic">No qualified leads assigned yet.</div>
            ) : (
              <div className="divide-y divide-slate-100">
                {data.recently_qualified.map((lead) => (
                  <div key={lead.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-sky-700">{lead.lead_number}</span>
                        <span className="font-semibold text-slate-900 text-sm">{lead.name}</span>
                        <span className="text-xs text-slate-500">({lead.city})</span>
                      </div>
                      <p className="text-xs text-slate-600 font-medium">
                        Investment: ₹{Number(lead.investment_capacity || 0).toLocaleString()} • Score: {lead.qualification_score}/100
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/sales/leads/${lead.id}`)}
                      icon={<ArrowRight className="h-3.5 w-3.5" />}
                    >
                      Action
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
