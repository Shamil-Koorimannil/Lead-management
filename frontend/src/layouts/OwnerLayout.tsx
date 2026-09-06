import React from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';


import {
  LayoutDashboard, Users, ShieldCheck, BarChart3, Settings,
  Zap, LogOut, Building2, ChevronRight, UserCircle
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/ui/Badge';

export const OwnerLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/owner/dashboard', icon: LayoutDashboard },
    { label: 'All Leads', path: '/owner/leads', icon: Users },
    { label: 'Analytics', path: '/owner/analytics', icon: BarChart3 },
    { label: 'Team', path: '/owner/team', icon: UserCircle },
    { label: 'Qualification Rules', path: '/owner/rules', icon: ShieldCheck },
    { label: 'Automations', path: '/owner/automations', icon: Zap },
    { label: 'Settings', path: '/owner/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-100 flex font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col fixed inset-y-0 z-30 shadow-xl">
        {/* Brand Header */}
        <div className="p-6 border-b border-slate-800 flex items-center gap-3">
          <div className="p-2 bg-sky-600 rounded-lg text-white">
            <Building2 className="h-6 w-6" />
          </div>
          <div>
            <h1 className="font-bold text-white tracking-wide text-base leading-tight">
              {user?.brand_name || 'Brand Control'}
            </h1>
            <p className="text-xs text-sky-400 font-medium mt-0.5">Owner Portal</p>
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
                    ? 'bg-sky-600 text-white shadow-md'
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
              <Badge variant="qualified" className="mt-1 text-[10px] py-0 px-2">
                {user?.role}
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
            <span>Brand Owner</span>
            <ChevronRight className="h-4 w-4 text-slate-400" />
            <span className="text-slate-900 capitalize">
              {location.pathname.split('/')[2] || 'Dashboard'}
            </span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs bg-sky-50 text-sky-700 px-3 py-1 rounded-full font-semibold border border-sky-200">
              System Active: Phase 1 MVP
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
