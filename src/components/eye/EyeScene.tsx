import { OrbitControls } from '@react-three/drei';
import type { MutableRefObject } from 'react';
import { EyeModel } from './EyeModel';
import { EyeLabels } from './EyeLabels';
import { EyeCameraController, type CameraRequest } from './EyeCameraController';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import type { EyeStructureId } from '@/data/eyeAnatomy';

export type EyeSceneProps = {
  selected: EyeStructureId | null;
  hovered: EyeStructureId | null;
  internal: boolean;
  showLabels: boolean;
  explodeAmount: number;
  reducedMotion: boolean;
  labels: Record<EyeStructureId, string>;
  interactingRef: MutableRefObject<boolean>;
  controlsRef: MutableRefObject<OrbitControlsImpl | null>;
  requestRef: MutableRefObject<CameraRequest | null>;
  onSelect: (id: EyeStructureId | null) => void;
  onHover: (id: EyeStructureId | null) => void;
};

export function EyeScene({
  selected,
  hovered,
  internal,
  showLabels,
  explodeAmount,
  reducedMotion,
  labels,
  interactingRef,
  controlsRef,
  requestRef,
  onSelect,
  onHover,
}: EyeSceneProps) {
  return (
    <>
      <hemisphereLight args={['#ffffff', '#0a2233', 0.5]} />
      <directionalLight position={[5, 8, 7]} intensity={2.4} color="#ffffff" />
      <directionalLight position={[-6, -3, 5]} intensity={1.1} color="#cffafe" />
      <pointLight position={[0, 0, 5]} intensity={0.8} color="#e0f2fe" />
      <pointLight position={[0, 3, -6]} intensity={0.5} color="#14b8a6" />

      <EyeModel
        selected={selected}
        hovered={hovered}
        internal={internal}
        explodeAmount={explodeAmount}
        reducedMotion={reducedMotion}
        interactingRef={interactingRef}
        onSelect={onSelect}
        onHover={onHover}
      />

      <EyeLabels showLabels={showLabels} selected={selected} hovered={hovered} labels={labels} />

      <OrbitControls
        ref={(instance) => {
          controlsRef.current = instance;
        }}
        makeDefault
        enableDamping
        dampingFactor={0.08}
        enablePan
        minDistance={1.5}
        maxDistance={8.5}
        onStart={() => {
          interactingRef.current = true;
        }}
        onEnd={() => {
          interactingRef.current = false;
        }}
      />

      <EyeCameraController
        controlsRef={controlsRef}
        requestRef={requestRef}
        interactingRef={interactingRef}
        reducedMotion={reducedMotion}
      />
    </>
  );
}