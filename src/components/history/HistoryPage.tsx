import { useCallback, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { formatPercent } from '@/utils/formatters';
import { Card } from '@/components/common/Card';
import { IconChevronRight, IconTrash } from '@/components/common/Icons';
import {
  clearHistory,
  getHistoryEntries,
  type HistoryEntry,
} from '@/services/history';

type HistoryPageProps = {
  onSelect: (entry: HistoryEntry) => void;
};

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

export function HistoryPage({ onSelect }: HistoryPageProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const [entries, setEntries] = useState<HistoryEntry[]>(() => getHistoryEntries());

  const refresh = useCallback(() => setEntries(getHistoryEntries()), []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function handleClear() {
    clearHistory();
    refresh();
  }

  return (
    <motion.div
      className="history-page"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.35 }}
    >
      <div className="screen__intro history-page__head">
        <h1 className="page-title">{t('history.title')}</h1>
        <p className="screen__desc">{t('history.subtitle')}</p>
        {entries.length > 0 && (
          <button type="button" className="history-page__clear" onClick={handleClear}>
            <IconTrash /> {t('history.clear')}
          </button>
        )}
      </div>

      {entries.length === 0 ? (
        <Card>
          <p className="history-page__empty">{t('history.empty')}</p>
        </Card>
      ) : (
        <ul className="history-list">
          {entries.map((entry) => {
            const gradeKey = entry.grade >= 0 && entry.grade <= 4 ? `icdr.grade${entry.grade}` : 'icdr.grade2';
            return (
              <li key={entry.id}>
                <Card padded={false}>
                  <button
                    type="button"
                    className="history-item"
                    onClick={() => onSelect(entry)}
                  >
                    <span className="history-item__thumb" aria-hidden="true">
                      {entry.previewUrl && (entry.previewUrl.startsWith('data:') || entry.previewUrl.startsWith('http')) ? (
                        <img src={entry.previewUrl} alt="" />
                      ) : (
                        <span className="history-item__placeholder" />
                      )}
                    </span>
                    <span className="history-item__body">
                      <span className="history-item__name">{entry.filename}</span>
                      <span className="history-item__meta">{formatDate(entry.date)}</span>
                    </span>
                    <span className="history-item__grade">
                      <span className="history-item__grade-badge">DR {entry.grade}</span>
                      <span className="history-item__severity">{t(gradeKey)}</span>
                    </span>
                    <span className="history-item__conf">{formatPercent(entry.confidence)}</span>
                    <span
                      className={`history-item__flag ${entry.referable ? 'history-item__flag--danger' : 'history-item__flag--success'}`}
                    >
                      {entry.referable ? t('result.referable') : t('result.nonReferable')}
                    </span>
                    <IconChevronRight className="history-item__chevron" />
                  </button>
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </motion.div>
  );
}
