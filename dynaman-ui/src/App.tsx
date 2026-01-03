import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from '@/components/Layout';
import Home from '@/pages/Home';
import DataExplorer from '@/pages/DataExplorer';
import SchemaEditor from '@/pages/SchemaEditor';
import { Login } from '@/pages/Login';
import { AuthProvider } from '@/context/AuthContext';
import { RequireAuth } from '@/components/RequireAuth';
import { RequireSystemAdmin } from '@/components/RequireSystemAdmin';
import { AdminUsers } from '@/pages/AdminUsers';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route path="/" element={
            <RequireAuth>
              <DashboardLayout />
            </RequireAuth>
          }>
            <Route index element={<Home />} />
            <Route path="explorer/:entity" element={<DataExplorer />} />
            
            <Route path="schemas/new" element={
                <RequireSystemAdmin>
                    <SchemaEditor />
                </RequireSystemAdmin>
            } />
            <Route path="schemas/:entity/edit" element={
                <RequireSystemAdmin>
                    <SchemaEditor />
                </RequireSystemAdmin>
            } />
            
            <Route path="admin/users" element={<AdminUsers />} />
          </Route>
          
          <Route path="*" element={<div className="p-4">404 - Page Not Found</div>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;