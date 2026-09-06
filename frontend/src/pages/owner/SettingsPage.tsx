import React from 'react';
import { Settings, Building } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { useAuth } from '../../context/AuthContext';

export const SettingsPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System Settings</h2>
        <p className="text-sm text-slate-500">Configure global application parameters and brand configuration defaults.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <Building className="h-5 w-5 text-sky-600" /> Active Brand Profile
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          <div>
            <span className="font-semibold text-slate-500 block uppercase">Brand Name</span>
            <span className="text-base font-bold text-slate-900">{user?.brand_name || 'Zywo Franchise'}</span>
          </div>
          <div>
            <span className="font-semibold text-slate-500 block uppercase">Administrator Contact</span>
            <span className="text-sm text-slate-800">{user?.email}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
