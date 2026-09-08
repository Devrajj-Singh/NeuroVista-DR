import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { ReferralStatus } from './ReferralStatus';
import { GradCAMPreview } from './GradCAMPreview';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { IconHome, IconScan, IconReport } from '@/components/common/Icons';
import { formatPercent } from '@/utils/formatters';
import type { Prediction } from '@/types/screening';

type DRResultProps = {
  prediction: Prediction;
  previewUrl: string;
  gradcamAvailable: boolean;
  heatmapImage?: string;
  onHome: () => void;
  onViewExplanation: () => void;
  onViewReport: () => void;
};

const GRADE_SCALE = [0, 1, 2, 3, 4] as const;
const RING_RADIUS = 54;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

export function DRResult({
  prediction,
  previewUrl,
  gradcamAvailable,
  heatmapImage,
  onHome,
  onViewExplanation,
  onViewReport,
}: DRResultProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const grade = Math.min(Math.max(prediction.icdr_grade, 0), 4);
  const severityKey =
    grade >= 0 && grade <= 4 ? `icdr.grade${grade}` : 'icdr.grade2';
  const ringFill = (grade / 4) * RING_CIRCUMFERENCE;
  const confidencePct = Math.round(
    Math.min(Math.max(prediction.confidence, 0), 1) * 100,
  );
  const confidence = formatPercent(prediction.confidence);

  return (
    <motion.div
      className="dr-result"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.4 }}
    >
      <div className="result-topbar">
        <button type="button" className="result-home" onClick={onHome}>
          <IconHome />
          <span>{t('nav.home')}</span>
        </button>
        <h1 className="page-title result-topbar__title">{t('result.title')}</h1>
      </div>

      <Card padded={false} className="result-hero">
        <div className="result-hero__inner" data-grade={grade}>
          <div className="result-hero__score">
            <div className="result-ring">
              <svg className="result-ring__svg" viewBox="0 0 128 128" aria-hidden="true">
                <circle
                  className="result-ring__track"
                  cx="64"
                  cy="64"
                  r={RING_RADIUS}
                  fill="none"
                  strokeWidth="10"
                />
                <circle
                  className="result-ring__value"
                  cx="64"
                  cy="64"
                  r={RING_RADIUS}
                  fill="none"
                  strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={`${ringFill} ${RING_CIRCUMFERENCE - ringFill}`}
                  transform="rotate(-90 64 64)"
                />
              </svg>
              <div className="result-ring__center">
                <span className="result-ring__grade">{grade}</span>
                <span className="result-ring__label">{t('result.severityScale')}</span>
              </div>
            </div>

            <div className="result-severity" data-grade={grade}>
              {t(severityKey)}
            </div>

            <div className="result-scale" role="img" aria-label={t('result.severityScale')}>
              {GRADE_SCALE.map((g) => (
                <span
                  key={g}
                  className={`result-scale__dot${g === grade ? ' result-scale__dot--active' : ''}`}
                  aria-hidden="true"
                >
                  {g}
                </span>
              ))}
            </div>
          </div>

          <div className="result-hero__summary">
            <h2 className="result-hero__title">{t('result.overallResult')}</h2>

            <div className="result-stats">
              <div className="result-stat">
                <span className="result-stat__label">{t('result.drGrade')}</span>
                <span className="result-stat__value result-stat__value--grade" data-grade={grade}>
                  {prediction.icdr_grade}
                </span>
              </div>
              <div className="result-stat">
                <span className="result-stat__label">{t('result.severity')}</span>
                <span className="result-stat__value">{t(severityKey)}</span>
              </div>
              <div className="result-stat">
                <span className="result-stat__label">{t('result.confidence')}</span>
                <span className="result-stat__value">{confidence}</span>
              </div>
            </div>

            <div className="result-confidence">
              <div className="result-confidence__bar" aria-hidden="true">
                <div className="result-confidence__fill" style={{ width: `${confidencePct}%` }} />
              </div>
            </div>

            <ReferralStatus referable={prediction.referable_dr} />
          </div>
        </div>
      </Card>

      <div className="result-body">
        <Card className="result-heatmap">
          <div className="gradcam-preview">
            <div className="gradcam-preview__head">
              <h3 className="gradcam-preview__title">{t('gradcam.title')}</h3>
              <span
                className={`eye-info__selected ${gradcamAvailable ? 'eye-info__selected--ok' : 'eye-info__selected--na'}`}
              >
                {gradcamAvailable ? 'Grad-CAM' : t('eye.unavailable')}
              </span>
            </div>
            <GradCAMPreview previewUrl={previewUrl} available={gradcamAvailable} heatmapImage={heatmapImage} />
          </div>
        </Card>

        <Card className="result-notes">
          <h3 className="result-notes__title">{t('result.viewExplanation')}</h3>
          <p className="dr-result__note">{t('result.screeningResultNote')}</p>
          <p className="dr-result__disclaimer">{t('result.notDiagnosis')}</p>
          <div className="result-actions">
            <Button variant="secondary" onClick={onViewExplanation} icon={<IconScan />}>
              {t('result.viewExplanation')}
            </Button>
            <Button onClick={onViewReport} icon={<IconReport />}>
              {t('result.viewReport')}
            </Button>
          </div>
        </Card>
      </div>
    </motion.div>
  );
}