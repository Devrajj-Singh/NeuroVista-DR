import { useMemo } from 'react';
import { EYE_STRUCTURES, type EyeStructure } from '@/data/eyeAnatomy';

/**
 * Model structure availability for the procedural anatomical eye.
 * All structures are present in the built-in model. When a licensed
 * GLB is installed (see public/models/anatomical-eye.glb), this hook
 * is the mapping point for the actual scene-graph node names.
 */
export function useEyeModel(): { structures: EyeStructure[]; structureMap: Record<string, EyeStructure> } {
  return useMemo(() => {
    const structureMap: Record<string, EyeStructure> = {};
    for (const s of EYE_STRUCTURES) structureMap[s.id] = s;
    return { structures: EYE_STRUCTURES, structureMap };
  }, []);
}