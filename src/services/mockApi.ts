import type { AnalysisResult, QualityReason } from '@/types/screening';

export type MockScenario =
  | 'success'
  | 'non-referable'
  | 'ungradable-blurry'
  | 'ungradable-dark'
  | 'ungradable-field'
  | 'ungradable-insufficient'
  | 'no-gradcam'
  | 'error';

type UngradableScenario =
  | 'ungradable-blurry'
  | 'ungradable-dark'
  | 'ungradable-field'
  | 'ungradable-insufficient';

let currentScenario: MockScenario = 'success';

export function __setMockScenario(scenario: MockScenario): void {
  currentScenario = scenario;
}

function successResponse(noGradcam = false, referable = true): AnalysisResult {
  return {
    status: 'success',
    quality: { status: 'good', reason: null },
    prediction: referable
      ? {
          icdr_grade: 2,
          class_name: 'Moderate NPDR',
          confidence: 0.87,
          referable_dr: true,
        }
      : {
          icdr_grade: 1,
          class_name: 'Mild NPDR',
          confidence: 0.78,
          referable_dr: false,
        },
    probabilities: referable
      ? { '0': 0.02, '1': 0.05, '2': 0.87, '3': 0.04, '4': 0.02 }
      : { '0': 0.08, '1': 0.78, '2': 0.09, '3': 0.03, '4': 0.02 },
    explainability: { gradcam_available: !noGradcam },
  };
}

const UNGRADABLE_REASONS: Record<UngradableScenario, QualityReason> = {
  'ungradable-blurry': 'low_focus',
  'ungradable-dark': 'too_dark',
  'ungradable-field': 'poor_field_of_view',
  'ungradable-insufficient': 'insufficient_quality',
};

function ungradableResponse(reason: QualityReason): AnalysisResult {
  return {
    status: 'ungradable',
    quality: { status: 'ungradable', reason },
  };
}

const RESPONSE_DELAY = 800;

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => globalThis.setTimeout(resolve, ms));
}

/**
 * Simulates the backend analysis pipeline.
 *
 * When the real Python backend is available, this module is replaced by the
 * implementation in `services/api.ts` and the UI is unaffected.
 */
export async function mockAnalyzeFundusImage(_image: File): Promise<AnalysisResult> {
  const scenario = currentScenario;

  await delay(RESPONSE_DELAY);

  switch (scenario) {
    case 'success':
      return successResponse();
    case 'non-referable':
      return successResponse(false, false);
    case 'no-gradcam':
      return successResponse(true);
    case 'ungradable-blurry':
    case 'ungradable-dark':
    case 'ungradable-field':
    case 'ungradable-insufficient':
      return ungradableResponse(UNGRADABLE_REASONS[scenario]);
    case 'error':
      throw new Error('Mock API: simulated network failure');
  }
}