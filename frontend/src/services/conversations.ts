import { api } from './api';
import { Conversation, Message, LeadNote } from '../types';

export const conversationsService = {
  getConversations: async (leadId?: number): Promise<Conversation[]> => {
    const res = await api.get<{ results: Conversation[] }>('/conversations/', {
      params: leadId ? { lead: leadId } : undefined,
    });
    return res.data.results || [];
  },

  addMessage: async (
    conversationId: number,
    data: { message: string; direction?: 'INBOUND' | 'OUTBOUND'; message_type?: string }
  ): Promise<Message> => {
    const res = await api.post<Message>(`/conversations/${conversationId}/messages/`, data);
    return res.data;
  },

  getLeadNotes: async (leadId: number): Promise<LeadNote[]> => {
    const res = await api.get<{ results: LeadNote[] }>('/conversations/notes/', {
      params: { lead: leadId },
    });
    return res.data.results || [];
  },

  createNote: async (leadId: number, content: string): Promise<LeadNote> => {
    const res = await api.post<LeadNote>('/conversations/notes/', { lead: leadId, content });
    return res.data;
  },
};
