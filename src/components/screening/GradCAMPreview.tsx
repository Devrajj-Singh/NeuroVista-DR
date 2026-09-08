import { useEffect, useRef } from 'react';
import { useLocalization } from '@/i18n';

type GradCAMPreviewProps = {
  previewUrl: string;
  available: boolean;
};

export function GradCAMPreview({ previewUrl, available }: GradCAMPreviewProps) {
  const { t } = useLocalization();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const overlay = overlayRef.current;
    const img = imgRef.current;
    if (!available || !overlay || !img) return;

    const drawOverlay = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const width = canvas.width;
      const height = canvas.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);

      const hotSpots = [
        { x: 0.32, y: 0.4, r: 0.22, color: 'rgba(239, 68, 68, 0.85)' },
        { x: 0.62, y: 0.3, r: 0.16, color: 'rgba(239, 68, 68, 0.8)' },
        { x: 0.5, y: 0.66, r: 0.18, color: 'rgba(245, 158, 11, 0.75)' },
        { x: 0.75, y: 0.55, r: 0.12, color: 'rgba(245, 158, 11, 0.7)' },
        { x: 0.2, y: 0.62, r: 0.13, color: 'rgba(249, 115, 22, 0.6)' },
      ];

      hotSpots.forEach((spot) => {
        const cx = spot.x * width;
        const cy = spot.y * height;
        const radius = spot.r * width;
        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
        gradient.addColorStop(0, spot.color);
        gradient.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
      });
    };

    const resize = () => {
      const rect = overlay.getBoundingClientRect();
      const canvas = canvasRef.current;
      if (!canvas) return;
      canvas.width = rect.width;
      canvas.height = rect.height;
      drawOverlay();
    };

    overlay.style.opacity = '0.7';
    const observer = new ResizeObserver(resize);
    observer.observe(overlay);
    resize();
    return () => observer.disconnect();
  }, [available]);

  return (
    <div className="gradcam-preview">
      <div className="fundus-viewer">
        {previewUrl ? (
          <img
            ref={imgRef}
            src={previewUrl}
            alt={t('gradcam.modelExplanation')}
            className="fundus-viewer__img"
          />
        ) : (
          <div className="fundus-viewer__placeholder">{t('history.noPreview')}</div>
        )}
        {available && (
          <div className="gradcam-overlay" ref={overlayRef}>
            <canvas ref={canvasRef} className="gradcam-overlay__canvas" />
          </div>
        )}
      </div>
    </div>
  );
}
