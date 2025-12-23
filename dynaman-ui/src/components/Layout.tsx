import { useEffect, useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { Table as TableIcon, LayoutDashboard, Menu, PlusCircle, Globe } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useLanguage } from '@/lib/i18n';

export default function DashboardLayout() {
  const [schemas, setSchemas] = useState<string[]>([]);
  const location = useLocation();
  const { t, language, setLanguage } = useLanguage();

  useEffect(() => {
    fetchSchemas();
  }, []);

  const fetchSchemas = async () => {
    try {
      const response = await api.get('/schemas/');
      setSchemas(response.data);
    } catch (error) {
      console.error('Failed to fetch schemas', error);
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-muted/40 hidden md:block flex flex-col">
        <div className="p-4 border-b flex items-center gap-2">
           <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center">
             <span className="text-primary-foreground font-bold">D</span>
           </div>
           <span className="font-bold text-lg">{t('app.title')}</span>
        </div>
        <nav className="p-4 space-y-2 flex-1">
          <div className="mb-4">
             <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.platform')}</h2>
             <Link to="/">
                <Button variant={location.pathname === '/' ? 'secondary' : 'ghost'} className="w-full justify-start">
                   <LayoutDashboard className="mr-2 h-4 w-4" />
                   {t('nav.dashboard')}
                </Button>
             </Link>
          </div>

          <div className="mb-4">
             <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.schemaManagement')}</h2>
             <Link to="/schemas/new">
                <Button variant={location.pathname === '/schemas/new' ? 'secondary' : 'ghost'} className="w-full justify-start">
                   <PlusCircle className="mr-2 h-4 w-4" />
                   {t('nav.createNew')}
                </Button>
             </Link>
             <div className="space-y-1 mt-2">
               {schemas.map((schema) => (
                 <Link key={`edit-${schema}`} to={`/schemas/${schema}/edit`}>
                    <Button variant={location.pathname === `/schemas/${schema}/edit` ? 'secondary' : 'ghost'} className="w-full justify-start pl-8 text-sm">
                       <TableIcon className="mr-2 h-4 w-4" />
                       {schema}
                    </Button>
                 </Link>
               ))}
             </div>
          </div>

          <div>
             <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.dataExplorer')}</h2>
             <div className="space-y-1">
               {schemas.map((schema) => (
                 <Link key={schema} to={`/explorer/${schema}`}>
                    <Button variant={location.pathname === `/explorer/${schema}` ? 'secondary' : 'ghost'} className="w-full justify-start pl-8 text-sm">
                       <TableIcon className="mr-2 h-4 w-4" />
                       {schema}
                    </Button>
                 </Link>
               ))}
               {schemas.length === 0 && (
                 <p className="text-sm text-muted-foreground pl-4">{t('nav.noSchemas')}</p>
               )}
             </div>
          </div>
        </nav>
        
        {/* Language Switcher */}
        <div className="p-4 border-t">
            <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-muted-foreground" />
                <select 
                    value={language} 
                    onChange={(e) => setLanguage(e.target.value as 'en' | 'ja')}
                    className="bg-transparent text-sm border-none focus:ring-0 cursor-pointer"
                >
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                </select>
            </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 border-b flex items-center px-4 md:hidden">
            <Menu className="h-5 w-5" />
            <span className="ml-2 font-bold">{t('app.title')}</span>
        </header>
        <div className="flex-1 overflow-auto p-6">
          <Outlet context={{ refreshSchemas: fetchSchemas }} />
        </div>
      </main>
    </div>
  );
}
