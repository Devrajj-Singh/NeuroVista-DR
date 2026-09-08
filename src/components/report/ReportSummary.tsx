import { useLocalization } from '@/i18n';
import { formatPercent } from '@/utils/formatters';
import type { Explainability, Prediction, QualityResult } from '@/types/screening';

type ReportSummaryProps = {
  quality: QualityResult;
  prediction: Prediction;
  explanation: Explainability | null;
};

function SummaryRow({ label, value, strong }: { label: string; value: string; strong?: boolean }) {
  return (
    <div className={`report-row${strong ? ' report-row--strong' : ''}`}>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

export function ReportSummary({ quality, prediction, explanation }: ReportSummaryProps) {
  const { t } = useLocalization();
  const severityKey = `icdr.grade${Math.min(prediction.icdr_grade, 4)}`;

  return (
    <dl className="report-summary">
      <SummaryRow
        label={t('report.imageQuality')}
        value={quality.status === 'good' ? t('quality.good') : t('quality.headingUnsuitable')}
        strong
      />
      <SummaryRow label={t('report.drGrade')} value={`${t('icdr.gradeLabel')} ${prediction.icdr_grade}`} strong />
      <SummaryRow label={t('report.severity')} value={t(severityKey)} />
      <SummaryRow
        label={t('report.referralStatus')}
        value={prediction.referable_dr ? t('result.referable') : t('result.nonReferable')}
        strong
      />
      <SummaryRow label={t('report.confidence')} value={formatPercent(prediction.confidence)} />
      <SummaryRow
        label={t('report.modelExplanation')}
        value={
          explanation?.gradcam_available
            ? t('report.gradcamAvailable')
            : t('report.gradcamUnavailable')
        }
      />
    </dl>
  );
}