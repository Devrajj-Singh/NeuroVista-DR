import { Card } from '@/components/common/Card';
import { useLocalization } from '@/i18n';

type FundusViewerProps = {
  previewUrl: string;
  alt?: string;
};

export function FundusViewer({ previewUrl, alt }: FundusViewerProps) {
  const { t } = useLocalization();
  return (
    <Card padded={false}>
      <div className="fundus-viewer">
        {previewUrl ? (
          <img src={previewUrl} alt={alt ?? t('gradcam.originalImage')} className="fundus-viewer__img" />
        ) : (
          <div className="fundus-viewer__placeholder">{t('history.noPreview')}</div>
        )}
      </div>
    </Card>
  );
}