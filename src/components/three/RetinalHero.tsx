import { useEffect, useMemo, useRef } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useRetinalVessels } from './vessels';

type RetinalHeroProps = {
  reducedMotion?: boolean;
  small?: boolean;
  interactive?: boolean;
};

const BASE_SCALE = 0.92;
const ROTATION_SENSITIVITY = 0.005;
const MAX_TILT = Math.PI / 2.2;

function createIrisTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);
  const gradient = ctx.createRadialGradient(128, 128, 62, 128, 128, 128);
  gradient.addColorStop(0, '#2dd4bf');
  gradient.addColorStop(0.55, '#14b8a6');
  gradient.addColorStop(0.85, '#0f766e');
  gradient.addColorStop(1, '#064e3b');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 48; i++) {
    const angle = (i / 48) * Math.PI * 2;
    const inner = 66;
    const outer = 126;
    ctx.beginPath();
    ctx.moveTo(128 + Math.cos(angle) * inner, 128 + Math.sin(angle) * inner);
    ctx.lineTo(128 + Math.cos(angle + 0.08) * outer, 128 + Math.sin(angle + 0.08) * outer);
    ctx.strokeStyle = `rgba(255,255,255,${0.14 + (i % 3) * 0.06})`;
    ctx.lineWidth = 1.6;
    ctx.stroke();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

/**
 * Stylized procedural eye used as the dashboard identity visual.
 * Draggable for full 360° rotation via canvas-level pointer events.
 */
export function RetinalHero({
  reducedMotion = false,
  small = false,
  interactive = false,
}: RetinalHeroProps) {
  const groupRef = useRef<THREE.Group>(null);
  const gl = useThree((s) => s.gl);
  const vessels = useRetinalVessels(5, 0.92, 0.41);
  const irisTexture = useMemo(() => createIrisTexture(), []);

  // Raw target rotation accumulated from pointer deltas (for smooth 360° spin)
  const targetY = useRef(0.2);
  const targetX = useRef(0.15);
  const dragRef = useRef({
    active: false,
    id: -1,
    lastX: 0,
    lastY: 0,
  });
  const hasInteracted = useRef(false);

  useEffect(() => {
    if (!interactive || reducedMotion) return;
    const el = gl.domElement;

    function onDown(e: PointerEvent) {
      hasInteracted.current = true;
      dragRef.current = {
        active: true,
        id: e.pointerId,
        lastX: e.clientX,
        lastY: e.clientY,
      };
    }
    function onMove(e: PointerEvent) {
      if (!dragRef.current.active || e.pointerId !== dragRef.current.id) return;
      const dx = e.clientX - dragRef.current.lastX;
      const dy = e.clientY - dragRef.current.lastY;
      dragRef.current.lastX = e.clientX;
      dragRef.current.lastY = e.clientY;
      targetY.current += dx * ROTATION_SENSITIVITY;
      targetX.current = THREE.MathUtils.clamp(
        targetX.current + dy * ROTATION_SENSITIVITY,
        -MAX_TILT,
        MAX_TILT,
      );
    }
    function onUp(e: PointerEvent) {
      if (dragRef.current.active && e.pointerId === dragRef.current.id) {
        dragRef.current.active = false;
      }
    }

    // Track movement on window so drags continue even if the cursor
    // strays off the canvas element.
    el.addEventListener('pointerdown', onDown);
    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointercancel', onUp);
    return () => {
      el.removeEventListener('pointerdown', onDown);
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
    };
  }, [gl, interactive, reducedMotion]);

  useFrame(({ clock, pointer }) => {
    const group = groupRef.current;
    if (!group) return;

    if (reducedMotion) {
      group.rotation.y = 0.2;
      group.rotation.x = 0.15;
      return;
    }

    if (dragRef.current.active) {
      // While dragging, lock to the accumulated target (full 360° spin on Y)
      group.rotation.y = targetY.current;
      group.rotation.x = targetX.current;
      return;
    }

    if (!hasInteracted.current) {
      // Autonomous idle animation until the user first touches the eye
      targetY.current = 0.2 + Math.sin(clock.elapsedTime * 0.25) * 0.12;
      targetX.current = 0.15 + pointer.y * 0.08;
    }

    // Smoothly chase the target so releases settle without snapping
    group.rotation.y += (targetY.current - group.rotation.y) * 0.12;
    group.rotation.x += (targetX.current - group.rotation.x) * 0.12;
    group.position.y = Math.sin(clock.elapsedTime * 0.6) * 0.04;

    if (import.meta.env.DEV) {
      (window as unknown as Record<string, unknown>).__eyeRotation = [
        group.rotation.x,
        group.rotation.y,
      ];
      (window as unknown as Record<string, unknown>).__eyeTargetY = targetY.current;
    }
  });

  const scale = small ? 0.52 : BASE_SCALE;

  return (
    <group ref={groupRef} scale={scale} rotation={[0.15, 0.2, 0]}>
      <hemisphereLight args={['#ffffff', '#0b2038', 0.8]} />
      <directionalLight position={[4, 6, 6]} intensity={2.2} />
      <directionalLight position={[-5, -2, 4]} intensity={1.1} color="#5eead4" />
      <pointLight position={[0, 0, 4]} intensity={0.9} color="#e0f2fe" />

      {/* Eyeball */}
      <mesh>
        <sphereGeometry args={[1.1, 48, 48]} />
        <meshPhysicalMaterial
          color="#f8fafc"
          roughness={0.16}
          metalness={0.1}
          clearcoat={1}
          clearcoatRoughness={0.08}
          transparent
          opacity={0.95}
        />
      </mesh>

      {/* Cornea highlight */}
      <mesh position={[0.25, 0.32, 0.85]} rotation={[0.15, -0.1, 0]}>
        <circleGeometry args={[0.34, 24]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.2} />
      </mesh>

      {/* Small secondary highlight */}
      <mesh position={[-0.28, -0.18, 0.9]} rotation={[0.1, 0.1, 0]}>
        <circleGeometry args={[0.08, 16]} />
        <meshBasicMaterial color="#ffffff" transparent opacity={0.35} />
      </mesh>

      {/* Iris */}
      <mesh position={[0, 0, 0.93]}>
        <circleGeometry args={[0.56, 48]} />
        <meshStandardMaterial map={irisTexture} roughness={0.28} metalness={0.05} />
      </mesh>

      {/* Pupil */}
      <mesh position={[0, 0, 0.955]}>
        <circleGeometry args={[0.23, 32]} />
        <meshBasicMaterial color="#04070c" />
      </mesh>

      {/* Retinal surface shown through the back — decorative, teal not yellow */}
      <mesh position={[0, 0, -0.55]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.88, 48]} />
        <meshBasicMaterial color="#14b8a6" transparent opacity={0.26} side={THREE.DoubleSide} />
      </mesh>

      {/* Vessels on the inner surface */}
      {vessels.map((v, i) => (
        <mesh key={i} geometry={v.tube} material={v.mat} position={[0, 0, -0.55]} rotation={[Math.PI / 2, 0, 0]} />
      ))}

      {/* Optic nerve head behind the retinal disc — represents the nerve bundle */}
      <mesh position={[0, 0, -0.56]} rotation={[Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.2, 32]} />
        <meshBasicMaterial
          color="#7cefe3"
          transparent
          opacity={0.5}
          side={THREE.DoubleSide}
          depthWrite={false}
        />
      </mesh>
    </group>
  );
}
