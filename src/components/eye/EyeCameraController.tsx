import { useRef, type MutableRefObject } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { EYE_STRUCTURES, type CameraPreset, type EyeStructureId } from '@/data/eyeAnatomy';
import { CAMERA_MAX_DISTANCE, CAMERA_MIN_DISTANCE, PRESET_CAMERA_POSITION } from '@/utils/eyeModelUtils';

export type CameraRequest =
  | { kind: 'preset'; preset: CameraPreset }
  | { kind: 'zoom'; direction: 1 | -1 }
  | { kind: 'focus'; id: EyeStructureId; deep?: boolean };

export type EyeCameraControllerProps = {
  controlsRef: MutableRefObject<OrbitControlsImpl | null>;
  requestRef: MutableRefObject<CameraRequest | null>;
  interactingRef: MutableRefObject<boolean>;
  reducedMotion: boolean;
};

type Flight = {
  from: THREE.Vector3;
  targetFrom: THREE.Vector3;
  pos: THREE.Vector3;
  target: THREE.Vector3;
  elapsed: number;
};

const FLIGHT_DURATION = 1.25;

export function EyeCameraController({
  controlsRef,
  requestRef,
  interactingRef,
  reducedMotion,
}: EyeCameraControllerProps) {
  const camera = useThree((s) => s.camera);
  const flight = useRef<Flight | null>(null);

  useFrame((_, delta) => {
    const controls = controlsRef.current;
    if (!controls) return;

    if (import.meta.env.DEV) {
      (window as unknown as Record<string, unknown>).__eyeViewerCamera = camera.position.toArray();
      (window as unknown as Record<string, unknown>).__eyeViewerCtrl = {
        interacting: interactingRef.current,
        flightActive: Boolean(flight.current),
        pending: Boolean(requestRef.current),
      };
    }

    const request = requestRef.current;
    if (request) {
      requestRef.current = null;
      if (import.meta.env.DEV) {
        (window as unknown as Record<string, unknown>).__eyeViewerLastRequest =
          request.kind === 'focus' ? `focus:${request.id}` : request.kind;
      }
      const targetPos = controls.target;
      const toPos = new THREE.Vector3();
      if (request.kind === 'preset') {
        const [x, y, z] = PRESET_CAMERA_POSITION[request.preset];
        toPos.set(x, y, z);
        controls.target.set(0, 0, 0);
      } else if (request.kind === 'zoom') {
        const direction = camera.position.clone().sub(targetPos);
        const distance = Math.min(Math.max(direction.length() * (request.direction > 0 ? 0.72 : 1.38), CAMERA_MIN_DISTANCE), CAMERA_MAX_DISTANCE);
        toPos.copy(targetPos).add(direction.normalize().multiplyScalar(distance));
        controls.target.set(0, 0, 0);
      } else {
        const structure = EYE_STRUCTURES.find((s) => s.id === request.id) ?? EYE_STRUCTURES[0];
        const anchor = new THREE.Vector3(...structure.base);
        const outward =
          anchor.lengthSq() < 1e-6 ? new THREE.Vector3(0, 0.1, 1) : anchor.clone().normalize();
        toPos.copy(anchor).add(outward.multiplyScalar(Math.max(structure.focusDistance * (request.deep ? 0.62 : 0.85), 1.2)));
        controls.target.set(...structure.base);
      }
      controls.enableDamping = false;
      flight.current = {
        from: camera.position.clone(),
        targetFrom: controls.target.clone(),
        pos: toPos,
        target: controls.target.clone(),
        elapsed: 0,
      };
    }

    if (interactingRef.current) {
      flight.current = null;
    }

    if (flight.current) {
      flight.current.elapsed += delta;
      const duration = reducedMotion ? 0.3 : FLIGHT_DURATION;
      const progress = Math.min(flight.current.elapsed / duration, 1);
      const eased = reducedMotion ? progress : 1 - Math.pow(1 - progress, 3);
      camera.position.lerpVectors(flight.current.from, flight.current.pos, eased);
      controls.target.lerpVectors(flight.current.targetFrom, flight.current.target, eased);
      if (flight.current.elapsed >= duration) {
        camera.position.copy(flight.current.pos);
        controls.target.copy(flight.current.target);
        flight.current = null;
        controls.enableDamping = true;
      }
    }

    controls.update();
  });

  return null;
}