import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import {
  ArrowLeft, Phone, Mail, MapPin, ShieldCheck, MessageSquare,
  StickyNote, Clock, Send, Plus
} from 'lucide-react';
import { leadsService } from '../../services/leads';
import { conversationsService } from '../../services/conversations';
import { Lead, Conversation, LeadNote, SalesStatus } from '../../types';
import { QualificationBadge, SalesStatusBadge } from '../../components/ui/Badge';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Dialog } from '../../components/ui/Dialog';
import { LoadingSpinner } from '../../components/ui/LoadingState';

export const SalesLeadDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [lead, setLead] = useState<Lead | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [notes, setNotes] = useState<LeadNote[]>([]);
  const [loading, setLoading] = useState(true);

  // Message & Note Form state
  const [newMessage, setNewMessage] = useState('');
  const [newNote, setNewNote] = useState('');
  const [isFollowUpModalOpen, setIsFollowUpModalOpen] = useState(false);

  const [followUpData, setFollowUpData] = useState({
    next_follow_up_at: new Date(Date.now() + 86400000).toISOString().slice(0, 16),
    follow_up_type: 'CALL',
    follow_up_note: '',
  });

  const loadLead = async () => {
    if (!id) return;
    try {
      const l = await leadsService.getLeadById(Number(id));
      setLead(l);
      const convs = await conversationsService.getConversations(Number(id));
      setConversations(convs);
      const n = await conversationsService.getLeadNotes(Number(id));
      setNotes(n);
    } catch {
      navigate('/sales/leads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLead();
  }, [id]);

  const handleStatusChange = async (status: SalesStatus) => {
    if (!lead) return;
    try {
      const updated = await leadsService.updateLead(lead.id, { sales_status: status });
      setLead(updated);
    } catch {
      alert('Error updating status.');
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!conversations.length || !newMessage.trim()) return;
    try {
      await conversationsService.addMessage(conversations[0].id, {
        message: newMessage,
        direction: 'OUTBOUND',
        message_type: 'TEXT',
      });
      setNewMessage('');
      loadLead();
    } catch {
      alert('Error sending message.');
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lead || !newNote.trim()) return;
    try {
      await conversationsService.createNote(lead.id, newNote);
      setNewNote('');
      loadLead();
    } catch {
      alert('Error adding note.');
    }
  };

  const handleScheduleFollowUp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!lead) return;
    try {
      await leadsService.scheduleFollowUp(lead.id, {
        next_follow_up_at: new Date(followUpData.next_follow_up_at).toISOString(),
        follow_up_type: followUpData.follow_up_type,
        follow_up_note: followUpData.follow_up_note,
      });
      setIsFollowUpModalOpen(false);
      loadLead();
    } catch {
      alert('Error scheduling follow-up.');
    }
  };

  const handleCompleteFollowUp = async () => {
    if (!lead) return;
    try {
      await leadsService.completeFollowUp(lead.id);
      loadLead();
    } catch {
      alert('Error completing follow-up.');
    }
  };

  if (loading || !lead) return <LoadingSpinner text="Loading Lead Actions..." />;

  return (
    <div className="space-y-6">
      {/* Top Header Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/sales/leads')}
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" /> Back to My Leads
        </button>

        <div className="flex items-center gap-3">
          <QualificationBadge status={lead.qualification_status} score={lead.qualification_score} />
          <SalesStatusBadge status={lead.sales_status} />
        </div>
      </div>

      {/* Primary Action Bar */}
      <Card className="bg-slate-900 text-white border-none shadow-lg">
        <CardContent className="p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
              {lead.lead_number}
            </span>
            <h1 className="text-xl font-bold mt-1.5">{lead.name}</h1>
            <p className="text-xs text-slate-400 flex items-center gap-3 mt-1">
              <span>Phone: {lead.phone}</span>
              <span>•</span>
              <span>City: {lead.city}</span>
              <span>•</span>
              <span>Budget: ₹{Number(lead.investment_capacity || 0).toLocaleString()}</span>
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <select
              value={lead.sales_status}
              onChange={(e) => handleStatusChange(e.target.value as SalesStatus)}
              className="px-3 py-2 bg-slate-800 border border-slate-700 text-white rounded-lg text-xs font-semibold focus:ring-2 focus:ring-emerald-500"
            >
              <option value="NEW">Status: NEW</option>
              <option value="CONTACTED">Status: CONTACTED</option>
              <option value="FOLLOW_UP">Status: FOLLOW UP</option>
              <option value="MEETING">Status: MEETING</option>
              <option value="NEGOTIATION">Status: NEGOTIATION</option>
              <option value="CONVERTED">Status: CONVERTED</option>
              <option value="LOST">Status: LOST</option>
            </select>

            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsFollowUpModalOpen(true)}
              icon={<Clock className="h-4 w-4" />}
            >
              Schedule Follow-up
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main 2-Column Operational Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Conversation & Internal Notes */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prominent Conversation Interface */}
          <Card className="flex flex-col h-112">
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-sky-600" /> Customer Conversation Channel
                </span>
                <span className="text-xs text-slate-400 font-normal">
                  {conversations.length ? `Channel: ${conversations[0].channel}` : 'No conversation active'}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col justify-between p-4 overflow-hidden">
              {/* Message Feed */}
              <div className="flex-1 overflow-y-auto space-y-3 pr-2 mb-4">
                {conversations.length === 0 || !conversations[0].messages.length ? (
                  <p className="text-xs text-slate-400 italic text-center py-12">No messages exchanged yet.</p>
                ) : (
                  conversations[0].messages.map((m) => (
                    <div
                      key={m.id}
                      className={`p-3 rounded-xl text-xs max-w-sm ${
                        m.direction === 'OUTBOUND'
                          ? 'ml-auto bg-sky-600 text-white rounded-br-none'
                          : 'mr-auto bg-slate-100 text-slate-800 rounded-bl-none'
                      }`}
                    >
                      <p>{m.message}</p>
                      <span className={`text-[10px] block mt-1 ${m.direction === 'OUTBOUND' ? 'text-sky-200' : 'text-slate-400'}`}>
                        {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  ))
                )}
              </div>

              {/* Message Send Form */}
              <form onSubmit={handleSendMessage} className="flex gap-2 border-t border-slate-100 pt-3">
                <input
                  type="text"
                  placeholder="Type an outbound message to customer..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
                <Button type="submit" size="sm" icon={<Send className="h-3.5 w-3.5" />}>
                  Send
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Internal Notes Feed */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <StickyNote className="h-5 w-5 text-amber-600" /> Internal Staff Notes
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <form onSubmit={handleAddNote} className="space-y-2">
                <textarea
                  required
                  rows={2}
                  placeholder="Add private note for yourself or team..."
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  className="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:ring-2 focus:ring-sky-500 focus:outline-none"
                />
                <div className="flex justify-end">
                  <Button type="submit" size="sm">Save Internal Note</Button>
                </div>
              </form>

              <div className="space-y-2 pt-2">
                {notes.map((n) => (
                  <div key={n.id} className="p-3 bg-amber-50/60 border border-amber-200/80 rounded-lg text-xs">
                    <div className="flex justify-between font-semibold text-slate-800 mb-1">
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

        {/* Right Sidebar: Qualification & Follow-up Details */}
        <div className="space-y-6">
          {/* Qualification Card */}
          <Card className="border-l-4 border-l-emerald-600">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <ShieldCheck className="h-5 w-5 text-emerald-600" /> Lead Qualification Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div>
                  <span className="font-semibold text-slate-600 block">Score</span>
                  <span className="text-2xl font-extrabold text-slate-900">{lead.qualification_score}/100</span>
                </div>
                <QualificationBadge status={lead.qualification_status} />
              </div>
              <p className="text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200/60 leading-relaxed font-mono">
                {lead.qualification_reason}
              </p>
            </CardContent>
          </Card>

          {/* Scheduled Follow-up Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between text-sm">
                <span className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-purple-600" /> Active Follow-Up
                </span>
                {lead.follow_up_required && (
                  <Button size="sm" variant="outline" onClick={handleCompleteFollowUp}>
                    Mark Complete
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs">
              {lead.follow_up_required ? (
                <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg space-y-1">
                  <span className="font-bold text-purple-900 block">{lead.follow_up_type}</span>
                  <span className="text-purple-700 font-mono block">
                    {lead.next_follow_up_at ? new Date(lead.next_follow_up_at).toLocaleString() : ''}
                  </span>
                  {lead.follow_up_note && <p className="text-slate-600 pt-1">{lead.follow_up_note}</p>}
                </div>
              ) : (
                <p className="text-slate-500 italic">No active follow-up scheduled.</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Schedule Follow-up Dialog */}
      <Dialog isOpen={isFollowUpModalOpen} onClose={() => setIsFollowUpModalOpen(false)} title="Schedule Next Follow-Up">
        <form onSubmit={handleScheduleFollowUp} className="space-y-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Follow-Up Date & Time</label>
            <input
              type="datetime-local"
              required
              value={followUpData.next_follow_up_at}
              onChange={(e) => setFollowUpData({ ...followUpData, next_follow_up_at: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            />
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Follow-Up Channel/Type</label>
            <select
              value={followUpData.follow_up_type}
              onChange={(e) => setFollowUpData({ ...followUpData, follow_up_type: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            >
              <option value="CALL">Phone Call</option>
              <option value="WHATSAPP">WhatsApp</option>
              <option value="MEETING">Meeting</option>
              <option value="EMAIL">Email</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Note / Objective</label>
            <textarea
              rows={2}
              placeholder="e.g. Call to discuss site location parameters..."
              value={followUpData.follow_up_note}
              onChange={(e) => setFollowUpData({ ...followUpData, follow_up_note: e.target.value })}
              className="w-full p-3 border border-slate-200 rounded-lg"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsFollowUpModalOpen(false)}>Cancel</Button>
            <Button type="submit">Confirm & Schedule</Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
