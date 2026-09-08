import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

type BackgroundProps = {
  reducedMotion?: boolean;
  theme?: 'light' | 'dark';
};

/**
 * Full-screen ambient 3D backdrop: a drifting starfield (dark theme) or soft
 * warm sparkles (light theme) plus nebula-like glowing orbs. Renders behind
 * the entire app.
 */
export function BackgroundFX({ reducedMotion = false, theme = 'dark' }: BackgroundProps) {
  const starsRef = useRef<THREE.Points>(null);
  const sparklesRef = useRef<THREE.Points>(null);
  const glowRefA = useRef<THREE.Mesh>(null);
  const glowRefB = useRef<THREE.Mesh>(null);
  const light = theme === 'light';

  const stars = useMemo(() => {
    const count = 700;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 80;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 80;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 60;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return geometry;
  }, []);

  // Soft round sparkle sprite (radial falloff) for the light theme.
  const sparkleTexture = useMemo(() => {
    const size = 64;
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
      gradient.addColorStop(0, 'rgba(255,255,255,1)');
      gradient.addColorStop(0.35, 'rgba(255,255,255,0.6)');
      gradient.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, size, size);
    }
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    return texture;
  }, []);

  const sparkles = useMemo(() => {
    const count = 90;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 70;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 40;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 30;
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    return geometry;
  }, []);

  // Soft nebula blobs (billboarded glow discs)
  const glowMatA = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: light ? '#5eead4' : '#0ea5a9',
        transparent: true,
        opacity: light ? 0.55 : 0.18,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    [light],
  );
  const glowMatB = useMemo(
    () =>
      new THREE.MeshBasicMaterial({
        color: light ? '#a5f3fc' : '#38ddf8',
        transparent: true,
        opacity: light ? 0.5 : 0.12,
        depthWrite: false,
        side: THREE.DoubleSide,
      }),
    [light],
  );
  const sparkleMat = useMemo(() => {
    const material = new THREE.PointsMaterial({
      size: 0.55,
      map: sparkleTexture,
      color: '#e7fbff',
      transparent: true,
      opacity: 0.5,
      depthWrite: false,
      sizeAttenuation: true,
      blending: THREE.AdditiveBlending,
    });
    return material;
  }, [sparkleTexture]);

  useFrame((state) => {
    if (reducedMotion) return;
    const t = state.clock.elapsedTime;
    if (starsRef.current) {
      starsRef.current.rotation.y = t * 0.008;
      starsRef.current.rotation.x = t * 0.004;
    }
    if (sparklesRef.current) {
      sparklesRef.current.rotation.y = t * 0.02;
      sparklesRef.current.position.y = Math.sin(t * 0.4) * 1.2;
    }
    if (sparkleMat.opacity !== undefined) {
      sparkleMat.opacity = 0.42 + Math.sin(t * 1.4) * 0.12;
    }
    if (glowRefA.current) {
      glowRefA.current.position.x = Math.sin(t * 0.12) * 14;
      glowRefA.current.position.y = Math.cos(t * 0.09) * 8;
    }
    if (glowRefB.current) {
      glowRefB.current.position.x = Math.cos(t * 0.1 + 2) * 16;
      glowRefB.current.position.y = Math.sin(t * 0.13 + 1) * 10;
    }
  });

  return (
    <group>
      {!light && (
        <points ref={starsRef} geometry={stars}>
          <pointsMaterial
            size={0.22}
            color="#ffffff"
            transparent
            opacity={0.85}
            sizeAttenuation
            depthWrite={false}
          />
        </points>
      )}
      {light && (
        <points ref={sparklesRef} geometry={sparkles}>
          <primitive object={sparkleMat} attach="material" />
        </points>
      )}
      <mesh ref={glowRefA} position={[-16, 8, -18]}>
        <circleGeometry args={[30, 32]} />
        <primitive object={glowMatA} attach="material" />
      </mesh>
      <mesh ref={glowRefB} position={[18, -9, -22]}>
        <circleGeometry args={[34, 32]} />
        <primitive object={glowMatB} attach="material" />
      </mesh>
    </group>
  );
}