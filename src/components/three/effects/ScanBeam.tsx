import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

type ScanBeamProps = {
  active: boolean;
  reducedMotion?: boolean;
  width?: number;
  height?: number;
};

/**
 * A soft, glowing horizontal beam that sweeps across the retinal surface
 * while the image is being processed.
 */
export function ScanBeam({ active, reducedMotion = false, width = 3.4, height = 0.1 }: ScanBeamProps) {
  const ref = useRef<THREE.Mesh>(null);
  const range = 2.6;

  useFrame(({ clock }) => {
    const mesh = ref.current;
    if (!mesh || !active || reducedMotion) return;
    const t = (clock.elapsedTime % 2.4) / 2.4;
    mesh.position.y = range * 0.5 - t * range;
  });

  const geometry = useMemo(() => new THREE.PlaneGeometry(width, height), [width, height]);
  const material = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: '#4fd1c5',
        transparent: true,
        opacity: 0.55,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      }),
    [],
  );

  if (!active) return null;

  return <mesh ref={ref} geometry={geometry} material={material} position={[0, 0, 0.02]} />;
}