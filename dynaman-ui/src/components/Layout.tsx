import { useEffect, useState } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Table as TableIcon, LayoutDashboard, Menu, Globe, LogOut, Users, History, Database } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useLanguage } from '@/lib/i18n';
import { useAuth } from '@/context/AuthContext';

export default function DashboardLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { t, language, setLanguage } = useLanguage();
  const { logout, user } = useAuth();

  const [recentExplore, setRecentExplore] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('recentExplore');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [recentEdit, setRecentEdit] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('recentEdit');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    const path = location.pathname;
    if (path.startsWith('/explorer/')) {
        const parts = path.split('/');
        const schema = parts[2]; // /explorer/schema_name
        if (schema) addToRecent(schema, 'explore');
    } else if (path.startsWith('/schemas/')) {
        const parts = path.split('/');
        const schema = parts[2]; // /schemas/schema_name/edit
        // specific check to avoid adding 'new' or if it's just /schemas (list)
        if (schema && schema !== 'new' && parts.length > 2) { 
           addToRecent(schema, 'edit');
        }
    }
  }, [location]);

  const addToRecent = (schema: string, type: 'explore' | 'edit') => {
      const setFunc = type === 'explore' ? setRecentExplore : setRecentEdit;
      const storageKey = type === 'explore' ? 'recentExplore' : 'recentEdit';
      
      setFunc(prev => {
          // Remove if exists, add to front, take top 3
          const newRecent = [schema, ...prev.filter(s => s !== schema)].slice(0, 3);
          localStorage.setItem(storageKey, JSON.stringify(newRecent));
          return newRecent;
      });
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Dummy refresh function to satisfy potential outlet context consumers
  const refreshSchemas = async () => {
    // No longer needed for sidebar, but kept for interface compatibility
  };

  const isAdmin = user?.role === 'system_admin' || user?.role === 'user_admin';
  const isSystemAdmin = user?.role === 'system_admin';

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
        <nav className="p-4 space-y-2 flex-1 overflow-y-auto">
          <div className="mb-4">
             <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.platform')}</h2>
             <Link to="/">
                <Button variant={location.pathname === '/' ? 'secondary' : 'ghost'} className="w-full justify-start">
                   <LayoutDashboard className="mr-2 h-4 w-4" />
                   {t('nav.dashboard')}
                </Button>
             </Link>
             {isAdmin && (
                 <Link to="/admin/users">
                    <Button variant={location.pathname === '/admin/users' ? 'secondary' : 'ghost'} className="w-full justify-start mt-1">
                       <Users className="mr-2 h-4 w-4" />
                       {t('nav.userManagement')}
                    </Button>
                 </Link>
             )}
             {isSystemAdmin && (
                 <Link to="/admin/groups">
                    <Button variant={location.pathname === '/admin/groups' ? 'secondary' : 'ghost'} className="w-full justify-start mt-1">
                       <Users className="mr-2 h-4 w-4" />
                       {t('nav.userGroups')}
                    </Button>
                 </Link>
             )}
          </div>

          {isSystemAdmin && (
              <div className="mb-4">
                 <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.schemaManagement')}</h2>
                 <Link to="/schemas">
                    <Button variant={location.pathname === '/schemas' ? 'secondary' : 'ghost'} className="w-full justify-start">
                       <Database className="mr-2 h-4 w-4" />
                       {t('nav.schemaManagement')}
                    </Button>
                 </Link>
                 
                 {/* Recent Edit List */}
                 {recentEdit.length > 0 && (
                   <div className="mt-2 space-y-1 ml-2 pl-2 border-l">
                     <p className="text-[10px] text-muted-foreground font-medium uppercase mb-1 pl-2">{t('nav.recent')}</p>
                     {recentEdit.map((schema) => (
                       <Link key={`recent-edit-${schema}`} to={`/schemas/${schema}/edit`}>
                          <Button variant="ghost" size="sm" className="w-full justify-start h-8 text-xs font-normal text-muted-foreground hover:text-foreground">
                             <History className="mr-2 h-3 w-3" />
                             {schema}
                          </Button>
                       </Link>
                     ))}
                   </div>
                 )}
              </div>
          )}

          <div>
             <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{t('nav.dataExplorer')}</h2>
             <Link to="/explorer">
                <Button variant={location.pathname === '/explorer' ? 'secondary' : 'ghost'} className="w-full justify-start">
                   <TableIcon className="mr-2 h-4 w-4" />
                   {t('nav.dataExplorer')}
                </Button>
             </Link>

             {/* Recent Explore List */}
             {recentExplore.length > 0 && (
               <div className="mt-2 space-y-1 ml-2 pl-2 border-l">
                 <p className="text-[10px] text-muted-foreground font-medium uppercase mb-1 pl-2">{t('nav.recent')}</p>
                 {recentExplore.map((schema) => (
                   <Link key={`recent-explore-${schema}`} to={`/explorer/${schema}`}>
                      <Button variant="ghost" size="sm" className="w-full justify-start h-8 text-xs font-normal text-muted-foreground hover:text-foreground">
                         <History className="mr-2 h-3 w-3" />
                         {schema}
                      </Button>
                   </Link>
                 ))}
               </div>
             )}
          </div>
        </nav>
        
        {/* User Profile, Language Switcher and Logout */}
        <div className="p-4 border-t space-y-2">
            {user && (
              <div className="flex items-center gap-3 px-2 py-2 mb-2 rounded-md bg-muted/50">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold shrink-0">
                      {user.email.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate" title={user.email}>
                          {user.email}
                      </p>
                      <p className="text-xs text-muted-foreground capitalize truncate">
                          {user.role.replace('_', ' ')}
                      </p>
                  </div>
              </div>
            )}
            <div className="flex items-center justify-between">
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
                <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-600 hover:bg-red-50" onClick={handleLogout} title={t('nav.logout')}>
                    <LogOut className="h-4 w-4" />
                </Button>
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
          <Outlet context={{ refreshSchemas }} />
        </div>
      </main>
    </div>
  );
}
