import { getEyeStructure, type EyeStructureId } from '@/data/eyeAnatomy';
import { useLocalization } from '@/i18n';
import type { CameraRequest } from './EyeCameraController';

export type EyeInfoPanelProps = {
  selected: EyeStructureId | null;
  labels: Record<EyeStructureId, string>;
  onFocus: () => void;
  onClose: () => void;
  onRequest: (request: CameraRequest) => void;
};

export function EyeInfoPanel({ selected, labels, onFocus, onClose, onRequest }: EyeInfoPanelProps) {
  const { t } = useLocalization();
  const structure = getEyeStructure(selected);
  if (!structure) return null;

  return (
    <div
      className="eye-info"
      role="region"
      aria-live="polite"
      aria-label={`${labels[structure.id]} information`}
    >
      <div className="eye-info__head">
        <h4 className="eye-info__title">{labels[structure.id]}</h4>
        <span className="eye-info__selected">{t('eye.selected')}</span>
        <button
          type="button"
          className="eye-btn eye-btn--small"
          aria-label={t('eye.close')}
          onClick={onClose}
        >
          {t('eye.close')}
        </button>
      </div>
      <p className="eye-info__desc">{structure.description}</p>
      <p className="eye-info__detail">{structure.detail}</p>
      <div className="eye-info__actions">
        <button
          type="button"
          className="eye-mode eye-mode--active"
          onClick={() => {
            onFocus();
            onRequest({ kind: 'focus', id: structure.id, deep: true });
          }}
        >
          {t('eye.focusStructure')}
        </button>
      </div>
    </div>
  );
}