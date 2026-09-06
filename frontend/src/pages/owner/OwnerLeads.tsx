import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Search, Filter, Plus, Eye, UserPlus, Trash2, ChevronLeft, ChevronRight } from 'lucide-react';
import { leadsService, LeadFilterParams } from '../../services/leads';
import { usersService } from '../../services/users';
import { Lead, User } from '../../types';
import { QualificationBadge, SalesStatusBadge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Dialog } from '../../components/ui/Dialog';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { EmptyState } from '../../components/ui/EmptyState';
import { LoadingSpinner } from '../../components/ui/LoadingState';

export const OwnerLeads: React.FC = () => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter state
  const [search, setSearch] = useState('');
  const [qualificationStatus, setQualificationStatus] = useState('');
  const [salesStatus, setSalesStatus] = useState('');
  const [leadSource, setLeadSource] = useState('');
  const [page, setPage] = useState(1);

  // Modals state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isAssignOpen, setIsAssignOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [assignAgentId, setAssignAgentId] = useState<number | ''>('');

  // New Lead form state
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
      const params: LeadFilterParams = { page };
      if (search) params.search = search;
      if (qualificationStatus) params.qualification_status = qualificationStatus;
      if (salesStatus) params.sales_status = salesStatus;
      if (leadSource) params.lead_source = leadSource;

      const res = await leadsService.getLeads(params);
      setLeads(res.results);
      setTotalCount(res.count);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeads();
  }, [page, qualificationStatus, salesStatus, leadSource]);

  useEffect(() => {
    usersService.getUsers().then(setUsers);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
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

  const handleAssignLead = async () => {
    if (!selectedLead || !assignAgentId) return;
    try {
      await leadsService.assignLead(selectedLead.id, Number(assignAgentId));
      setIsAssignOpen(false);
      loadLeads();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error assigning lead.');
    }
  };

  const handleDeleteLead = async () => {
    if (!selectedLead) return;
    try {
      await leadsService.deleteLead(selectedLead.id);
      setIsDeleteOpen(false);
      loadLeads();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error deleting lead.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Brand Lead Management</h2>
          <p className="text-sm text-slate-500">View, search, filter, assign, and manage all franchise enquiries across the brand.</p>
        </div>
        <Button onClick={() => setIsCreateOpen(true)} icon={<Plus className="h-4 w-4" />}>
          Create New Lead
        </Button>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <CardContent className="p-4">
          <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search lead #, name, phone..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
              />
            </div>

            <select
              value={qualificationStatus}
              onChange={(e) => setQualificationStatus(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            >
              <option value="">All Qualification Statuses</option>
              <option value="QUALIFIED">Qualified</option>
              <option value="REVIEW">Needs Review</option>
              <option value="NOT_QUALIFIED">Not Qualified</option>
            </select>

            <select
              value={salesStatus}
              onChange={(e) => setSalesStatus(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:ring-2 focus:ring-sky-500 focus:outline-none"
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

            <select
              value={leadSource}
              onChange={(e) => setLeadSource(e.target.value)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-700 focus:ring-2 focus:ring-sky-500 focus:outline-none"
            >
              <option value="">All Lead Sources</option>
              <option value="MANUAL">Manual</option>
              <option value="TEST">Test</option>
              <option value="WHATSAPP">WhatsApp</option>
              <option value="WEBSITE">Website</option>
              <option value="INSTAGRAM">Instagram</option>
              <option value="FACEBOOK">Facebook</option>
            </select>

            <Button type="submit" variant="secondary" size="sm" icon={<Filter className="h-3.5 w-3.5" />}>
              Filter
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Main Leads Table */}
      <Card>
        <CardContent className="p-0">
          {loading ? (
            <LoadingSpinner text="Fetching brand leads..." />
          ) : leads.length === 0 ? (
            <EmptyState title="No leads found" description="No leads match your search or filter parameters." />
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
                    <th className="px-4 py-3">Assigned To</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-slate-50/50">
                      <td className="px-4 py-3.5 font-mono text-xs font-bold text-sky-700">
                        {lead.lead_number}
                      </td>
                      <td className="px-4 py-3.5 font-medium text-slate-900">
                        {lead.name}
                        <span className="block text-xs font-normal text-slate-400">{lead.phone}</span>
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-700">{lead.city}</td>
                      <td className="px-4 py-3.5 font-semibold text-slate-900 text-xs">
                        ₹{Number(lead.investment_capacity || 0).toLocaleString()}
                      </td>
                      <td className="px-4 py-3.5">
                        <QualificationBadge status={lead.qualification_status} score={lead.qualification_score} />
                      </td>
                      <td className="px-4 py-3.5">
                        <SalesStatusBadge status={lead.sales_status} />
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-600 font-medium">
                        {lead.assigned_to_name || <span className="text-slate-400 italic">Unassigned</span>}
                      </td>
                      <td className="px-4 py-3.5 text-right space-x-1">
                        <button
                          onClick={() => navigate(`/owner/leads/${lead.id}`)}
                          className="p-1.5 text-slate-500 hover:text-sky-600 hover:bg-sky-50 rounded-md transition-colors"
                          title="View Details"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => { setSelectedLead(lead); setIsAssignOpen(true); }}
                          className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-md transition-colors"
                          title="Assign Lead"
                        >
                          <UserPlus className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => { setSelectedLead(lead); setIsDeleteOpen(true); }}
                          className="p-1.5 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
                          title="Delete Lead"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-2">
        <span>Total Leads: {totalCount}</span>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage(page - 1)}
            icon={<ChevronLeft className="h-4 w-4" />}
          >
            Previous
          </Button>
          <span className="font-semibold">Page {page}</span>
          <Button
            size="sm"
            variant="outline"
            disabled={page * 25 >= totalCount}
            onClick={() => setPage(page + 1)}
            icon={<ChevronRight className="h-4 w-4" />}
          >
            Next
          </Button>
        </div>
      </div>

      {/* Create Lead Modal */}
      <Dialog isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Create New Lead">
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
              <label className="font-semibold text-slate-700 block mb-1">Phone Number</label>
              <input
                type="text"
                required
                value={newLead.phone}
                onChange={(e) => setNewLead({ ...newLead, phone: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Email Address</label>
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
              <label className="font-semibold text-slate-700 block mb-1">Preferred Location</label>
              <input
                type="text"
                value={newLead.preferred_location}
                onChange={(e) => setNewLead({ ...newLead, preferred_location: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
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
          <div className="flex items-center gap-6 pt-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newLead.property_available}
                onChange={(e) => setNewLead({ ...newLead, property_available: e.target.checked })}
              />
              <span>Property Available</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={newLead.business_experience}
                onChange={(e) => setNewLead({ ...newLead, business_experience: e.target.checked })}
              />
              <span>Business Experience</span>
            </label>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
            <Button type="submit">Create Lead & Calculate Score</Button>
          </div>
        </form>
      </Dialog>

      {/* Assign Lead Modal */}
      <Dialog isOpen={isAssignOpen} onClose={() => setIsAssignOpen(false)} title={`Assign Lead ${selectedLead?.lead_number}`}>
        <div className="space-y-4 text-xs">
          <p className="text-slate-600">Select a salesperson from your team to handle this lead:</p>
          <select
            value={assignAgentId}
            onChange={(e) => setAssignAgentId(Number(e.target.value))}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg"
          >
            <option value="">Select Salesperson...</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.full_name} ({u.role.replace('_', ' ')})</option>
            ))}
          </select>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setIsAssignOpen(false)}>Cancel</Button>
            <Button onClick={handleAssignLead}>Assign Lead</Button>
          </div>
        </div>
      </Dialog>

      {/* Delete Lead Modal */}
      <Dialog isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} title="Confirm Lead Deletion">
        <div className="space-y-4 text-xs">
          <p className="text-slate-700 font-medium">
            Are you sure you want to permanently delete lead <strong className="text-rose-600">{selectedLead?.lead_number}</strong>?
          </p>
          <p className="text-slate-500">This action cannot be undone.</p>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setIsDeleteOpen(false)}>Cancel</Button>
            <Button variant="danger" onClick={handleDeleteLead}>Delete Permanently</Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
};
