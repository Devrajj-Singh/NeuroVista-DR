import { EYE_STRUCTURES, type EyeStructureId } from '@/data/eyeAnatomy';
import { useLocalization } from '@/i18n';
import type { CameraRequest } from './EyeCameraController';

export type EyeLayerPanelProps = {
  selected: EyeStructureId | null;
  internal: boolean;
  showLabels: boolean;
  collapsed: boolean;
  labels: Record<EyeStructureId, string>;
  onSelect: (id: EyeStructureId | null) => void;
  onToggleCollapsed: () => void;
  onToggleInternal: () => void;
  onToggleLabels: () => void;
  explodeAmount: number;
  onExplodeAmount: (amount: number) => void;
  onRequest: (request: CameraRequest) => void;
};

export function EyeLayerPanel({
  selected,
  internal,
  showLabels,
  collapsed,
  labels,
  onSelect,
  onToggleCollapsed,
  onToggleInternal,
  onToggleLabels,
  explodeAmount,
  onExplodeAmount,
  onRequest,
}: EyeLayerPanelProps) {
  const { t } = useLocalization();
  return (
    <aside className={`eye-panel${collapsed ? ' eye-panel--collapsed' : ''}`}>
      <div className="eye-panel__header">
        <h3 className="eye-panel__title">{t('eye.anatomy')}</h3>
        <button
          type="button"
          className="eye-btn eye-btn--small"
          aria-expanded={!collapsed}
          onClick={onToggleCollapsed}
        >
          {collapsed ? t('eye.show') : t('eye.hide')}
        </button>
      </div>

      {!collapsed && (
        <div className="eye-panel__body">
          <div className="eye-viewer__modes">
            <button
              type="button"
              className={`eye-mode${internal ? ' eye-mode--active' : ''}`}
              aria-pressed={internal}
              onClick={onToggleInternal}
            >
              {t('eye.internalView')}
            </button>
            <button
              type="button"
              className={`eye-mode${showLabels ? ' eye-mode--active' : ''}`}
              aria-pressed={showLabels}
              onClick={onToggleLabels}
            >
              {t('eye.showLabels')}
            </button>
          </div>

          <ul className="eye-layer" role="listbox" aria-label="Anatomical structures">
            <li>
              <button
                type="button"
                role="option"
                aria-selected={selected === null}
                className={`eye-layer__item${selected === null ? ' eye-layer__item--active' : ''}`}
                onClick={() => {
                  onSelect(null);
                  onRequest({ kind: 'preset', preset: 'reset' });
                }}
              >
                <span className="eye-layer__dot eye-layer__dot--full" />
                {t('eye.fullEye')}
              </button>
            </li>
            {EYE_STRUCTURES.map((structure) => (
              <li key={structure.id}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected === structure.id}
                  className={`eye-layer__item${selected === structure.id ? ' eye-layer__item--active' : ''}`}
                  onClick={() => onSelect(selected === structure.id ? null : structure.id)}
                >
                  <span className="eye-layer__dot" />
                  {labels[structure.id]}
                </button>
              </li>
            ))}
          </ul>

          <div className="eye-explode">
            <button
              type="button"
              className="eye-mode"
              aria-pressed={explodeAmount > 0}
              onClick={() => onExplodeAmount(explodeAmount > 0 ? 0 : 0.5)}
            >
              {t('eye.explodeView')}
            </button>
            <input
              className="eye-explode__range"
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={explodeAmount}
              aria-label={t('eye.explodeLabel')}
              onChange={(event) => onExplodeAmount(Number(event.target.value))}
            />
          </div>
        </div>
      )}
    </aside>
  );
}