import type { CameraPreset } from '@/data/eyeAnatomy';

export const PRESET_CAMERA_POSITION: Record<CameraPreset, [number, number, number]> = {
  front: [0, 0.05, 3.9],
  back: [0, 0.05, -3.9],
  left: [-3.9, 0.05, 0],
  right: [3.9, 0.05, 0],
  top: [0, 3.9, 0],
  bottom: [0, -3.9, 0],
  reset: [2.8, 1.25, 3.8],
};

export const CAMERA_MIN_DISTANCE = 1.5;
export const CAMERA_MAX_DISTANCE = 8.5;

export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}