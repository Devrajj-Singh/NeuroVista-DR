import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { ProcessingStage } from '@/types/screening';
import { ScanBeam } from './effects/ScanBeam';
import { DataParticles } from './effects/DataParticles';
import { useRetinalVessels } from './vessels';

type RetinalScannerProps = {
  processingStage: ProcessingStage;
  reducedMotion?: boolean;
};

const DISC_RADIUS = 1.6;

function createRetinaTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);
  const gradient = ctx.createRadialGradient(256, 256, 16, 256, 256, 256);
  gradient.addColorStop(0, '#0d9488');
  gradient.addColorStop(0.45, '#0a6b6b');
  gradient.addColorStop(1, '#052e33');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 512, 512);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Primary 3D visualization for the processing screen.
 * A translucent retinal disc is scanned by a moving beam; the stage prop
 * drives the scan, orbiting particles and glowing regions.
 */
export function RetinalScanner({ processingStage, reducedMotion = false }: RetinalScannerProps) {
  const discRef = useRef<THREE.Mesh>(null);
  const glowGroupRef = useRef<THREE.Group>(null);
  const vessels = useRetinalVessels(7, DISC_RADIUS);

  const texture = useMemo(() => createRetinaTexture(), []);
  const beachStage = processingStage >= 1;

  const glowSpots = useMemo(
    () => [
      { pos: [-0.4, 0.35], color: '#38ddf8' },
      { pos: [0.55, -0.25], color: '#14b8a6' },
      { pos: [0.15, 0.7], color: '#7cefe3' },
    ],
    [],
  );

  useFrame(({ clock }) => {
    const disc = discRef.current;
    if (disc && !reducedMotion) {
      disc.rotation.z = Math.sin(clock.elapsedTime * 0.35) * 0.06;
    }
    const glowGroup = glowGroupRef.current;
    if (glowGroup && processingStage >= 2 && !reducedMotion) {
      const intensity = 0.55 + Math.sin(clock.elapsedTime * 2.2) * 0.2;
      glowGroup.children.forEach((child, i) => {
        const mat = (child as THREE.Mesh).material as THREE.MeshBasicMaterial;
        mat.opacity = 0.25 + intensity * (0.55 - i * 0.1);
      });
    }
  });

  return (
    <group>
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 3, 5]} intensity={1.1} />

      {/* Retinal disc */}
      <mesh ref={discRef} rotation={[-0.1, 0, 0]}>
        <circleGeometry args={[DISC_RADIUS, 64]} />
        <meshStandardMaterial map={texture} roughness={0.9} metalness={0} side={THREE.DoubleSide} />
      </mesh>

      {/* Rim */}
      <mesh rotation={[-0.1, 0, 0]} position={[0, 0, -0.01]}>
        <ringGeometry args={[DISC_RADIUS, DISC_RADIUS + 0.04, 96]} />
        <meshBasicMaterial color={beachStage ? '#4fd1c5' : '#1f4470'} transparent opacity={0.6} />
      </mesh>

      {/* Vessels */}
      {vessels.map((v, i) => (
        <mesh key={i} geometry={v.tube} material={v.mat} rotation={[-0.1, 0, 0]} />
      ))}

      {/* Glow regions for stage 3 */}
      <group ref={glowGroupRef}>
        {processingStage >= 2 &&
          glowSpots.map((spot, i) => (
            <mesh key={i} position={[spot.pos[0], spot.pos[1], 0.04]} scale={0.22}>
              <sphereGeometry args={[1, 16, 16]} />
              <meshBasicMaterial
                color={spot.color}
                transparent
                opacity={0}
                blending={THREE.AdditiveBlending}
                depthWrite={false}
              />
            </mesh>
          ))}
      </group>

      <ScanBeam active={processingStage >= 0} reducedMotion={reducedMotion} />
      <DataParticles active={processingStage >= 1} reducedMotion={reducedMotion} />
    </group>
  );
}