import { api } from './api';
import { User } from '../types';

export interface LoginResponse {
  user: User;
  access: string;
  refresh: string;
}

export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const res = await api.post<LoginResponse>('/auth/login/', { email, password });
    return res.data;
  },

  logout: async (refreshToken?: string): Promise<void> => {
    try {
      await api.post('/auth/logout/', { refresh: refreshToken });
    } catch {
      // Ignore network errors during logout
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me/');
    return res.data;
  },
};
