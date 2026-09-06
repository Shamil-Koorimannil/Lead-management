import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Search, Filter, Eye, Clock, Plus } from 'lucide-react';
import { leadsService } from '../../services/leads';
import { Lead } from '../../types';
import { QualificationBadge, SalesStatusBadge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { EmptyState } from '../../components/ui/EmptyState';
import { Dialog } from '../../components/ui/Dialog';

export const SalesLeads: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [salesStatus, setSalesStatus] = useState('');
  const [qualificationStatus, setQualificationStatus] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const [newLead, setNewLead] = useState({
    name: '',
    phone: '',
    email: '',
    city: '',
    preferred_location: '',
    investment_capacity: '2500000',
    property_available: true,
    business_experience: true,
    expected_start: '3 months',
    lead_source: 'MANUAL',
  });

  const navigate = useNavigate();

  const loadLeads = async () => {
    setLoading(true);
    try {
      const res = await leadsService.getLeads({
        search: search || undefined,
        sales_status: salesStatus || undefined,
        qualification_status: qualificationStatus || undefined,
      });
      setLeads(res.results);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, [salesStatus, qualificationStatus]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadLeads();
  };

  const handleCreateLead = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await leadsService.createLead({
        ...newLead,
        investment_capacity: parseFloat(newLead.investment_capacity) || 0,
      });
      setIsCreateOpen(false);
      loadLeads();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error creating lead.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">My Assigned Leads</h2>
          <p className="text-sm text-slate-500">Manage and work your assigned franchise enquiries.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} icon={<Plus className="h-4 w-4" />}>
          Add New Lead
        </Button>
      </div>

      <Card>
        <CardContent className="p-4">
          <form onSubmit={handleSearch} className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="relative col-span-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search my leads..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            <select
              value={qualificationStatus}
              onChange={(e) => setQualificationStatus(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="">All Qualification Statuses</option>
              <option value="QUALIFIED">Qualified</option>
              <option value="REVIEW">Needs Review</option>
              <option value="NOT_QUALIFIED">Not Qualified</option>
            </select>

            <select
              value={salesStatus}
              onChange={(e) => setSalesStatus(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            >
              <option value="">All Sales Statuses</option>
              <option value="NEW">New</option>
              <option value="CONTACTED">Contacted</option>
              <option value="FOLLOW_UP">Follow Up</option>
              <option value="MEETING">Meeting</option>
              <option value="NEGOTIATION">Negotiation</option>
              <option value="CONVERTED">Converted</option>
              <option value="LOST">Lost</option>
            </select>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <LoadingSpinner text="Fetching assigned leads..." />
          ) : leads.length === 0 ? (
            <EmptyState title="No assigned leads" description="You have no leads assigned matching criteria." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase">
                  <tr>
                    <th className="px-4 py-3">Lead #</th>
                    <th className="px-4 py-3">Customer</th>
                    <th className="px-4 py-3">Location</th>
                    <th className="px-4 py-3">Investment</th>
                    <th className="px-4 py-3">Qualification</th>
                    <th className="px-4 py-3">Sales Status</th>
                    <th className="px-4 py-3">Next Follow-up</th>
                    <th className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-slate-50/50">
                      <td className="px-4 py-3.5 font-mono text-xs font-bold text-sky-700">{lead.lead_number}</td>
                      <td className="px-4 py-3.5 font-medium text-slate-900">
                        {lead.name}
                        <span className="block text-xs font-normal text-slate-400">{lead.phone}</span>
                      </td>
                      <td className="px-4 py-3.5 text-xs">{lead.city}</td>
                      <td className="px-4 py-3.5 font-semibold text-slate-900 text-xs">
                        ₹{Number(lead.investment_capacity || 0).toLocaleString()}
                      </td>
                      <td className="px-4 py-3.5">
                        <QualificationBadge status={lead.qualification_status} score={lead.qualification_score} />
                      </td>
                      <td className="px-4 py-3.5">
                        <SalesStatusBadge status={lead.sales_status} />
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-600">
                        {lead.follow_up_required && lead.next_follow_up_at ? (
                          <span className="flex items-center gap-1 font-semibold text-purple-700">
                            <Clock className="h-3.5 w-3.5" />
                            {new Date(lead.next_follow_up_at).toLocaleDateString()}
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">None</span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/sales/leads/${lead.id}`)}
                          icon={<Eye className="h-3.5 w-3.5" />}
                        >
                          Work Lead
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Lead Modal */}
      <Dialog isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Add New Lead">
        <form onSubmit={handleCreateLead} className="space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Customer Full Name</label>
            <input
              type="text"
              required
              value={newLead.name}
              onChange={(e) => setNewLead({ ...newLead, name: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Phone</label>
              <input
                type="text"
                required
                value={newLead.phone}
                onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Email</label>
              <input
                type="email"
                required
                value={newLead.email}
                onChange={(e) => setNewLead({ ...newLead, email: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">City</label>
              <input
                type="text"
                required
                value={newLead.city}
                onChange={(e) => setNewLead({ ...newLead, city: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Investment Capacity (₹)</label>
              <input
                type="number"
                required
                value={newLead.investment_capacity}
                onChange={(e) => setNewLead({ ...newLead, investment_capacity: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button type="submit">Save & Calculate Qualification</Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
