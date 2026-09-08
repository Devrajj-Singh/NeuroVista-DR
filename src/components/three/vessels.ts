import { useMemo } from 'react';
import * as THREE from 'three';

/**
 * Generates a lightweight set of decorative vessel-like curves on a flat
 * disc. These are visual placeholders only — they are NOT detected vessels.
 */
export function useRetinalVessels(count = 7, radius = 1.6, baseZ = 0.01) {
  return useMemo(() => {
    const curves: { points: THREE.Vector3[]; tube: THREE.TubeGeometry; mat: THREE.MeshBasicMaterial }[] = [];
    for (let i = 0; i < count; i++) {
      const startAngle = (i / count) * Math.PI * 2 + (i % 3) * 0.4;
      const midAngle = startAngle + (0.4 + (i % 4) * 0.12);
      const endAngle = midAngle + (0.25 + (i % 2) * 0.15);
      const inner = radius * 0.18;
      const outer = radius * (0.6 + (i % 3) * 0.14);
      const r1 = inner + (radius - inner) * 0.25;
      const r2 = inner + (radius - inner) * 0.6;

      const points = [
        new THREE.Vector3(Math.cos(startAngle) * inner, Math.sin(startAngle) * inner, baseZ),
        new THREE.Vector3(Math.cos(midAngle) * r1, Math.sin(midAngle) * r1, baseZ),
        new THREE.Vector3(Math.cos(endAngle) * r2, Math.sin(endAngle) * r2, baseZ + 0.02),
        new THREE.Vector3(Math.cos(endAngle + 0.3) * outer, Math.sin(endAngle + 0.3) * outer, baseZ),
      ];
      const curve = new THREE.CatmullRomCurve3(points);
      curves.push({
        points,
        tube: new THREE.TubeGeometry(curve, 24, 0.014, 6, false),
        mat: new THREE.MeshBasicMaterial({
          color: new THREE.Color('#14b8a6'),
          transparent: true,
          opacity: 0.55,
          depthWrite: false,
        }),
      });
    }
    return curves;
  }, [count, radius, baseZ]);
}