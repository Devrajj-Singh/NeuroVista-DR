import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * Subtle decorative depth ring rendered behind the Grad-CAM viewer.
 * The clinical image always stays in sharp 2D focus; this never overlaps it.
 */
export function GradCAMScene() {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const ring = ringRef.current;
    if (!ring) return;
    ring.rotation.x = Math.sin(clock.elapsedTime * 0.2) * 0.15;
    ring.rotation.y = clock.elapsedTime * 0.1;
  });

  return (
    <group position={[0, 0, -2]}>
      <ambientLight intensity={0.4} />
      <mesh ref={ringRef}>
        <torusGeometry args={[1.6, 0.02, 12, 64]} />
        <meshBasicMaterial color="#4fd1c5" transparent opacity={0.16} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[1.7, 1.73, 64]} />
        <meshBasicMaterial color="#1f4470" transparent opacity={0.12} />
      </mesh>
    </group>
  );
}