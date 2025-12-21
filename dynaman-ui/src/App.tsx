import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from '@/components/Layout';
import Home from '@/pages/Home';
import DataExplorer from '@/pages/DataExplorer';
import SchemaEditor from '@/pages/SchemaEditor';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Home />} />
          <Route path="explorer/:entity" element={<DataExplorer />} />
          <Route path="schemas/new" element={<SchemaEditor />} />
          <Route path="schemas/:entity/edit" element={<SchemaEditor />} />
        </Route>
        <Route path="*" element={<div className="p-4">404 - Page Not Found</div>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;