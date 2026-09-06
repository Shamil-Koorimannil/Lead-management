import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, MapPin, Award } from 'lucide-react';
import { dashboardService } from '../../services/dashboard';
import { OwnerDashboardData } from '../../types';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/LoadingState';

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<OwnerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardService.getOwnerDashboard()
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner text="Calculating Analytics..." />;
  if (!data) return <div>Failed to load analytics data.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Business Intelligence & Analytics</h2>
        <p className="text-sm text-slate-500">Deep-dive breakdown into geographic locations, lead sources, conversion rates, and average qualification scores.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-indigo-600" /> Conversion Ratio
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center py-6">
            <p className="text-4xl font-extrabold text-indigo-700">{data.conversion_rate}%</p>
            <p className="text-xs text-slate-500 mt-1">Converted vs Total Leads</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Award className="h-4 w-4 text-emerald-600" /> Average Qualification Score
            </CardTitle>
          </CardHeader>
          <CardContent className="text-center py-6">
            <p className="text-4xl font-extrabold text-emerald-700">{data.avg_qualification_score} <span className="text-sm font-normal text-slate-400">/ 100</span></p>
            <p className="text-xs text-slate-500 mt-1">Across all brand leads</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <MapPin className="h-4 w-4 text-sky-600" /> Top Location Demand
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {data.locations.map((loc) => (
              <div key={loc.city} className="flex justify-between items-center text-xs">
                <span className="font-semibold text-slate-800">{loc.city}</span>
                <span className="font-mono text-slate-500">{loc.count} leads</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
