import { useState, useEffect } from 'react';
import { groupApi, type UserGroup } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';

export default function AdminGroups() {
  const [groups, setGroups] = useState<UserGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Form State
  const [isCreating, setIsCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [newDesc, setNewDesc] = useState('');

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const data = await groupApi.list();
      setGroups(data);
    } catch (err) {
      setError('Failed to load groups');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await groupApi.create({ name: newName, description: newDesc });
      setNewName('');
      setNewDesc('');
      setIsCreating(false);
      fetchGroups();
    } catch (err) {
      alert('Failed to create group');
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this group?')) return;
    try {
      await groupApi.delete(id);
      fetchGroups();
    } catch (err) {
      alert('Failed to delete group');
      console.error(err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">User Groups</h1>
        <Button onClick={() => setIsCreating(!isCreating)}>
          {isCreating ? 'Cancel' : 'Create Group'}
        </Button>
      </div>

      {isCreating && (
        <div className="bg-gray-50 p-4 rounded-md border">
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <Label htmlFor="name">Group Name</Label>
              <Input 
                id="name" 
                value={newName} 
                onChange={(e) => setNewName(e.target.value)} 
                required 
              />
            </div>
            <div>
              <Label htmlFor="desc">Description</Label>
              <Input 
                id="desc" 
                value={newDesc} 
                onChange={(e) => setNewDesc(e.target.value)} 
              />
            </div>
            <Button type="submit">Save</Button>
          </form>
        </div>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {Array.isArray(groups) && groups.length > 0 ? (
            groups.map((group) => (
              <TableRow key={group._id}>
                <TableCell className="font-medium">{group.name}</TableCell>
                <TableCell>{group.description}</TableCell>
                <TableCell>
                  <Button 
                    variant="destructive" 
                    size="sm"
                    onClick={() => handleDelete(group._id)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} className="text-center h-24">
                No groups found.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
