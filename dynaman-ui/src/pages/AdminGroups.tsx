import { useState, useEffect } from 'react';
import { groupApi, type UserGroup } from '../lib/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { useLanguage } from '@/lib/i18n';
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
  const { t } = useLanguage();
  
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
      setError(t('userGroups.loadError'));
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
      alert(t('userGroups.createError'));
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('userGroups.confirmDelete'))) return;
    try {
      await groupApi.delete(id);
      fetchGroups();
    } catch (err) {
      alert(t('userGroups.deleteError'));
      console.error(err);
    }
  };

  if (loading) return <div>{t('common.loading')}</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('userGroups.title')}</h1>
        <Button onClick={() => setIsCreating(!isCreating)}>
          {isCreating ? t('userGroups.cancel') : t('userGroups.createGroup')}
        </Button>
      </div>

      {isCreating && (
        <div className="bg-gray-50 p-4 rounded-md border">
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <Label htmlFor="name">{t('userGroups.name')}</Label>
              <Input 
                id="name" 
                value={newName} 
                onChange={(e) => setNewName(e.target.value)} 
                required 
              />
            </div>
            <div>
              <Label htmlFor="desc">{t('userGroups.description')}</Label>
              <Input 
                id="desc" 
                value={newDesc} 
                onChange={(e) => setNewDesc(e.target.value)} 
              />
            </div>
            <Button type="submit">{t('common.save')}</Button>
          </form>
        </div>
      )}

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>{t('userGroups.table.name')}</TableHead>
            <TableHead>{t('userGroups.table.description')}</TableHead>
            <TableHead>{t('userGroups.table.actions')}</TableHead>
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
                    {t('common.delete')}
                  </Button>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} className="text-center h-24">
                {t('userGroups.noGroups')}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}