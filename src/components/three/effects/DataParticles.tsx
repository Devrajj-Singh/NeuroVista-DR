import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

type DataParticlesProps = {
  active: boolean;
  reducedMotion?: boolean;
  count?: number;
};

const COLORS = ['#4fd1c5', '#7dd3fc', '#a5f3fc'];

/**
 * Small data-like particles that orbit the retinal disc while analysis runs.
 * Purely decorative — represents data flow, not real measurements.
 */
export function DataParticles({ active, reducedMotion = false, count = 28 }: DataParticlesProps) {
  const groupRef = useRef<THREE.Group>(null);

  const particles = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const angle = (i / count) * Math.PI * 2;
      return {
        radius: 1.15 + (i % 3) * 0.18,
        angle,
        speed: 0.4 + ((i * 0.7) % 0.8),
        color: COLORS[i % COLORS.length],
        scale: 0.04 + (i % 4) * 0.012,
        floatOffset: i * 0.9,
      };
    });
  }, [count]);

  useFrame(({ clock }) => {
    const group = groupRef.current;
    if (!group || !active || reducedMotion) return;
    group.rotation.z = (clock.elapsedTime ?? 0) * 0.25;
    group.children.forEach((child, i) => {
      const p = particles[i];
      if (!p) return;
      child.position.z = Math.sin(clock.elapsedTime * 1.2 + p.floatOffset) * 0.15;
    });
  });

  if (!active) return null;

  return (
    <group ref={groupRef}>
      {particles.map((p, i) => (
        <mesh key={i} position={[Math.cos(p.angle) * p.radius, Math.sin(p.angle) * p.radius, 0]} scale={p.scale}>
          <sphereGeometry args={[1, 8, 8]} />
          <meshBasicMaterial color={p.color} transparent opacity={0.8} />
        </mesh>
      ))}
    </group>
  );
}