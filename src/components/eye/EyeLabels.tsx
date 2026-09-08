import { Html } from '@react-three/drei';
import { EYE_STRUCTURES, type EyeStructureId } from '@/data/eyeAnatomy';

export type EyeLabelsProps = {
  showLabels: boolean;
  selected: EyeStructureId | null;
  hovered: EyeStructureId | null;
  labels: Record<EyeStructureId, string>;
};

export function EyeLabels({ showLabels, selected, hovered, labels }: EyeLabelsProps) {
  return (
    <>
      {EYE_STRUCTURES.filter((s) => showLabels || s.id === selected || s.id === hovered).map((structure) => (
        <Html
          key={structure.id}
          position={structure.labelAnchor}
          center
          zIndexRange={[40, 0]}
          style={{ pointerEvents: 'none', transition: 'opacity 0.3s ease' }}
        >
          <span
            className={`eye-label${structure.id === selected ? ' eye-label--active' : ''}${
              structure.id === hovered && !selected ? ' eye-label--hover' : ''
            }`}
          >
            {labels[structure.id]}
          </span>
        </Html>
      ))}
    </>
  );
}
