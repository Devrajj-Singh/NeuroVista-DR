import { useLocalization } from '@/i18n';
import { StatusMessage } from '@/components/common/StatusMessage';
import { IconInfo, IconWarning } from '@/components/common/Icons';

type ExplanationPanelProps = {
  available: boolean;
};

export function ExplanationPanel({ available }: ExplanationPanelProps) {
  const { t } = useLocalization();

  if (!available) {
    return (
      <StatusMessage tone="info" icon={<IconWarning />} heading={t('gradcam.unavailable')}>
        <p>{t('gradcam.unavailableHint')}</p>
      </StatusMessage>
    );
  }

  return (
    <StatusMessage tone="info" icon={<IconInfo />} heading={t('gradcam.subtitle')}>
      <p>{t('gradcam.notDiagnosis')}</p>
    </StatusMessage>
  );
}