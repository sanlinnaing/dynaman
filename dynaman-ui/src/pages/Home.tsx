import { useLanguage } from '@/lib/i18n';

export default function Home() {
  const { t } = useLanguage();

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">{t('home.welcome')}</h1>
      <p className="text-muted-foreground mb-8">
        {t('home.description')}
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">{t('home.schemas.title')}</h3>
          <p className="text-sm text-muted-foreground">{t('home.schemas.description')}</p>
        </div>
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">{t('home.explorer.title')}</h3>
          <p className="text-sm text-muted-foreground">{t('home.explorer.description')}</p>
        </div>
        <div className="p-6 rounded-lg border bg-card text-card-foreground shadow-sm">
          <h3 className="font-semibold text-lg mb-2">{t('home.api.title')}</h3>
          <p className="text-sm text-muted-foreground">{t('home.api.description')}</p>
        </div>
      </div>
    </div>
  );
}
