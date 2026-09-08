import { analyzeFundusImage } from '@/services/api';
import { saveHistoryEntry } from '@/services/history';
import type {
  AnalysisResult,
  AppState,
  Explainability,
  Prediction,
  Probabilities,
  ProcessingStage,
  ScreeningAction,
  ScreeningState,
} from '@/types/screening';
import { useCallback, useEffect, useReducer, useRef } from 'react';

const STAGE_DELAYS: Record<ProcessingStage, number> = {
  0: 1500,
  1: 2200,
  2: 1200,
};

const HISTORY_PREVIEW_MAX_BYTES = 1_000_000;

function fileToDataUrl(file: File, maxBytes: number): Promise<string | null> {
  return new Promise((resolve) => {
    if (file.size > maxBytes) {
      resolve(null);
      return;
    }
    const reader = new FileReader();
    reader.onload = () => resolve(typeof reader.result === 'string' ? reader.result : null);
    reader.onerror = () => resolve(null);
    reader.readAsDataURL(file);
  });
}

function createInitialState(): ScreeningState {
  return {
    appState: 'HOME',
    selectedImage: null,
    imagePreviewUrl: null,
    processingStage: 0,
    quality: null,
    prediction: null,
    probabilities: null,
    explanation: null,
    error: null,
  };
}

function reducer(state: ScreeningState, action: ScreeningAction): ScreeningState {
  switch (action.type) {
    case 'SELECT_IMAGE':
      return {
        ...state,
        selectedImage: action.payload.file,
        imagePreviewUrl: action.payload.previewUrl,
        appState: 'IMAGE_SELECTED',
        quality: null,
        prediction: null,
        probabilities: null,
        explanation: null,
        error: null,
      };
    case 'REMOVE_IMAGE':
      return {
        ...state,
        selectedImage: null,
        imagePreviewUrl: null,
        appState: 'EMPTY_UPLOAD',
      };
    case 'START_ANALYSIS':
      return {
        ...state,
        appState: 'PROCESSING',
        processingStage: 0,
        quality: null,
        prediction: null,
        probabilities: null,
        explanation: null,
        error: null,
      };
    case 'SET_PROCESSING_STAGE':
      return { ...state, processingStage: action.payload };
    case 'GO_TO_RESULT':
      return { ...state, appState: 'RESULT' };
    case 'SET_RESULT': {
      const result = action.payload;
      if (result.status === 'ungradable') {
        return {
          ...state,
          quality: result.quality,
          appState: 'QUALITY_UNGRADABLE',
        };
      }
      const nextState: AppState =
        result.quality.status === 'good' ? 'QUALITY_GOOD' : 'QUALITY_UNGRADABLE';
      return {
        ...state,
        quality: result.quality,
        prediction: result.prediction ?? null,
        probabilities: result.probabilities ?? null,
        explanation: result.explainability ?? null,
        appState: nextState,
      };
    }
    case 'SET_ERROR':
      return { ...state, error: action.payload, appState: 'API_ERROR' };
    case 'NAVIGATE':
      return { ...state, appState: action.payload };
    case 'LOAD_HISTORY':
      return {
        ...state,
        prediction: action.payload.prediction,
        probabilities: action.payload.probabilities ?? null,
        explanation: action.payload.explanation ?? null,
        quality: action.payload.quality,
        appState: 'RESULT',
      };
    case 'RESET':
      return {
        ...createInitialState(),
        appState: 'EMPTY_UPLOAD',
      };
    case 'GO_HOME':
      return createInitialState();
    default:
      return state;
  }
}

export function useScreening() {
  const [state, dispatch] = useReducer(reducer, undefined, createInitialState);
  const savedIdRef = useRef<Set<string>>(new Set());

  const selectImage = useCallback((file: File, previewUrl: string) => {
    dispatch({ type: 'SELECT_IMAGE', payload: { file, previewUrl } });
  }, []);

  const removeImage = useCallback(() => {
    dispatch({ type: 'REMOVE_IMAGE' });
  }, []);

  const startAnalysis = useCallback(() => dispatch({ type: 'START_ANALYSIS' }), []);

  const navigate = useCallback((to: AppState) => dispatch({ type: 'NAVIGATE', payload: to }), []);

  const reset = useCallback(() => dispatch({ type: 'RESET' }), []);

  const goHome = useCallback(() => dispatch({ type: 'GO_HOME' }), []);

  const loadFromHistory = useCallback(
    (entry: {
      prediction?: Prediction;
      probabilities?: Probabilities | null;
      explanation?: Explainability | null;
    }) => {
      if (entry.prediction) {
        dispatch({
          type: 'LOAD_HISTORY',
          payload: {
            prediction: entry.prediction,
            probabilities: entry.probabilities ?? null,
            explanation: entry.explanation ?? null,
            quality: { status: 'good', reason: null },
          },
        });
      } else {
        navigate('HISTORY');
      }
    },
    [navigate],
  );

  useEffect(() => {
    if (state.appState !== 'PROCESSING' || !state.selectedImage) return;

    let cancelled = false;
    const file = state.selectedImage;

    async function run() {
      try {
        await delay(STAGE_DELAYS[0]);
        if (cancelled) return;
        dispatch({ type: 'SET_PROCESSING_STAGE', payload: 1 });

        await delay(STAGE_DELAYS[1]);
        if (cancelled) return;
        dispatch({ type: 'SET_PROCESSING_STAGE', payload: 2 });

        await delay(STAGE_DELAYS[2]);
        if (cancelled) return;

        const result: AnalysisResult = await analyzeFundusImage(file);
        if (cancelled) return;

        if (result.status === 'success' && result.prediction) {
          const key = `${file.name}-${result.prediction.icdr_grade}`;
          if (!savedIdRef.current.has(key)) {
            savedIdRef.current.add(key);
            const storedPreview = await fileToDataUrl(file, HISTORY_PREVIEW_MAX_BYTES);
            if (cancelled) return;
            saveHistoryEntry({
              filename: file.name,
              grade: result.prediction.icdr_grade,
              confidence: result.prediction.confidence,
              referable: result.prediction.referable_dr,
              previewUrl: storedPreview,
            });
          }
        }

        dispatch({ type: 'SET_RESULT', payload: result });
      } catch {
        if (cancelled) return;
        dispatch({ type: 'SET_ERROR', payload: 'error.networkError' });
      }
    }

    void run();

    return () => {
      cancelled = true;
    };
  }, [state.appState, state.selectedImage]);

  return {
    state,
    selectImage,
    removeImage,
    startAnalysis,
    navigate,
    reset,
    goHome,
    loadFromHistory,
  };
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}