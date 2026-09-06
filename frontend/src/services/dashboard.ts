import { api } from './api';
import { OwnerDashboardData, SalesDashboardData } from '../types';

export const dashboardService = {
  getOwnerDashboard: async (): Promise<OwnerDashboardData> => {
    const res = await api.get<OwnerDashboardData>('/dashboard/owner/');
    return res.data;
  },

  getSalesDashboard: async (): Promise<SalesDashboardData> => {
    const res = await api.get<SalesDashboardData>('/dashboard/sales/');
    return res.data;
  },
};
