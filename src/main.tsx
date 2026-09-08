import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import { LocalizationProvider } from './i18n';
import { ThemeProvider } from './theme/ThemeProvider';
import { __setMockScenario } from './services/mockApi';
import { __useMockForTesting } from './services/api';
import './index.css';

// Dev/demo-only scenario switcher for the prototype. Never exposed in builds.
// Setting a mock scenario also routes the UI's analysis call to the mock so
// the e2e test suite can exercise deterministic outcomes. When left unset,
// the UI talks to the real FastAPI backend by default.
if (import.meta.env.DEV) {
  (window as unknown as Record<string, unknown>).__neurovista = {
    setMockScenario: (scenario: Parameters<typeof __setMockScenario>[0]) => {
      __useMockForTesting();
      __setMockScenario(scenario);
    },
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
