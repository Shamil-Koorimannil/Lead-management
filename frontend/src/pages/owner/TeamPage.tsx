import React, { useEffect, useState } from 'react';
import { UserCircle, Plus, Shield, Check, X } from 'lucide-react';
import { usersService } from '../../services/users';
import { User, UserRole } from '../../types';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Dialog } from '../../components/ui/Dialog';
import { LoadingSpinner } from '../../components/ui/LoadingState';
import { Badge } from '../../components/ui/Badge';

export const TeamPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [newUser, setNewUser] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: 'Password123!',
    role: 'SALES_AGENT' as UserRole,
  });

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await usersService.getUsers();
      setUsers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await usersService.createUser(newUser);
      setIsModalOpen(false);
      loadUsers();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error creating user.');
    }
  };

  const handleToggleUserActive = async (user: User) => {
    try {
      await usersService.updateUser(user.id, { is_active: !user.is_active });
      loadUsers();
    } catch (err: any) {
      alert('Error updating user status.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Team Management & Access Control</h2>
          <p className="text-sm text-slate-500">Manage brand users, assign business roles, and manage system access permissions.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} icon={<Plus className="h-4 w-4" />}>
          Add Team Member
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <LoadingSpinner text="Loading Brand Users..." />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase">
                  <tr>
                    <th className="px-6 py-3">Member Name</th>
                    <th className="px-6 py-3">Email Address</th>
                    <th className="px-6 py-3">Business Role</th>
                    <th className="px-6 py-3">Account Status</th>
                    <th className="px-6 py-3">Joined Date</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/50">
                      <td className="px-6 py-4 font-semibold text-slate-900">{u.full_name}</td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-700">{u.email}</td>
                      <td className="px-6 py-4">
                        <Badge variant="info">{u.role.replace('_', ' ')}</Badge>
                      </td>
                      <td className="px-6 py-4">
                        {u.is_active ? (
                          <Badge variant="qualified">Active</Badge>
                        ) : (
                          <Badge variant="danger">Deactivated</Badge>
                        )}
                      </td>
                      <td className="px-6 py-4 text-xs text-slate-500">
                        {new Date(u.date_joined).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleToggleUserActive(u)}
                          className="px-3 py-1 text-xs font-semibold rounded-md border border-slate-200 hover:bg-slate-100 transition-colors"
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
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

      {/* Add User Modal */}
      <Dialog isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Team User">
        <form onSubmit={handleCreateUser} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">First Name</label>
              <input
                type="text"
                required
                value={newUser.first_name}
                onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Last Name</label>
              <input
                type="text"
                required
                value={newUser.last_name}
                onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg"
              />
            </div>
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Email Address</label>
            <input
              type="email"
              required
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            />
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Password</label>
            <input
              type="password"
              required
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            />
          </div>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Assign Role</label>
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value as UserRole })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg"
            >
              <option value="SALES_AGENT">Sales Agent</option>
              <option value="SALES_MANAGER">Sales Manager</option>
              <option value="BRAND_OWNER">Brand Owner</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>Cancel</Button>
            <Button type="submit">Create User</Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
