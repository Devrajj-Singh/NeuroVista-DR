import { AnimatePresence, motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { ThreeCanvas } from '@/components/three/ThreeCanvas';
import { RetinalScanner } from '@/components/three/RetinalScanner';
import { AIAnalysisPipeline } from '@/components/three/AIAnalysisPipeline';
import { Card } from '@/components/common/Card';
import type { ProcessingStage } from '@/types/screening';

type ProcessingScreenProps = {
  stage: ProcessingStage;
};

const STAGE_KEYS = ['processing.checkingQuality', 'processing.analyzingRetina', 'processing.generatingExplanation'];

export function ProcessingScreen({ stage }: ProcessingScreenProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      className="processing"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.3 }}
      aria-busy="true"
      aria-live="polite"
    >
      <h1 className="page-title">{t('processing.title')}</h1>

      <div className="processing__grid">
        <Card padded={false} className="processing__scanner">
          <div className="processing__canvas">
            <ThreeCanvas camera={{ position: [0, 0, 4.2], fov: 50 }} fallbackMessage={t('processing.pleaseWait')}>
              <RetinalScanner processingStage={stage} reducedMotion={reducedMotion} />
            </ThreeCanvas>
          </div>
        </Card>

        <Card>
          <ol className="processing__stages">
            {STAGE_KEYS.map((key, index) => {
              const status = index < stage ? 'done' : index === stage ? 'active' : 'pending';
              return (
                <motion.li
                  key={key}
                  className={`processing__stage processing__stage--${status}`}
                  initial={{ opacity: 0, x: reducedMotion ? 0 : -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.15 }}
                  aria-current={status === 'active' ? 'step' : undefined}
                >
                  <span className="processing__marker" aria-hidden="true">
                    {status === 'done' ? '✓' : status === 'active' ? '●' : '○'}
                  </span>
                  <span className="processing__label">{t(key)}</span>
                </motion.li>
              );
            })}
          </ol>
          <p className="processing__hint">{t('processing.pleaseWait')}</p>
        </Card>
      </div>

      <AnimatePresence>
        <Card className="processing__pipeline">
          <div className="processing__pipeline-canvas">
            <ThreeCanvas camera={{ position: [0, 0, 5.2], fov: 45 }} fallbackMessage="">
              <AIAnalysisPipeline processingStage={stage} reducedMotion={reducedMotion} />
            </ThreeCanvas>
          </div>
        </Card>
      </AnimatePresence>
    </motion.div>
  );
}