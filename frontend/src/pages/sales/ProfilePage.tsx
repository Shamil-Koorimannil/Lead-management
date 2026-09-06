import React from 'react';
import { UserCircle, Shield, Mail } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Sales User Profile</h2>
        <p className="text-sm text-slate-500">Your account profile and role details.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <UserCircle className="h-5 w-5 text-emerald-600" /> User Credentials & Role
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-xs">
          <div>
            <span className="font-semibold text-slate-400 block uppercase">Full Name</span>
            <span className="text-base font-bold text-slate-900">{user?.full_name}</span>
          </div>

          <div>
            <span className="font-semibold text-slate-400 block uppercase">Email Address</span>
            <span className="text-sm text-slate-800 flex items-center gap-1 mt-0.5 font-mono">
              <Mail className="h-3.5 w-3.5 text-slate-400" /> {user?.email}
            </span>
          </div>

          <div>
            <span className="font-semibold text-slate-400 block uppercase">Brand Assigned</span>
            <span className="text-sm text-slate-800 font-semibold">{user?.brand_name || 'Zywo Franchise'}</span>
          </div>

          <div>
            <span className="font-semibold text-slate-400 block uppercase mb-1">Business Role</span>
            <Badge variant="info">{user?.role.replace('_', ' ')}</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
