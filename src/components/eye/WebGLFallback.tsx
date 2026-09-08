import { useMemo } from 'react';
import { EYE_STRUCTURES } from '@/data/eyeAnatomy';
import { structureLabels } from './eyeLabels';
import { useLocalization } from '@/i18n';

export function WebGLFallback() {
  const { t } = useLocalization();
  const labels = useMemo(() => structureLabels(t), [t]);
  return (
    <div className="eye-fallback" role="status">
      <h3 className="eye-fallback__title">{t('eye.fallbackTitle')}</h3>
      <p className="eye-fallback__text">{t('eye.fallbackText')}</p>
      <ul className="eye-fallback__list">
        {EYE_STRUCTURES.map((structure) => (
          <li key={structure.id}>{labels[structure.id]}</li>
        ))}
      </ul>
    </div>
  );
}