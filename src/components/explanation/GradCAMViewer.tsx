import { useEffect, useRef } from 'react';
import { Card } from '@/components/common/Card';
import { useLocalization } from '@/i18n';

type GradCAMViewerProps = {
  previewUrl: string;
  available: boolean;
};

/**
 * Renders the fundus image with a simulated heatmap overlay applied via a
 * canvas. Replaced by the real Grad-CAM image when the backend provides it.
 */
export function GradCAMViewer({ previewUrl, available }: GradCAMViewerProps) {
  const { t } = useLocalization();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const overlay = overlayRef.current;
    const img = imgRef.current;
    if (!available || !overlay) return;

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

    // Do not size the canvas until the underlying image has decoded real
    // dimensions — sizing too early collapses the heatmap into a sliver.
    const hasSize = () => {
      const rect = overlay.getBoundingClientRect();
      return Number.isFinite(rect.width) && rect.width > 24 && Number.isFinite(rect.height) && rect.height > 24;
    };

    const resize = () => {
      const canvas = canvasRef.current;
      if (!canvas || !hasSize()) return;
      const rect = overlay.getBoundingClientRect();
      canvas.width = Math.round(rect.width);
      canvas.height = Math.round(rect.height);
      drawOverlay();
    };

    overlay.style.opacity = '0.7';

    const observer = new ResizeObserver(() => void resize());
    observer.observe(overlay);

    if (img) {
      if (img.complete && img.naturalWidth > 0) {
        resize();
      } else {
        img.addEventListener('load', resize, { once: true });
      }
    } else {
      resize();
    }

    return () => {
      observer.disconnect();
      if (img) img.removeEventListener('load', resize);
    };
  }, [available]);

  return (
    <Card padded={false}>
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
    </Card>
  );
}