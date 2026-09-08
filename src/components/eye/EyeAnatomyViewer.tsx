import { Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import '@/styles/eyeViewer.css';
import { EyeScene } from './EyeScene';
import { EyeControls } from './EyeControls';
import { EyeLayerPanel } from './EyeLayerPanel';
import { EyeInfoPanel } from './EyeInfoPanel';
import { WebGLFallback } from './WebGLFallback';
import { structureLabels } from './eyeLabels';
import { useLocalization } from '@/i18n';
import type { CameraRequest } from './EyeCameraController';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import type { EyeStructureId } from '@/data/eyeAnatomy';
import { useReducedMotion } from '@/hooks/useReducedMotion';

function isWebGLSupported(): boolean {
  if (typeof window === 'undefined') return false;
  const canvas = document.createElement('canvas');
  const gl =
    canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  return Boolean(gl);
}

export default function EyeAnatomyViewer() {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const labels = useMemo(() => structureLabels(t), [t]);
  const [supported] = useState(isWebGLSupported);
  const [selected, setSelected] = useState<EyeStructureId | null>(null);
  const [hovered, setHovered] = useState<EyeStructureId | null>(null);
  const [internal, setInternal] = useState(false);
  const [showLabels, setShowLabels] = useState(false);
  const [explodeAmount, setExplodeAmount] = useState(0);
  const [panelCollapsed, setPanelCollapsed] = useState(false);

  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const requestRef = useRef<CameraRequest | null>(null);
  const interactingRef = useRef(false);

  const handleSelect = (id: EyeStructureId | null) => {
    setSelected(id);
    requestRef.current = id
      ? { kind: 'focus', id }
      : { kind: 'preset', preset: 'reset' };
  };
  const handleRequest = (request: CameraRequest) => {
    requestRef.current = request;
  };

  useEffect(() => {
    if (!import.meta.env.DEV) return;
    (window as unknown as Record<string, unknown>).__eyeViewer = {
      selected: selected ?? null,
      internal,
      showLabels,
      explodeAmount,
    };
  }, [selected, internal, showLabels, explodeAmount]);

  if (!supported) {
    return <WebGLFallback />;
  }

  return (
    <div className="eye-viewer">
      <div className="eye-viewer__topbar">
        <div className="eye-viewer__heading">
          <h3 className="eye-viewer__title">{t('explore.title')}</h3>
          <p className="eye-viewer__note">
            {t('explore.disclaimer')}
          </p>
        </div>
      </div>

      <div className="eye-viewer__stage">
        <div className="eye-viewer__canvas" role="img" aria-label={t('explore.title')}>
          <Suspense fallback={<div className="eye-viewer__loading">{t('explore.loading')}</div>}>
            <Canvas
              dpr={[1, 1.5]}
              gl={{ antialias: true, alpha: true, powerPreference: 'default' }}
              camera={{ position: [2.8, 1.25, 3.8], fov: 42 }}
            >
              <EyeScene
                selected={selected}
                hovered={hovered}
                internal={internal}
                showLabels={showLabels}
                explodeAmount={explodeAmount}
                reducedMotion={reducedMotion}
                labels={labels}
                interactingRef={interactingRef}
                controlsRef={controlsRef}
                requestRef={requestRef}
                onSelect={handleSelect}
                onHover={setHovered}
              />
            </Canvas>
          </Suspense>

          <div className="eye-viewer__instr">
            {t('eye.instruction')}
          </div>

          <EyeControls onRequest={handleRequest} />

          <EyeInfoPanel
            selected={selected}
            labels={labels}
            onFocus={() => undefined}
            onClose={() => handleSelect(null)}
            onRequest={handleRequest}
          />
        </div>

        <EyeLayerPanel
          selected={selected}
          internal={internal}
          showLabels={showLabels}
          collapsed={panelCollapsed}
          labels={labels}
          onSelect={handleSelect}
          onToggleCollapsed={() => setPanelCollapsed((v) => !v)}
          onToggleInternal={() => setInternal((v) => !v)}
          onToggleLabels={() => setShowLabels((v) => !v)}
          explodeAmount={explodeAmount}
          onExplodeAmount={setExplodeAmount}
          onRequest={handleRequest}
        />
      </div>

      <p className="eye-viewer__announce" role="status" aria-live="polite">
        {selected ? `${labels[selected]} ${t('eye.selected')}` : ''}
      </p>
    </div>
  );
}