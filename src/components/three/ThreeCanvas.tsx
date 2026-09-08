import { Component, Suspense, type ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';

type ThreeCanvasProps = {
  children: ReactNode;
  camera?: { position: [number, number, number]; fov?: number };
  fallbackMessage?: string;
  className?: string;
};

function isWebGLSupported(): boolean {
  if (typeof window === 'undefined') return false;
  const canvas = document.createElement('canvas');
  const gl =
    canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  return Boolean(gl);
}

class WebGLBoundary extends Component<
  { children: ReactNode; fallback: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  render() {
    return this.state.failed ? this.props.fallback : this.props.children;
  }
}

function Fallback({ message }: { message: string }) {
  return (
    <div className="three-fallback" role="status">
      {message}
    </div>
  );
}

export function ThreeCanvas({
  children,
  camera = { position: [0, 0, 4], fov: 50 },
  fallbackMessage = 'Visualization unavailable',
  className = '',
}: ThreeCanvasProps) {
  const fallback = <Fallback message={fallbackMessage} />;
  const supported = isWebGLSupported();
  const filtered = [className, supported ? '' : 'three-canvas--static']
    .filter(Boolean)
    .join(' ');

  return (
    <div className={`three-canvas ${filtered}`.trim()}>
      {supported ? (
        <WebGLBoundary fallback={fallback}>
          <Suspense fallback={fallback}>
            <Canvas
              dpr={[1, 1.5]}
              gl={{ antialias: true, alpha: true, powerPreference: 'default' }}
              camera={camera}
            >
              {children}
            </Canvas>
          </Suspense>
        </WebGLBoundary>
      ) : (
        fallback
      )}
    </div>
  );
}