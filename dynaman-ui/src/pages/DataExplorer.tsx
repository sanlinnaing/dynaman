import { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
  getSortedRowModel,
} from '@tanstack/react-table';
import type { SortingState } from '@tanstack/react-table';
import { Search, ChevronLeft, ChevronRight, Loader2, PlusCircle, Trash2, Edit } from 'lucide-react';
import api from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import DataInputForm from '@/components/DataInputForm';
import { useLanguage } from '@/lib/i18n';

interface SchemaField {
  name: string;
  field_type: string;
  label: string;
  is_required: boolean;
  reference_target?: string;
}

interface Schema {
  entity_name: string;
  fields: SchemaField[];
}

export default function DataExplorer() {
  const { entity } = useParams<{ entity: string }>();
  const [schema, setSchema] = useState<Schema | null>(null);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showDataInputForm, setShowDataInputForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);
  const { t } = useLanguage();
  
  // Pagination
  const [page, setPage] = useState(0);
  const [pageSize] = useState(10);
  
  // Search
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Sorting
  const [sorting, setSorting] = useState<SortingState>([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(0); // Reset to first page on search
    }, 500);
    return () => clearTimeout(timer);
  }, [search]);

  // Fetch Schema
  useEffect(() => {
    if (!entity) return;
    const fetchSchema = async () => {
      try {
        setLoading(true);
        const res = await api.get(`/schemas/${entity}`);
        setSchema(res.data);
      } catch (err) {
        console.error('Error fetching schema:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSchema();
    setPage(0);
    setSearch('');
  }, [entity]);

  const fetchData = async () => {
      if (!entity) return;
      try {
        setLoading(true);
        const skip = page * pageSize;
        const limit = pageSize;
        
        let url = `/data/${entity}`;
        const params: any = { skip, limit };

        if (debouncedSearch) {
          url = `/data/${entity}/search`;
          params.q = debouncedSearch;
        }

        const res = await api.get(url, { params });
        setData(res.data);
      } catch (err) {
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

  // Fetch Data
  useEffect(() => {
    fetchData();
  }, [entity, page, pageSize, debouncedSearch, refreshTrigger]);

  const handleDelete = async (id: string) => {
    if (!confirm(t('explorer.confirmDelete'))) return;
    try {
      await api.delete(`/data/${entity}/${id}`);
      setRefreshTrigger(prev => prev + 1);
    } catch (err) {
      console.error('Failed to delete record:', err);
      alert(t('explorer.deleteError'));
    }
  };


  // Columns
  const columns = useMemo(() => {
    if (!schema) return [];
    const helper = createColumnHelper<any>();
    
    const dynamicCols = schema.fields.map((field) => 
      helper.accessor((row) => row.content?.[field.name], {
        id: field.name,
        header: field.label || field.name,
        cell: (info) => {
            const val = info.getValue();
            if (typeof val === 'object') return JSON.stringify(val);
            return val;
        }
      })
    );

    return [
      helper.accessor('id', { header: 'ID', size: 60 }),
      ...dynamicCols,
      helper.accessor((row) => row._metadata?.created_at, { header: 'Created', id: 'created_at' }),
      helper.display({
        id: 'actions',
        header: t('explorer.actions'),
        cell: (info) => (
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" onClick={() => {
                setSelectedRecord(info.row.original);
                setShowDataInputForm(true);
            }}>
                <Edit className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => handleDelete(info.row.original.id)}>
                <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        )
      })
    ];
  }, [schema, t]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    state: {
      sorting,
    },
    manualPagination: true, // We handle pagination server-side
  });

  if (!entity) return <div>Select an entity</div>;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">
          {t('explorer.title', { entity: schema?.entity_name || entity })}
        </h1>
        <div className="flex items-center gap-2">
           <div className="relative">
             <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
             <Input
               type="search"
               placeholder={t('common.search')}
               className="pl-8 w-[200px] lg:w-[300px]"
               value={search}
               onChange={(e) => setSearch(e.target.value)}
             />
           </div>
           <Button variant="outline" onClick={() => setRefreshTrigger((prev) => prev + 1)}>{t('common.refresh')}</Button>
           <Button onClick={() => setShowDataInputForm(true)} disabled={!schema}>
              <PlusCircle className="mr-2 h-4 w-4" /> {t('explorer.addData')}
           </Button>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {loading ? (
               <TableRow>
                 <TableCell colSpan={columns.length} className="h-24 text-center">
                    <div className="flex justify-center items-center gap-2">
                       <Loader2 className="h-4 w-4 animate-spin" />
                       {t('common.loading')}
                    </div>
                 </TableCell>
               </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  {t('explorer.noData')}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0 || loading}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          {t('common.previous')}
        </Button>
        <div className="text-sm font-medium">{t('common.page', { page: String(page + 1) })}</div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage((p) => p + 1)}
          disabled={data.length < pageSize || loading}
        >
          {t('common.next')}
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>

      {showDataInputForm && schema && (
        <DataInputForm
          schema={schema}
          isOpen={showDataInputForm}
          onClose={() => {
            setShowDataInputForm(false);
            setSelectedRecord(null);
          }}
          onSave={() => {
            setRefreshTrigger(prev => prev + 1); // Refresh data after saving
            setShowDataInputForm(false);
            setSelectedRecord(null);
          }}
          recordId={selectedRecord?.id}
          initialData={selectedRecord?.content}
        />
      )}
    </div>
  );
}


