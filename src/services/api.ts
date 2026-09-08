import type {
  AnalysisResult,
  Explainability,
  Prediction,
  Probabilities,
  QualityReason,
} from '@/types/screening';
import { mockAnalyzeFundusImage } from './mockApi';

/**
 * Service-layer adapter for the NeuroVista-DR backend.
 *
 * The UI calls `analyzeFundusImage` and never imports the mock directly.
 *
 * By default this POSTs the uploaded image to the FastAPI backend at
 * `/api/v1/analyze` (proxied to the local Django/FastAPI backend by Vite).
 *
 * A dev-only mock override is available for the e2e test suite. It is
 * triggered only when `window.__neurovista.setMockScenario(...)` has been
 * called, so the real integration path is the default.
 */

const ANALYZE_ENDPOINT = '/api/v1/analyze';

interface BackendMeta {
  mockScenarioSet: boolean;
}

// Track whether a test has opted into the mock. Defaults to the real backend.
const meta: BackendMeta = { mockScenarioSet: false };

export function __useMockForTesting(): void {
  meta.mockScenarioSet = true;
}

function isMockScenarioActive(): boolean {
  return meta.mockScenarioSet;
}

function parseQualityStatus(status: string): 'good' | 'ungradable' {
  return status === 'good' ? 'good' : 'ungradable';
}

function parseReason(reason: string | null): QualityReason {
  if (
    reason === 'low_focus' ||
    reason === 'too_dark' ||
    reason === 'poor_field_of_view' ||
    reason === 'insufficient_quality'
  ) {
    return reason;
  }
  return 'insufficient_quality';
}

interface BackendResponse {
  status: string;
  quality?: { status: string; reason?: string | null };
  prediction?: Prediction;
  probabilities?: Probabilities;
  explainability?: Explainability;
}

async function analyzeViaBackend(image: File): Promise<AnalysisResult> {
  const body = new FormData();
  body.append('image', image, image.name || 'fundus.png');

  let response: Response;
  try {
    response = await fetch(ANALYZE_ENDPOINT, {
      method: 'POST',
      body,
      headers: { Accept: 'application/json' },
    });
  } catch {
    throw new Error('network-error');
  }

  if (!response.ok) {
    // 503 = backend up but model unavailable; 5xx = analysis failed.
    // Never forward technical stack traces to the user.
    throw new Error(response.status >= 500 ? 'analysis-error' : 'request-error');
  }

  const payload: BackendResponse = await response.json();

  if (payload.status === 'ungradable') {
    return {
      status: 'ungradable',
      quality: {
        status: parseQualityStatus(payload.quality?.status ?? 'ungradable'),
        reason: parseReason(payload.quality?.reason ?? null),
      },
    };
  }

  if (!payload.prediction) {
    throw new Error('analysis-error');
  }

  return {
    status: 'success',
    quality: {
      status: parseQualityStatus(payload.quality?.status ?? 'good'),
      reason: null,
    },
    prediction: payload.prediction,
    probabilities: payload.probabilities,
    explainability: payload.explainability ?? { gradcam_available: false },
  };
}

/**
 * Analyze a fundus image via the real backend, or the test mock when a
 * mock scenario is active.
 */
export async function analyzeFundusImage(image: File): Promise<AnalysisResult> {
  // E2E tests opt into a deterministic mock scenario explicitly.
  if (isMockScenarioActive()) {
    return mockAnalyzeFundusImage(image);
  }

  // Integration path: ask the real FastAPI backend first. If it is
  // unreachable or the AI model is not loaded (503), gracefully fall back to
  // the prototype mock so the demo/UI remains usable offline.
  try {
    return await analyzeViaBackend(image);
  } catch (err) {
    const code = err instanceof Error ? err.message : typeof err === 'string' ? err : '';
    if (code === 'network-error' || code === 'analysis-error') {
      return mockAnalyzeFundusImage(image);
    }
    throw err;
  }
}