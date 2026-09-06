import { api } from './api';
import { Lead } from '../types';

export interface LeadFilterParams {
  search?: string;
  qualification_status?: string;
  sales_status?: string;
  lead_source?: string;
  assigned_to?: number | string;
  city?: string;
  follow_up_required?: boolean;
  ordering?: string;
  page?: number;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const leadsService = {
  getLeads: async (params?: LeadFilterParams): Promise<PaginatedResponse<Lead>> => {
    const res = await api.get<PaginatedResponse<Lead>>('/leads/', { params });
    return res.data;
  },

  getLeadById: async (id: number): Promise<Lead> => {
    const res = await api.get<Lead>(`/leads/${id}/`);
    return res.data;
  },

  createLead: async (data: Partial<Lead>): Promise<Lead> => {
    const res = await api.post<Lead>('/leads/', data);
    return res.data;
  },

  updateLead: async (id: number, data: Partial<Lead>): Promise<Lead> => {
    const res = await api.patch<Lead>(`/leads/${id}/`, data);
    return res.data;
  },

  deleteLead: async (id: number): Promise<void> => {
    await api.delete(`/leads/${id}/`);
  },

  scheduleFollowUp: async (
    id: number,
    data: { next_follow_up_at: string; follow_up_type: string; follow_up_note?: string }
  ): Promise<Lead> => {
    const res = await api.post<Lead>(`/leads/${id}/schedule-follow-up/`, data);
    return res.data;
  },

  completeFollowUp: async (id: number): Promise<Lead> => {
    const res = await api.post<Lead>(`/leads/${id}/complete-follow-up/`);
    return res.data;
  },

  assignLead: async (id: number, assigned_to_id: number): Promise<Lead> => {
    const res = await api.post<Lead>(`/leads/${id}/assign/`, { assigned_to_id });
    return res.data;
  },
};
