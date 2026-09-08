export type AppLanguage = 'en' | 'hi';

export type AppState =
  | 'HOME'
  | 'EMPTY_UPLOAD'
  | 'IMAGE_SELECTED'
  | 'PROCESSING'
  | 'QUALITY_GOOD'
  | 'QUALITY_UNGRADABLE'
  | 'RESULT'
  | 'GRADCAM'
  | 'GRADCAM_UNAVAILABLE'
  | 'REPORT'
  | 'EXPLORE'
  | 'HISTORY'
  | 'API_ERROR';

export type ProcessingStage = 0 | 1 | 2;

export type QualityStatus = 'good' | 'ungradable';

export type QualityReason =
  | 'low_focus'
  | 'too_dark'
  | 'poor_field_of_view'
  | 'insufficient_quality'
  | null;

export interface QualityResult {
  status: QualityStatus;
  reason: QualityReason;
}

export interface Prediction {
  icdr_grade: number;
  class_name: string;
  confidence: number;
  referable_dr: boolean;
}

export interface Probabilities {
  [key: string]: number;
}

export interface Explainability {
  gradcam_available: boolean;
}

export interface AnalysisResult {
  status: 'success' | 'ungradable';
  quality: QualityResult;
  prediction?: Prediction;
  probabilities?: Probabilities;
  explainability?: Explainability;
}

export interface ScreeningState {
  appState: AppState;
  selectedImage: File | null;
  imagePreviewUrl: string | null;
  processingStage: ProcessingStage;
  quality: QualityResult | null;
  prediction: Prediction | null;
  probabilities: Probabilities | null;
  explanation: Explainability | null;
  error: string | null;
}

export type ScreeningAction =
  | { type: 'SELECT_IMAGE'; payload: { file: File; previewUrl: string } }
  | { type: 'REMOVE_IMAGE' }
  | { type: 'START_ANALYSIS' }
  | { type: 'SET_PROCESSING_STAGE'; payload: ProcessingStage }
  | { type: 'SET_RESULT'; payload: AnalysisResult }
  | { type: 'GO_TO_RESULT' }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'NAVIGATE'; payload: AppState }
  | { type: 'LOAD_HISTORY'; payload: { prediction: Prediction; probabilities?: Probabilities | null; explanation?: Explainability | null; quality: QualityResult } }
  | { type: 'RESET' }
  | { type: 'GO_HOME' };

export type TranslationKey = string;

export interface TranslationMap {
  [key: string]: string | TranslationMap;
}
