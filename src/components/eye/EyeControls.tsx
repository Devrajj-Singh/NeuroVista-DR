import { CAMERA_PRESETS } from '@/data/eyeAnatomy';
import { useLocalization } from '@/i18n';
import type { CameraRequest } from './EyeCameraController';

export type EyeControlsProps = {
  onRequest: (request: CameraRequest) => void;
};

export function EyeControls({ onRequest }: EyeControlsProps) {
  const { t } = useLocalization();
  return (
    <div className="eye-controls" role="group" aria-label={t('eye.camera.controls')}>
      {CAMERA_PRESETS.map((preset) => (
        <button
          key={preset.id}
          type="button"
          className="eye-btn"
          onClick={() => onRequest({ kind: 'preset', preset: preset.id })}
        >
          {t(`eye.presets.${preset.id}`)}
        </button>
      ))}
      <span className="eye-controls__sep" aria-hidden="true" />
      <button
        type="button"
        className="eye-btn eye-btn--icon"
        aria-label={t('eye.camera.zoomIn')}
        title={t('eye.camera.zoomIn')}
        onClick={() => onRequest({ kind: 'zoom', direction: 1 })}
      >
        +
      </button>
      <button
        type="button"
        className="eye-btn eye-btn--icon"
        aria-label={t('eye.camera.zoomOut')}
        title={t('eye.camera.zoomOut')}
        onClick={() => onRequest({ kind: 'zoom', direction: -1 })}
      >
        &minus;
      </button>
    </div>
  );
}