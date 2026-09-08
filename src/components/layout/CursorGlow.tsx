import { useEffect, useRef } from 'react';

/**
 * Soft glowing spotlight that follows the pointer for a high-end feel.
 * Decorative only; disabled when reduced-motion is preferred or on coarse pointers.
 */
export function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (window.matchMedia('(pointer: coarse)').matches) return;

    const el: HTMLDivElement = node;

    let raf = 0;
    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;

    function onMove(e: PointerEvent) {
      el.dataset.tx = String(e.clientX);
      el.dataset.ty = String(e.clientY);
    }

    function loop() {
      const dx = Number(el.dataset.tx ?? x) - x;
      const dy = Number(el.dataset.ty ?? y) - y;
      x += dx * 0.08;
      y += dy * 0.08;
      el.style.transform = `translate(${x - 300}px, ${y - 300}px)`;
      raf = requestAnimationFrame(loop);
    }

    window.addEventListener('pointermove', onMove, { passive: true });
    raf = requestAnimationFrame(loop);
    return () => {
      window.removeEventListener('pointermove', onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return <div className="cursor-glow" ref={ref} aria-hidden="true" />;
}
