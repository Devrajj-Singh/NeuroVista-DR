import { useLocalization } from '@/i18n';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { formatFileSize } from '@/utils/validators';

type ImagePreviewProps = {
  previewUrl: string;
  filename: string;
  fileSize: number;
  onChangeImage: () => void;
  onAnalyze: () => void;
  canAnalyze: boolean;
  analyzing?: boolean;
};

export function ImagePreview({
  previewUrl,
  filename,
  fileSize,
  onChangeImage,
  onAnalyze,
  canAnalyze,
  analyzing = false,
}: ImagePreviewProps) {
  const { t } = useLocalization();

  return (
    <div className="image-preview">
      <Card padded={false}>
        <div className="image-preview__viewer">
          <img
            src={previewUrl}
            alt={t('preview.title')}
            className="image-preview__image"
            referrerPolicy="no-referrer"
          />
        </div>
      </Card>

      <Card>
        <div className="image-preview__meta">
          <div className="image-preview__meta-item">
            <span className="image-preview__label">{t('upload.selectedFile')}</span>
            <span className="image-preview__value">{filename}</span>
          </div>
          <div className="image-preview__meta-item">
            <span className="image-preview__label">{t('preview.size')}</span>
            <span className="image-preview__value">{formatFileSize(fileSize)}</span>
          </div>
        </div>

        <div className="image-preview__actions">
          <Button variant="ghost" onClick={onChangeImage} disabled={analyzing}>
            {t('upload.changeImage')}
          </Button>
          <Button onClick={onAnalyze} disabled={!canAnalyze || analyzing} loading={analyzing}>
            {t('common.analyze')}
          </Button>
        </div>
      </Card>
    </div>
  );
}