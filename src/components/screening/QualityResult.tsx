import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { StatusMessage } from '@/components/common/StatusMessage';
import { Button } from '@/components/common/Button';
import { IconWarning, IconRefresh } from '@/components/common/Icons';
import { QUALITY_REASON_KEYS } from '@/utils/constants';
import type { QualityReason } from '@/types/screening';

type QualityResultProps = {
  reason: QualityReason;
  onRecapture: () => void;
};

export function QualityResult({ reason, onRecapture }: QualityResultProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();

  const reasonKey = reason ? QUALITY_REASON_KEYS[reason] : 'quality.whyInsufficient';

  return (
    <motion.div
      className="screen"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.35 }}
    >
      <StatusMessage tone="warning" icon={<IconWarning />} heading={t('quality.headingUnsuitable')}>
        <p className="quality__reason">{t(reasonKey)}</p>
        <p className="quality__recapture">{t('quality.unsuitable')}</p>
        <p className="quality__recapture">{t('quality.recapture')}</p>
      </StatusMessage>

      <div className="quality__actions">
        <Button onClick={onRecapture} icon={<IconRefresh />}>
          {t('quality.recaptureButton')}
        </Button>
      </div>
    </motion.div>
  );
}