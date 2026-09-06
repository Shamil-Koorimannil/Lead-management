import { api } from './api';
import { QualificationRule } from '../types';

export const qualificationService = {
  getRules: async (): Promise<QualificationRule[]> => {
    const res = await api.get<{ results: QualificationRule[] }>('/qualification/rules/');
    return res.data.results || [];
  },

  createRule: async (data: Partial<QualificationRule>): Promise<QualificationRule> => {
    const res = await api.post<QualificationRule>('/qualification/rules/', data);
    return res.data;
  },

  updateRule: async (id: number, data: Partial<QualificationRule>): Promise<QualificationRule> => {
    const res = await api.patch<QualificationRule>(`/qualification/rules/${id}/`, data);
    return res.data;
  },

  deleteRule: async (id: number): Promise<void> => {
    await api.delete(`/qualification/rules/${id}/`);
  },
};
