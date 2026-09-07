import React, { useEffect, useState } from 'react';
import {
  Users, CheckCircle2, AlertCircle, XCircle, TrendingUp,
  Clock, Award, ArrowUpRight, BarChart2
} from 'lucide-react';
import { dashboardService } from '../../services/dashboard';
import { OwnerDashboardData } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { Badge } from '../../components/ui/Badge';

export const OwnerDashboard: React.FC = () => {
  const [data, setData] = useState<OwnerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getOwnerDashboard()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Loading Owner Analytics..." />;
  if (!data) return <div className="text-slate-500">Failed to load owner dashboard.</div>;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Business Executive Dashboard</h2>
        <p className="text-sm text-slate-500 mt-1">High-level franchise performance, qualification distributions, and pipeline conversion analytics.</p>
      </div>

      {/* Primary KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
        <Card className="border-l-4 border-l-sky-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Total Leads</span>
              <Users className="h-4 w-4 text-sky-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-slate-900 mt-1.5 sm:mt-2">{data.total_leads}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Qualified</span>
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-emerald-700 mt-1.5 sm:mt-2">{data.qualified}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Review</span>
              <AlertCircle className="h-4 w-4 text-amber-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-amber-700 mt-1.5 sm:mt-2">{data.review}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-rose-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Disqualified</span>
              <XCircle className="h-4 w-4 text-rose-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-rose-700 mt-1.5 sm:mt-2">{data.not_qualified}</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-indigo-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Conversion</span>
              <TrendingUp className="h-4 w-4 text-indigo-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-indigo-700 mt-1.5 sm:mt-2">{data.conversion_rate}%</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between text-slate-500">
              <span className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider">Follow-ups</span>
              <Clock className="h-4 w-4 text-purple-600" />
            </div>
            <p className="text-xl sm:text-2xl font-bold text-purple-700 mt-1.5 sm:mt-2">{data.active_followups}</p>
          </CardContent>
        </Card>
      </div>

      {/* Grid Section: Sales Funnel & Lead Sources */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sales Funnel Breakdown */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-sky-600" /> Sales Funnel Progression
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.sales_funnel.map((item) => {
                const percentage = data.total_leads > 0 ? Math.round((item.count / data.total_leads) * 100) : 0;
                return (
                  <div key={item.sales_status} className="space-y-1">
                    <div className="flex justify-between text-xs font-medium text-slate-700">
                      <span>{item.sales_status.replace('_', ' ')}</span>
                      <span>{item.count} ({percentage}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-sky-600 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Lead Sources */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5 text-emerald-600" /> Lead Acquisition Sources
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {data.lead_sources.map((item) => (
                <div key={item.lead_source} className="p-3 bg-slate-50 rounded-lg border border-slate-200/60">
                  <span className="text-xs font-semibold text-slate-500 block uppercase">{item.lead_source}</span>
                  <span className="text-xl font-bold text-slate-900">{item.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Performance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Sales Team Performance Overview</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase">
                <tr>
                  <th className="px-6 py-3 whitespace-nowrap">Team Member</th>
                  <th className="px-6 py-3 whitespace-nowrap">Role</th>
                  <th className="px-6 py-3 whitespace-nowrap">Assigned Leads</th>
                  <th className="px-6 py-3 whitespace-nowrap">Qualified Leads</th>
                  <th className="px-6 py-3 whitespace-nowrap">Converted Leads</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.team_performance.map((member) => (
                  <tr key={member.id} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-semibold text-slate-900 whitespace-nowrap">
                      {member.name}
                      <span className="block text-xs font-normal text-slate-400">{member.email}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant="info">{member.role.replace('_', ' ')}</Badge>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-800 whitespace-nowrap">{member.assigned_leads}</td>
                    <td className="px-6 py-4 font-semibold text-emerald-700 whitespace-nowrap">{member.qualified_leads}</td>
                    <td className="px-6 py-4 font-semibold text-indigo-700 whitespace-nowrap">{member.converted_leads}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

    </div>
  );
};
