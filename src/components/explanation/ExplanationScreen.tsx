import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { ThreeCanvas } from '@/components/three/ThreeCanvas';
import { GradCAMScene } from '@/components/three/GradCAMScene';
import { FundusViewer } from './FundusViewer';
import { GradCAMViewer } from './GradCAMViewer';
import { ExplanationPanel } from './ExplanationPanel';
import { Button } from '@/components/common/Button';
import type { Explainability } from '@/types/screening';

type ExplanationScreenProps = {
  previewUrl: string;
  explanation: Explainability | null;
  onViewReport: () => void;
  onBackToResult: () => void;
};

export function ExplanationScreen({
  previewUrl,
  explanation,
  onViewReport,
  onBackToResult,
}: ExplanationScreenProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const available = explanation?.gradcam_available === true;

  return (
    <motion.div
      className="explanation"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.35 }}
    >
      <div className="explanation__ring" aria-hidden="true">
        <ThreeCanvas camera={{ position: [0, 0, 4], fov: 45 }} fallbackMessage="">
          <GradCAMScene />
        </ThreeCanvas>
      </div>

      <h1 className="page-title">{t('gradcam.title')}</h1>

      <div className="explanation__grid">
        <figure className="explanation__figure">
          <figcaption>{t('gradcam.originalImage')}</figcaption>
          <FundusViewer previewUrl={previewUrl} />
        </figure>

        <figure className="explanation__figure">
          <figcaption>{t('gradcam.modelExplanation')}</figcaption>
          <GradCAMViewer previewUrl={previewUrl} available={available} />
        </figure>
      </div>

      <div className="explanation__panel">
        <ExplanationPanel available={available} />
      </div>

      <div className="explanation__actions">
        <Button variant="ghost" onClick={onBackToResult}>
          {t('result.backToResult')}
        </Button>
        <Button onClick={onViewReport}>{t('result.viewReport')}</Button>
      </div>
    </motion.div>
  );
}