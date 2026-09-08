import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { ReportSummary } from './ReportSummary';
import { IconArrowLeft, IconRefresh } from '@/components/common/Icons';
import { formatConfidence } from '@/utils/formatters';
import type { Explainability, Prediction, QualityResult } from '@/types/screening';

type ScreeningReportProps = {
  previewUrl: string;
  quality: QualityResult;
  prediction: Prediction;
  explanation: Explainability | null;
  onBackToResult: () => void;
  onAnalyzeAnother: () => void;
};

export function ScreeningReport({
  previewUrl,
  quality,
  prediction,
  explanation,
  onBackToResult,
  onAnalyzeAnother,
}: ScreeningReportProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();

  const severityKey = `icdr.grade${Math.min(prediction.icdr_grade, 4)}`;
  const confidence = formatConfidence(prediction.confidence);

  return (
    <motion.div
      className="report"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.4 }}
    >
      <div className="report__header">
        <h1 className="report__brand">{t('report.brandLine')}</h1>
        <h2 className="report__title">{t('report.title')}</h2>
        <p className="report__subtitle">{t('report.subtitle')}</p>
      </div>

      <Card className="report__body">
        <div className="report__grid">
          <div className="report__media">
            <div className="report__thumb">
              <img src={previewUrl} alt={t('report.title')} />
            </div>
          </div>

          <div className="report__content">
            <ReportSummary quality={quality} prediction={prediction} explanation={explanation} />
          </div>
        </div>

        <div className="report__recommendation">
          <h3>{t('report.recommendation')}</h3>
          <p>{t('report.recommendationText')}</p>
          <p className="report__confidence-line">
            <strong>{`${confidence}%`}</strong> — {prediction.referable_dr ? t('result.referable') : t('result.nonReferable')}
            {' · '}
            {t(severityKey)}
          </p>
        </div>

        <p className="report__disclaimer">{t('report.disclaimer')}</p>
      </Card>

      <div className="report__actions">
        <Button variant="ghost" onClick={onBackToResult} icon={<IconArrowLeft />}>
          {t('result.backToResult')}
        </Button>
        <Button onClick={onAnalyzeAnother} icon={<IconRefresh />}>
          {t('report.analyzeAnother')}
        </Button>
      </div>
    </motion.div>
  );
}