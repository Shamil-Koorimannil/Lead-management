import { api } from './api';
import { User } from '../types';

export const usersService = {
  getUsers: async (): Promise<User[]> => {
    const res = await api.get<{ results: User[] }>('/users/');
    return res.data.results || [];
  },

  createUser: async (data: Partial<User> & { password?: string }): Promise<User> => {
    const res = await api.post<User>('/users/', data);
    return res.data;
  },

  updateUser: async (id: number, data: Partial<User>): Promise<User> => {
    const res = await api.patch<User>(`/users/${id}/`, data);
    return res.data;
  },
};
