import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Building2, Lock, Mail, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/Button';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const loggedUser = await login(email, password);
      if (loggedUser.role === 'BRAND_OWNER') {
        navigate('/owner/dashboard');
      } else {
        navigate('/sales/dashboard');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (emailVal: string) => {
    setEmail(emailVal);
    setPassword('Password123!');
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Top Header */}
        <div className="bg-slate-950 p-8 text-center text-white border-b border-slate-800">
          <div className="inline-flex p-3 bg-sky-600 rounded-xl text-white shadow-lg mb-3">
            <Building2 className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-bold tracking-tight">Lead Management & Enquiry Platform</h2>
          <p className="text-xs text-slate-400 mt-1">Sign in to access your role-based workspace</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          {error && (
            <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg font-medium">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="owner@zywolabs.com"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 h-4 w-4 text-slate-400" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-white transition-all"
              />
            </div>
          </div>

          <Button type="submit" isLoading={loading} className="w-full py-3" icon={<ArrowRight className="h-4 w-4" />}>
            Sign In
          </Button>

          {/* Development Login Presets */}
          <div className="pt-4 border-t border-slate-100">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-sky-600" /> Demo Quick Login Presets
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('owner@zywolabs.com')}
                className="px-2 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-medium truncate"
              >
                Owner
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('manager@zywolabs.com')}
                className="px-2 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-medium truncate"
              >
                Manager
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('agent1@zywolabs.com')}
                className="px-2 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-800 rounded font-medium truncate"
              >
                Agent
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
