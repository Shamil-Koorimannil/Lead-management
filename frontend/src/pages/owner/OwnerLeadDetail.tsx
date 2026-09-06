import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import {
  ArrowLeft, Phone, Mail, MapPin, DollarSign, Calendar,
  ShieldCheck, MessageSquare, StickyNote, Activity, UserPlus, Clock
} from 'lucide-react';
import { leadsService } from '../../services/leads';
import { conversationsService } from '../../services/conversations';
import { usersService } from '../../services/users';
import { Lead, Conversation, LeadNote, User, SalesStatus } from '../../types';
import { QualificationBadge, SalesStatusBadge, Badge } from '../../components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { LoadingSpinner } from '../../components/ui/LoadingState';

export const OwnerLeadDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [lead, setLead] = useState<Lead | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // New Note state
  const [newNoteContent, setNewNoteContent] = useState('');
  const [submittingNote, setSubmittingNote] = useState(false);

  const loadDetail = async () => {
    if (!id) return;
    try {
      const leadData = await leadsService.getLeadById(Number(id));
      setLead(leadData);
      const convsData = await conversationsService.getConversations(Number(id));
      setConversations(convsData);
      const notesData = await conversationsService.getLeadNotes(Number(id));
      setNotes(notesData);
    } catch {
      navigate('/owner/leads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
    usersService.getUsers().then(setUsers);
  }, [id]);

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id || !newNoteContent.trim()) return;
    setSubmittingNote(true);
    try {
      await conversationsService.createNote(Number(id), newNoteContent);
      setNewNoteContent('');
      loadDetail();
    } finally {
      setSubmittingNote(false);
    }
  };

  const handleSalesStatusChange = async (newStatus: SalesStatus) => {
    if (!lead) return;
    try {
      const updated = await leadsService.updateLead(lead.id, { sales_status: newStatus });
      setLead(updated);
    } catch (err: any) {
      alert('Error updating status');
    }
  };

  const handleAssignChange = async (agentId: number) => {
    if (!lead) return;
    try {
      const updated = await leadsService.assignLead(lead.id, agentId);
      setLead(updated);
    } catch (err: any) {
      alert('Error assigning lead');
    }
  };

  if (loading || !lead) return <LoadingSpinner text="Loading Lead Detail..." />;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/owner/leads')}
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to All Leads
        </button>

        <div className="flex items-center gap-3">
          <SalesStatusBadge status={lead.sales_status} />
          <QualificationBadge status={lead.qualification_status} score={lead.qualification_score} />
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2-Column Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Hero Banner */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-100 pb-4 mb-4">
                <div>
                  <span className="text-xs font-mono font-bold text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md border border-sky-200">
                    {lead.lead_number}
                  </span>
                  <h1 className="text-xl font-bold text-slate-900 mt-2">{lead.name}</h1>
                </div>

                <div className="flex items-center gap-2">
                  <select
                    value={lead.sales_status}
                    onChange={(e) => handleSalesStatusChange(e.target.value as SalesStatus)}
                    className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800"
                  >
                    <option value="NEW">NEW</option>
                    <option value="CONTACTED">CONTACTED</option>
                    <option value="FOLLOW_UP">FOLLOW UP</option>
                    <option value="MEETING">MEETING</option>
                    <option value="NEGOTIATION">NEGOTIATION</option>
                    <option value="CONVERTED">CONVERTED</option>
                    <option value="LOST">LOST</option>
                  </select>
                </div>
              </div>

              {/* Lead Details Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Phone</span>
                  <span className="font-semibold text-slate-900 flex items-center gap-1 mt-0.5">
                    <Phone className="h-3.5 w-3.5 text-slate-400" /> {lead.phone}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Email</span>
                  <span className="font-semibold text-slate-900 flex items-center gap-1 mt-0.5 truncate">
                    <Mail className="h-3.5 w-3.5 text-slate-400" /> {lead.email}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Location</span>
                  <span className="font-semibold text-slate-900 flex items-center gap-1 mt-0.5">
                    <MapPin className="h-3.5 w-3.5 text-slate-400" /> {lead.city} ({lead.preferred_location})
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Investment Capacity</span>
                  <span className="font-bold text-slate-900 mt-0.5 block">
                    ₹{Number(lead.investment_capacity || 0).toLocaleString()}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Property Available</span>
                  <span className="font-semibold text-slate-900 mt-0.5 block">
                    {lead.property_available ? 'Yes' : 'No'}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block uppercase">Expected Start</span>
                  <span className="font-semibold text-slate-900 mt-0.5 block">
                    {lead.expected_start || 'N/A'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Qualification Engine Calculation Card */}
          <Card className="border-l-4 border-l-sky-600">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <ShieldCheck className="h-5 w-5 text-sky-600" /> Authoritative Qualification Breakdown (Django Server Calculation)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div>
                  <span className="font-semibold text-slate-700 block">Calculated Score</span>
                  <span className="text-xl font-bold text-slate-900">{lead.qualification_score} / 100</span>
                </div>
                <QualificationBadge status={lead.qualification_status} />
              </div>
              <div>
                <span className="font-semibold text-slate-700 block mb-1">Qualification Explanation Reason:</span>
                <p className="text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200/60 leading-relaxed font-mono">
                  {lead.qualification_reason || 'No breakdown available.'}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Conversations Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <MessageSquare className="h-5 w-5 text-indigo-600" /> Customer Conversation History
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {conversations.length === 0 ? (
                <p className="text-xs text-slate-500 italic">No customer conversations stored yet for this lead.</p>
              ) : (
                conversations.map((conv) => (
                  <div key={conv.id} className="space-y-3">
                    <div className="flex items-center justify-between text-xs text-slate-500 border-b border-slate-100 pb-1">
                      <span className="font-semibold text-slate-800">Channel: {conv.channel}</span>
                      <span>Status: {conv.status}</span>
                    </div>
                    <div className="space-y-2">
                      {conv.messages.map((msg) => (
                        <div
                          key={msg.id}
                          className={`p-3 rounded-xl text-xs max-w-md ${
                            msg.direction === 'OUTBOUND'
                              ? 'ml-auto bg-sky-600 text-white rounded-br-none'
                              : 'mr-auto bg-slate-100 text-slate-800 rounded-bl-none'
                          }`}
                        >
                          <p>{msg.message}</p>
                          <span className={`text-[10px] block mt-1 ${msg.direction === 'OUTBOUND' ? 'text-sky-200' : 'text-slate-400'}`}>
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Internal Notes Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <StickyNote className="h-5 w-5 text-amber-600" /> Internal Notes Feed (Staff Only)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleAddNote} className="space-y-2">
                <textarea
                  required
                  rows={2}
                  placeholder="Add an internal note about this customer..."
                  value={newNoteContent}
                  onChange={(e) => setNewNoteContent(e.target.value)}
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
                <div className="flex justify-end">
                  <Button type="submit" size="sm" isLoading={submittingNote}>Add Internal Note</Button>
                </div>
              </form>

              <div className="space-y-3 pt-2">
                {notes.map((n) => (
                  <div key={n.id} className="p-3 bg-amber-50/60 border border-amber-200/80 rounded-lg text-xs space-y-1">
                    <div className="flex justify-between font-semibold text-slate-800">
                      <span>{n.author_name}</span>
                      <span className="text-[10px] text-slate-400">{new Date(n.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-slate-700">{n.content}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar Column */}
        <div className="space-y-6">
          {/* Assignment Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <UserPlus className="h-4 w-4 text-sky-600" /> Lead Assignment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div>
                <label className="text-slate-500 font-semibold block mb-1">Assigned Salesperson</label>
                <select
                  value={lead.assigned_to || ''}
                  onChange={(e) => handleAssignChange(Number(e.target.value))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg font-medium text-slate-800"
                >
                  <option value="">Unassigned</option>
                  {users.map((u) => (
                    <option key={u.id} value={u.id}>{u.full_name} ({u.role.replace('_', ' ')})</option>
                  ))}
                </select>
              </div>
            </CardContent>
          </Card>

          {/* Follow up Card */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Clock className="h-4 w-4 text-purple-600" /> Scheduled Follow-Up
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              {lead.follow_up_required ? (
                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg space-y-1">
                  <div className="flex justify-between font-bold text-purple-900">
                    <span>{lead.follow_up_type || 'Follow Up'}</span>
                    <span>{lead.next_follow_up_at ? new Date(lead.next_follow_up_at).toLocaleString() : ''}</span>
                  </div>
                  {lead.follow_up_note && <p className="text-purple-700">{lead.follow_up_note}</p>}
                </div>
              ) : (
                <p className="text-slate-500 italic">No follow-up currently scheduled.</p>
              )}
            </CardContent>
          </Card>

          {/* Activity Log Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Activity className="h-4 w-4 text-emerald-600" /> Audit Activity History
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 max-h-96 overflow-y-auto space-y-3">
              {lead.activities?.map((act) => (
                <div key={act.id} className="border-l-2 border-slate-300 pl-3 space-y-0.5 text-xs">
                  <span className="font-semibold text-slate-800 block">{act.action.replace('_', ' ')}</span>
                  <p className="text-slate-600">{act.description}</p>
                  <span className="text-[10px] text-slate-400 block">{new Date(act.created_at).toLocaleString()}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
