import React, { useEffect, useState } from 'react';
import api from '@/lib/api';
import { useAuth, type User } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Trash2, UserPlus } from 'lucide-react';

export const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const { user: currentUser } = useAuth();
  
  // Form State
  const [isCreating, setIsCreating] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserRole, setNewUserRole] = useState('user');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/auth/users');
      setUsers(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (userId: string) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;
    try {
      await api.delete(`/auth/users/${userId}`);
      setUsers(users.filter(u => u._id !== userId));
    } catch (err) {
      console.error(err);
      alert("Failed to delete user");
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      const payload = {
          email: newUserEmail,
          password: newUserPassword,
          role: newUserRole
      };
      const response = await api.post('/auth/users', payload);
      setUsers([...users, response.data]);
      setIsCreating(false);
      setSuccess(`User ${newUserEmail} created successfully.`);
      setNewUserEmail('');
      setNewUserPassword('');
      setNewUserRole('user');
    } catch (err: any) {
        if (err.response?.data?.detail) {
            setError(err.response.data.detail);
        } else {
            setError("Failed to create user");
        }
    }
  };

  if (loading) return <div>Loading users...</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">User Management</h1>
        <Button onClick={() => setIsCreating(!isCreating)}>
            <UserPlus className="mr-2 h-4 w-4" />
            {isCreating ? 'Cancel' : 'Add User'}
        </Button>
      </div>

      {isCreating && (
          <div className="bg-muted/30 p-4 rounded-lg border space-y-4 max-w-lg">
              <h3 className="font-semibold">Create New User</h3>
              {error && <div className="text-red-500 text-sm">{error}</div>}
              <form onSubmit={handleCreateUser} className="space-y-3">
                  <div>
                      <Label>Email</Label>
                      <Input value={newUserEmail} onChange={e => setNewUserEmail(e.target.value)} required type="email" />
                  </div>
                  <div>
                      <Label>Password</Label>
                      <Input value={newUserPassword} onChange={e => setNewUserPassword(e.target.value)} required type="password" />
                  </div>
                  <div>
                      <Label>Role</Label>
                      <select 
                        className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                        value={newUserRole} 
                        onChange={e => setNewUserRole(e.target.value)}
                      >
                          <option value="user">User</option>
                          <option value="user_admin">User Admin</option>
                          <option value="system_admin">System Admin</option>
                      </select>
                  </div>
                  <Button type="submit">Create User</Button>
              </form>
          </div>
      )}

      {success && <div className="text-green-600 bg-green-50 p-3 rounded">{success}</div>}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {users.map((user) => (
              <TableRow key={user._id}>
                <TableCell className="font-medium">{user.email}</TableCell>
                <TableCell>{user.role}</TableCell>
                <TableCell>{user.is_active ? 'Active' : 'Inactive'}</TableCell>
                <TableCell className="text-right">
                  {user.email !== currentUser?.email && (
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(user._id)} className="text-red-500 hover:text-red-700">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
