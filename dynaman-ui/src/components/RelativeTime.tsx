import { useMemo } from 'react';
import { useLanguage } from '@/lib/i18n';

interface RelativeTimeProps {
  date: string | Date | undefined | null;
}

export function RelativeTime({ date }: RelativeTimeProps) {
  const { language } = useLanguage();

  const { relative, absolute } = useMemo(() => {
    if (!date) return { relative: '-', absolute: '' };

    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return { relative: '-', absolute: '' };

    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

    // Absolute format for tooltip
    const absoluteFormatter = new Intl.DateTimeFormat(language, {
      dateStyle: 'full',
      timeStyle: 'medium',
    });
    const absoluteStr = absoluteFormatter.format(dateObj);

    // Relative format
    const rtf = new Intl.RelativeTimeFormat(language, { numeric: 'auto' });

    let relativeStr = '';
    if (diffInSeconds < 60) {
      relativeStr = rtf.format(-diffInSeconds, 'second');
    } else if (diffInSeconds < 3600) {
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 60), 'minute');
    } else if (diffInSeconds < 86400) {
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 3600), 'hour');
    } else if (diffInSeconds < 604800) { // 7 days
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 86400), 'day');
    } else if (diffInSeconds < 2592000) { // 30 days
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 604800), 'week');
    } else if (diffInSeconds < 31536000) { // 365 days
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 2592000), 'month');
    } else {
      relativeStr = rtf.format(-Math.floor(diffInSeconds / 31536000), 'year');
    }

    return { relative: relativeStr, absolute: absoluteStr };
  }, [date, language]);

  if (!date) return <span className="text-muted-foreground">-</span>;

  return (
    <span title={absolute} className="cursor-help underline decoration-dotted underline-offset-2">
      {relative}
    </span>
  );
}
