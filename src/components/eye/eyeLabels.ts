import type { EyeStructureId } from '@/data/eyeAnatomy';
import { EYE_STRUCTURES } from '@/data/eyeAnatomy';

type Translate = (key: string) => string;

export function structureLabels(t: Translate): Record<EyeStructureId, string> {
  const map = {} as Record<EyeStructureId, string>;
  for (const s of EYE_STRUCTURES) {
    map[s.id] = t(`eye.structures.${s.id}`);
  }
  return map;
}
