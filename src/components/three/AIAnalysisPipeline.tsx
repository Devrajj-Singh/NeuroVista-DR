import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { ProcessingStage } from '@/types/screening';

type AIAnalysisPipelineProps = {
  processingStage: ProcessingStage;
  reducedMotion?: boolean;
};

type NodeState = 'done' | 'active' | 'pending';

const NODE_POSITIONS: [number, number, number][] = [
  [-1.9, 0, 0], // Fundus image
  [-0.65, 0, 0], // Quality check
  [0.65, 0, 0], // Retinal analysis
  [1.9, 0, 0], // Result
];

const DONE_COLOR = '#16a34a';
const ACTIVE_COLOR = '#4fd1c5';
const PENDING_COLOR = '#94a3b8';

/**
 * Shows the conceptual pipeline: fundus → quality → analysis → result.
 * A visual metaphor, not the real neural architecture.
 */
export function AIAnalysisPipeline({ processingStage, reducedMotion = false }: AIAnalysisPipelineProps) {
  const nodeRefs = useRef<(THREE.Group | null)[]>([]);
  const particleRefs = useRef<(THREE.Mesh | null)[]>([]);

  const pipelineNodes: NodeState[] = useMemo(
    () => NODE_POSITIONS.map((_, i) => (i < processingStage ? 'done' : i === processingStage ? 'active' : 'pending')),
    [processingStage],
  );

  const { lines } = useMemo(() => {
    const segments = NODE_POSITIONS.slice(0, -1).map((from, i) => {
      const to = NODE_POSITIONS[i + 1];
      const curve = new THREE.CatmullRomCurve3(
        [new THREE.Vector3(...from), new THREE.Vector3((from[0] + to[0]) / 2, 0.25, 0), new THREE.Vector3(...to)],
      );
      const mat = new THREE.LineBasicMaterial({
        color: '#4fd1c5',
        transparent: true,
        opacity: 0.35,
      });
      const geom = new THREE.BufferGeometry().setFromPoints(curve.getPoints(24));
      const line = new THREE.Line(geom, mat);
      return { line, curve };
    });
    return { lines: segments };
  }, []);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    nodeRefs.current.forEach((group, i) => {
      if (!group) return;
      const state = pipelineNodes[i];
      const target = state === 'active' ? 1.5 : state === 'done' ? 1.1 : 0.85;
      if (!reducedMotion) {
        group.scale.lerp(new THREE.Vector3(target, target, target), 0.08);
        group.position.y = state === 'active' ? Math.sin(t * 2) * 0.1 : 0;
      } else {
        group.scale.set(target, target, target);
      }
    });
    particleRefs.current.forEach((mesh, i) => {
      if (!mesh || reducedMotion) return;
      const curve = lines[i]?.curve;
      if (!curve) return;
      const progress = ((t * 0.35) + i * 0.25) % 1;
      const point = curve.getPoint(progress);
      mesh.position.set(point.x, point.y + 0.02, point.z);
    });
  });

  return (
    <group>
      <ambientLight intensity={0.6} />
      <directionalLight position={[2, 4, 4]} intensity={1} />

      {lines.map((line, i) => (
        <primitive key={`line${i}`} object={line.line} />
      ))}

      {lines.map((_, i) => (
        <mesh
          key={`p${i}`}
          ref={(el) => {
            particleRefs.current[i] = el;
          }}
        >
          <sphereGeometry args={[0.045, 8, 8]} />
          <meshBasicMaterial color={ACTIVE_COLOR} transparent opacity={0.9} />
        </mesh>
      ))}

      {NODE_POSITIONS.map((pos, i) => {
        const state = pipelineNodes[i];
        return (
          <group
            key={i}
            ref={(el) => {
              nodeRefs.current[i] = el;
            }}
            position={pos}
          >
            <mesh>
              <sphereGeometry args={[0.16, 16, 16]} />
              <meshStandardMaterial
                color={state === 'done' ? DONE_COLOR : state === 'active' ? ACTIVE_COLOR : PENDING_COLOR}
                roughness={0.4}
                emissive={
                  state === 'active' ? new THREE.Color(ACTIVE_COLOR) : new THREE.Color('#000000')
                }
                emissiveIntensity={state === 'active' ? 0.35 : 0}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}