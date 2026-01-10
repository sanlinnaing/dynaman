import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table as TableIcon, Database, ArrowRight, PlusCircle } from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useLanguage } from '@/lib/i18n';

interface SchemaListPageProps {
  mode: 'edit' | 'explore';
}

export default function SchemaListPage({ mode }: SchemaListPageProps) {
  const [schemas, setSchemas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const { t } = useLanguage();

  useEffect(() => {
    fetchSchemas();
  }, []);

  const fetchSchemas = async () => {
    try {
      const response = await api.get('/api/v1/schemas/');
      setSchemas(response.data);
    } catch (error) {
      console.error('Failed to fetch schemas', error);
    } finally {
      setLoading(false);
    }
  };

  const getTargetLink = (schema: string) => {
    return mode === 'edit' ? `/schemas/${schema}/edit` : `/explorer/${schema}`;
  };

  const title = mode === 'edit' ? t('nav.schemaManagement') : t('nav.dataExplorer');
  const description = mode === 'edit' 
    ? t('schema.list.manageDescription')
    : t('schema.list.exploreDescription');

  return (
    <div className="container mx-auto max-w-5xl py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        {mode === 'edit' && (
          <Link to="/schemas/new">
            <Button>
              <PlusCircle className="mr-2 h-4 w-4" />
              {t('nav.createNew')}
            </Button>
          </Link>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 rounded-lg bg-muted/50 animate-pulse" />
          ))}
        </div>
      ) : schemas.length === 0 ? (
        <div className="text-center py-12 bg-muted/30 rounded-lg border border-dashed">
          <Database className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">{t('nav.noSchemas')}</h3>
          <p className="text-muted-foreground mb-4">
            {mode === 'edit' 
              ? t('schema.list.getStarted') 
              : t('schema.list.startExploring')}
          </p>
          {mode === 'edit' && (
            <Link to="/schemas/new">
              <Button variant="outline">{t('schema.list.createSchema')}</Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {schemas.map((schema) => (
            <Link key={schema} to={getTargetLink(schema)}>
              <div className="group relative p-6 bg-card hover:bg-accent/50 border rounded-xl transition-all hover:shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                    <TableIcon className="h-5 w-5" />
                  </div>
                  <ArrowRight className="h-5 w-5 text-muted-foreground opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{schema}</h3>
                <p className="text-sm text-muted-foreground">
                  {mode === 'edit' ? t('schema.list.editDefinition') : t('schema.list.viewData')}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}