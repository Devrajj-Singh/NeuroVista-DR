import { useEffect, useMemo, useRef, type ReactNode } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { EyeStructure, EyeStructureId } from '@/data/eyeAnatomy';
import { EYE_STRUCTURES } from '@/data/eyeAnatomy';

type AnatomyNodeProps = {
  config: EyeStructure;
  explodeAmount: number;
  internal: boolean;
  selected: boolean;
  hovered: boolean;
  isolated: boolean;
  forceOpacity?: number;
  onSelect: (id: EyeStructureId) => void;
  onHover: (id: EyeStructureId | null) => void;
  children: ReactNode;
};

function AnatomyNode({
  config,
  explodeAmount,
  internal,
  selected,
  hovered,
  isolated,
  forceOpacity,
  onSelect,
  onHover,
  children,
}: AnatomyNodeProps) {
  const groupRef = useRef<THREE.Group>(null);

  const skipRaycast = internal && config.outer;

  useEffect(() => {
    const group = groupRef.current;
    if (!group) return;
    group.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      if (skipRaycast) {
        mesh.raycast = (() => {}) as unknown as (typeof THREE.Mesh)['prototype']['raycast'];
      } else {
        mesh.raycast = THREE.Mesh.prototype.raycast;
      }
    });
  }, [skipRaycast]);

  useFrame((_, dt) => {
    const group = groupRef.current;
    if (!group) return;

    const [bx, by, bz] = config.base;
    const [e0, e1, e2] = config.explode;
    group.position.set(bx + e0 * explodeAmount, by + e1 * explodeAmount, bz + e2 * explodeAmount);

    let targetOpacity = forceOpacity ?? 1;
    if (config.outer && internal) targetOpacity = config.internalOpacity;
    if (isolated) targetOpacity = selected ? 1 : Math.min(targetOpacity, 0.3);
    const glow = selected ? 0.35 : hovered ? 0.18 : 0;

    group.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (!mesh.isMesh) return;
      const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
      for (const material of materials) {
        material.transparent = true;
        const target = THREE.MathUtils.damp(material.opacity, targetOpacity, 8, dt);
        material.opacity = Math.max(0.001, target);
        const standard = material as THREE.MeshStandardMaterial;
        if (standard.emissive && standard.emissiveIntensity !== undefined) {
          standard.emissive.set('#14b8a6');
          standard.emissiveIntensity = THREE.MathUtils.damp(standard.emissiveIntensity ?? 0, glow, 8, dt);
        }
      }
    });
  });

  return (
    <group
      ref={groupRef}
      onClick={(event) => {
        event.stopPropagation();
        if (event.delta > 4) return;
        onSelect(config.id);
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        onHover(config.id);
      }}
      onPointerOut={(event) => {
        event.stopPropagation();
        onHover(null);
      }}
    >
      {children}
    </group>
  );
}

function createIrisTexture(): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');
  if (!ctx) return new THREE.CanvasTexture(canvas);
  const gradient = ctx.createRadialGradient(128, 128, 58, 128, 128, 128);
  gradient.addColorStop(0, '#c99a5b');
  gradient.addColorStop(0.35, '#8a5a2f');
  gradient.addColorStop(0.7, '#5d3a1f');
  gradient.addColorStop(0.9, '#3b2414');
  gradient.addColorStop(1, '#2a1809');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 120; i++) {
    const angle = Math.random() * Math.PI * 2;
    const inner = 60 + Math.random() * 10;
    const outer = 120 + Math.random() * 8;
    ctx.beginPath();
    ctx.moveTo(128 + Math.cos(angle) * inner, 128 + Math.sin(angle) * inner);
    ctx.lineTo(128 + Math.cos(angle + 0.02) * outer, 128 + Math.sin(angle + 0.02) * outer);
    ctx.strokeStyle = `rgba(40, 22, 8, ${0.18 + Math.random() * 0.3})`;
    ctx.lineWidth = 1.2 + Math.random() * 1.6;
    ctx.stroke();
  }
  for (let i = 0; i < 40; i++) {
    const angle = Math.random() * Math.PI * 2;
    const r = 70 + Math.random() * 50;
    ctx.beginPath();
    ctx.arc(128 + Math.cos(angle) * r, 128 + Math.sin(angle) * r, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 220, 170, ${0.08 + Math.random() * 0.12})`;
    ctx.fill();
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function useRetinalVesselCurves(radius = 0.78): { tube: THREE.TubeGeometry; mat: THREE.MeshBasicMaterial }[] {
  return useMemo(() => {
    const curves = [];
    for (let i = 0; i < 7; i++) {
      const startAngle = (i / 7) * Math.PI * 2 + (i % 3) * 0.35;
      const midAngle = startAngle + 0.5 + (i % 4) * 0.12;
      const endAngle = midAngle + 0.32 + (i % 2) * 0.16;
      const inner = radius * 0.16;
      const outer = radius * (0.66 + (i % 3) * 0.12);
      const r1 = inner + (radius - inner) * 0.3;
      const r2 = inner + (radius - inner) * 0.62;
      const points = [
        new THREE.Vector3(Math.cos(startAngle) * inner, Math.sin(startAngle) * inner, 0.02),
        new THREE.Vector3(Math.cos(midAngle) * r1, Math.sin(midAngle) * r1, 0.02),
        new THREE.Vector3(Math.cos(endAngle) * r2, Math.sin(endAngle) * r2, -0.01),
        new THREE.Vector3(Math.cos(endAngle + 0.3) * outer, Math.sin(endAngle + 0.3) * outer, 0.02),
      ];
      const curve = new THREE.CatmullRomCurve3(points);
      curves.push({
        tube: new THREE.TubeGeometry(curve, 22, 0.013, 6, false),
        mat: new THREE.MeshBasicMaterial({
          color: new THREE.Color('#a84044'),
          transparent: true,
          opacity: 0.85,
          depthWrite: false,
        }),
      });
    }
    return curves;
  }, [radius]);
}

const scleraGeometry = new THREE.SphereGeometry(1.0, 48, 48);
const choroidGeometry = new THREE.SphereGeometry(0.9, 48, 48);
const retinaGeometry = new THREE.SphereGeometry(0.86, 48, 48, Math.PI - 1.15, 2.3, Math.PI / 2 - 0.72, 1.44);
const vitreousGeometry = new THREE.SphereGeometry(0.94, 32, 32);
const corneaGeometry = new THREE.SphereGeometry(1.045, 48, 48, -0.6, 1.2, Math.PI / 2 - 0.62, 1.24);
const lensGeometry = new THREE.SphereGeometry(0.34, 32, 32);
const pupilGeometry = new THREE.CircleGeometry(0.175, 32);
const maculaGeometry = new THREE.CircleGeometry(0.13, 32);
const opticDiscGeometry = new THREE.CircleGeometry(0.115, 32);

function OpticNerveGeometry() {
  const geometry = useMemo(() => {
    const curve = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, -0.05, -0.82),
      new THREE.Vector3(0, -0.08, -1.15),
      new THREE.Vector3(0.02, -0.14, -1.75),
      new THREE.Vector3(0.05, -0.24, -2.1),
    ]);
    return new THREE.TubeGeometry(curve, 24, 0.14, 10, false);
  }, []);
  return <primitive object={geometry} attach="geometry" />;
}

export type EyeModelProps = {
  selected: EyeStructureId | null;
  hovered: EyeStructureId | null;
  internal: boolean;
  explodeAmount: number;
  reducedMotion: boolean;
  interactingRef: React.MutableRefObject<boolean>;
  onSelect: (id: EyeStructureId | null) => void;
  onHover: (id: EyeStructureId | null) => void;
};

export function EyeModel({
  selected,
  hovered,
  internal,
  explodeAmount,
  reducedMotion,
  interactingRef,
  onSelect,
  onHover,
}: EyeModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const irisTexture = useMemo(() => createIrisTexture(), []);
  const vessels = useRetinalVesselCurves();

  useFrame((state) => {
    const group = groupRef.current;
    if (!group) return;
    if (reducedMotion || interactingRef.current) {
      group.rotation.x += (0 - group.rotation.x) * 0.05;
      group.rotation.y += (0 - group.rotation.y) * 0.05;
      return;
    }
    const t = state.clock.elapsedTime;
    group.rotation.y = Math.sin(t * 0.15) * 0.12;
    group.rotation.x = Math.sin(t * 0.1) * 0.06;
  });

  const handleSelect = (id: EyeStructureId) => onSelect(id);

  return (
    <group ref={groupRef}>
      {EYE_STRUCTURES.map((config) => {
        const nodeProps = {
          config,
          explodeAmount,
          internal,
          selected: selected === config.id,
          hovered: hovered === config.id,
          isolated: selected !== null,
          onSelect: handleSelect,
          onHover,
        };
        switch (config.id) {
          case 'sclera':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={scleraGeometry}>
                  <meshPhysicalMaterial
                    color="#f3f5f7"
                    roughness={0.34}
                    metalness={0}
                    clearcoat={0.6}
                    clearcoatRoughness={0.4}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'choroid':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={choroidGeometry}>
                  <meshStandardMaterial
                    color="#5a2435"
                    roughness={0.7}
                    metalness={0}
                    side={THREE.DoubleSide}
                    opacity={0.9}
                    transparent
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'retina':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={retinaGeometry}>
                  <meshStandardMaterial
                    color="#a44a52"
                    roughness={0.55}
                    metalness={0}
                    side={THREE.DoubleSide}
                    opacity={0.94}
                    transparent
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'macula':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={maculaGeometry} position={[0.18, 0.02, -0.78]} rotation={[0, Math.PI, 0]}>
                  <meshStandardMaterial
                    color="#d9a86a"
                    roughness={0.4}
                    metalness={0}
                    side={THREE.DoubleSide}
                    transparent
                    opacity={0.9}
                    depthWrite={false}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'opticDisc':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={opticDiscGeometry} position={[0, 0, -0.8]} rotation={[0, Math.PI, 0]}>
                  <meshStandardMaterial
                    color="#e6c49a"
                    roughness={0.45}
                    metalness={0}
                    side={THREE.DoubleSide}
                    transparent
                    opacity={0.95}
                    depthWrite={false}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'opticNerve':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh>
                  <OpticNerveGeometry />
                  <meshStandardMaterial
                    color="#f0d3a4"
                    roughness={0.5}
                    metalness={0}
                    transparent
                    opacity={0.92}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'vessels':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                {vessels.map((v, i) => (
                  <primitive key={i} object={v.tube} material={v.mat} position={[0, 0, -0.8]} />
                ))}
              </AnatomyNode>
            );
          case 'vitreous':
            return (
              <AnatomyNode key={config.id} {...nodeProps} forceOpacity={0.06}>
                <mesh geometry={vitreousGeometry}>
                  <meshPhysicalMaterial
                    color="#eaf4fa"
                    roughness={0.1}
                    metalness={0}
                    transparent
                    opacity={0.06}
                    depthWrite={false}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'lens':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={lensGeometry} scale={[0.82, 1, 0.6]}>
                  <meshPhysicalMaterial
                    color="#d9cf9d"
                    roughness={0.08}
                    metalness={0}
                    transparent
                    opacity={0.24}
                    ior={1.41}
                    depthWrite={false}
                  />
                </mesh>
              </AnatomyNode>
            );
          case 'iris':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh position={[0, 0, 0.66]}>
                  <ringGeometry args={[0.2, 0.58, 48]} />
                  <meshStandardMaterial map={irisTexture} roughness={0.45} side={THREE.DoubleSide} transparent />
                </mesh>
              </AnatomyNode>
            );
          case 'pupil':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={pupilGeometry} position={[0, 0, 0.72]}>
                  <meshBasicMaterial color="#07090b" />
                </mesh>
              </AnatomyNode>
            );
          case 'cornea':
            return (
              <AnatomyNode key={config.id} {...nodeProps}>
                <mesh geometry={corneaGeometry}>
                  <meshPhysicalMaterial
                    color="#ffffff"
                    roughness={0.05}
                    metalness={0}
                    clearcoat={1}
                    clearcoatRoughness={0.05}
                    transparent
                    opacity={0.22}
                    ior={1.376}
                    depthWrite={false}
                  />
                </mesh>
              </AnatomyNode>
            );
          default:
            return null;
        }
      })}
    </group>
  );
}