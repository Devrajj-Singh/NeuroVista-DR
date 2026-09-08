import { Suspense, type ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';
import { Header } from './Header';
import { Footer } from './Footer';
import { CursorGlow } from './CursorGlow';
import { BackgroundFX } from '@/components/three/BackgroundFX';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { useTheme } from '@/theme/ThemeProvider';

type AppShellProps = {
  children: ReactNode;
};

function useWebGLSupport(): boolean {
  if (typeof window === 'undefined') return false;
  const canvas = document.createElement('canvas');
  const gl =
    canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  return Boolean(gl);
}

export function AppShell({ children }: AppShellProps) {
  const reducedMotion = useReducedMotion();
  const supported = useWebGLSupport();
  const { theme } = useTheme();

  return (
    <div className="app-shell">
      {supported && (
        <div className={`app-background app-background--${theme}`} aria-hidden="true">
          <Canvas
            camera={{ position: [0, 0, 12], fov: 60 }}
            dpr={[1, 1.5]}
            gl={{ antialias: true, alpha: true, powerPreference: 'default' }}
          >
            <Suspense fallback={null}>
              <BackgroundFX reducedMotion={reducedMotion} theme={theme} />
            </Suspense>
          </Canvas>
        </div>
      )}
      <CursorGlow />
      <Header />
      <main className="app-shell__main">{children}</main>
      <Footer />
    </div>
  );
}