import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { LocalizationProvider } from './i18n';
import { ThemeProvider } from './theme/ThemeProvider';
import { __setMockScenario } from './services/mockApi';
import './index.css';

// Dev/demo-only scenario switcher for the prototype. Never exposed in builds.
if (import.meta.env.DEV) {
  (window as unknown as Record<string, unknown>).__neurovista = {
    setMockScenario: __setMockScenario,
  };
}

const container = document.getElementById('root');
if (!container) throw new Error('Root element #root not found');

createRoot(container).render(
  <StrictMode>
    <ThemeProvider>
      <LocalizationProvider>
        <App />
      </LocalizationProvider>
    </ThemeProvider>
  </StrictMode>,
);