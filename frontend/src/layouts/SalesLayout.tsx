import React from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';

import {
  LayoutDashboard, Users, Clock, UserCheck, LogOut,
  Building2, ChevronRight, UserCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/ui/Badge';

export const SalesLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/sales/dashboard', icon: LayoutDashboard },
    { label: 'My Leads', path: '/sales/leads', icon: Users },
    { label: 'Follow-ups', path: '/sales/followups', icon: Clock },
    { label: 'Profile', path: '/sales/profile', icon: UserCircle },
  ];

  return (
    <div className="min-h-screen bg-slate-100 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col fixed inset-y-0 z-30 shadow-xl">
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-emerald-600 rounded-lg text-white">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-bold text-white tracking-wide text-base leading-tight">
              {user?.brand_name || 'Sales Workspace'}
            </h1>
            <p className="text-xs text-emerald-400 font-medium mt-0.5">Sales Portal</p>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                }`}
              >
                <Icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer User Info */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          <div className="flex items-center justify-between">
            <div className="truncate pr-2">
              <p className="text-sm font-semibold text-white truncate">{user?.full_name}</p>
              <Badge variant="info" className="mt-1 text-[10px] py-0 px-2">
                {user?.role.replace('_', ' ')}
              </Badge>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 pl-64 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between sticky top-0 z-20 shadow-2xs">
          <div className="flex items-center gap-2 text-sm text-slate-500 font-medium">
            <span>Sales Workspace</span>
            <ChevronRight className="h-4 w-4 text-slate-400" />
            <span className="text-slate-900 capitalize">
              {location.pathname.split('/')[2] || 'Dashboard'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full font-semibold border border-emerald-200">
              Operational Workspace Active
            </span>
          </div>
        </header>

        <main className="p-8 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
