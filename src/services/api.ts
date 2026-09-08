import type { AnalysisResult } from '@/types/screening';
import { mockAnalyzeFundusImage } from './mockApi';

/**
 * Service-layer adapter.
 *
 * The UI calls `analyzeFundusImage` and never imports `mockApi` directly.
 * To connect the real Python backend, replace the body of this function with
 * a fetch to `POST /api/v1/analyze` using the same return type.
 */
export async function analyzeFundusImage(image: File): Promise<AnalysisResult> {
  return mockAnalyzeFundusImage(image);
}