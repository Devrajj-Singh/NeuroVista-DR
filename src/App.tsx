import { useCallback, useEffect, useMemo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useScreening } from '@/hooks/useScreening';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { useLocalization } from '@/i18n';
import { NavContext } from '@/navigation/NavContext';
import { AppShell } from '@/components/layout/AppShell';
import { ErrorBoundary } from '@/components/common/ErrorBoundary';
import { HeroPage } from '@/components/home/HeroPage';
import { ImageUploader } from '@/components/upload/ImageUploader';
import { ImagePreview } from '@/components/upload/ImagePreview';
import { ProcessingScreen } from '@/components/screening/ProcessingScreen';
import { QualityResult } from '@/components/screening/QualityResult';
import { DRResult } from '@/components/screening/DRResult';
import { ExplanationScreen } from '@/components/explanation/ExplanationScreen';
import { ScreeningReport } from '@/components/report/ScreeningReport';
import { ExplorePage } from '@/components/explore/ExplorePage';
import { HistoryPage } from '@/components/history/HistoryPage';
import { StatusMessage } from '@/components/common/StatusMessage';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { IconCheck, IconError, IconRefresh } from '@/components/common/Icons';
import { ThreeCanvas } from '@/components/three/ThreeCanvas';
import { RetinalHero } from '@/components/three/RetinalHero';

function UploadHero() {
  return (
    <div className="upload-hero" aria-hidden="true">
      <ThreeCanvas camera={{ position: [0, 0.1, 3.6], fov: 45 }} fallbackMessage="">
        <RetinalHero interactive />
      </ThreeCanvas>
    </div>
  );
}

export function ScreeningDashboard() {
  const { state, selectImage, removeImage, startAnalysis, navigate, reset, goHome, loadFromHistory } =
    useScreening();
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    return () => {
      if (state.imagePreviewUrl) URL.revokeObjectURL(state.imagePreviewUrl);
    };
  }, [state.imagePreviewUrl]);

  useEffect(() => {
    if (state.appState !== 'QUALITY_GOOD') return;
    const timer = window.setTimeout(() => navigate('RESULT'), 1400);
    return () => window.clearTimeout(timer);
  }, [state.appState, navigate]);

  const handleSelectImage = useCallback(
    (file: File) => {
      if (state.imagePreviewUrl) URL.revokeObjectURL(state.imagePreviewUrl);
      const url = URL.createObjectURL(file);
      selectImage(file, url);
    },
    [state.imagePreviewUrl, selectImage],
  );

  const handleReset = useCallback(() => {
    if (state.imagePreviewUrl) URL.revokeObjectURL(state.imagePreviewUrl);
    reset();
  }, [state.imagePreviewUrl, reset]);

  const screen = useMemo(() => {
    switch (state.appState) {
      case 'HOME':
        return <HeroPage onStartScreening={() => navigate('EMPTY_UPLOAD')} />;

      case 'EMPTY_UPLOAD':
        return (
          <div className="screen">
            <UploadHero />
            <div className="screen__intro">
              <h1 className="page-title">{t('upload.title')}</h1>
              <p className="screen__desc">{t('upload.description')}</p>
              <p className="screen__tagline">{t('brand.tagline')}</p>
            </div>
            <ImageUploader onSelect={handleSelectImage} />
          </div>
        );

      case 'IMAGE_SELECTED':
        if (!state.selectedImage || !state.imagePreviewUrl) {
          navigate('EMPTY_UPLOAD');
          return null;
        }
        return (
          <div className="screen">
            <div className="screen__intro">
              <h1 className="page-title">{t('preview.title')}</h1>
              <p className="screen__desc">{t('preview.description')}</p>
            </div>
            <ImagePreview
              previewUrl={state.imagePreviewUrl}
              filename={state.selectedImage.name}
              fileSize={state.selectedImage.size}
              onChangeImage={removeImage}
              onAnalyze={startAnalysis}
              canAnalyze
            />
          </div>
        );

      case 'PROCESSING':
        return <ProcessingScreen stage={state.processingStage} />;

      case 'QUALITY_GOOD':
        return (
          <div className="screen screen--center">
            <StatusMessage tone="success" icon={<IconCheck />} heading={t('quality.proceeding')}>
              <p>{t('processing.complete')}</p>
            </StatusMessage>
          </div>
        );

      case 'QUALITY_UNGRADABLE':
        return <QualityResult reason={state.quality?.reason ?? null} onRecapture={removeImage} />;

      case 'RESULT':
        if (!state.prediction) {
          navigate('HISTORY');
          return null;
        }
        return (
          <DRResult
            prediction={state.prediction}
            previewUrl={state.imagePreviewUrl ?? ''}
            gradcamAvailable={state.explanation?.gradcam_available === true}
            onHome={goHome}
            onViewExplanation={() =>
              navigate(state.explanation?.gradcam_available ? 'GRADCAM' : 'GRADCAM_UNAVAILABLE')
            }
            onViewReport={() => navigate('REPORT')}
          />
        );

      case 'EXPLORE':
        return <ExplorePage />;

      case 'HISTORY':
        return (
          <HistoryPage
            onSelect={(entry) => {
              const prediction = {
                icdr_grade: entry.grade,
                class_name: '',
                confidence: entry.confidence,
                referable_dr: entry.referable,
              };
              loadFromHistory({
                prediction,
                probabilities: null,
                explanation: { gradcam_available: false },
              });
            }}
          />
        );

      case 'GRADCAM':
      case 'GRADCAM_UNAVAILABLE':
        if (!state.imagePreviewUrl) {
          navigate('EMPTY_UPLOAD');
          return null;
        }
        return (
          <ExplanationScreen
            previewUrl={state.imagePreviewUrl}
            explanation={state.explanation}
            onViewReport={() => navigate('REPORT')}
            onBackToResult={() => navigate('RESULT')}
          />
        );

      case 'REPORT':
        if (!state.prediction || !state.imagePreviewUrl) {
          navigate('EMPTY_UPLOAD');
          return null;
        }
        return (
          <ScreeningReport
            previewUrl={state.imagePreviewUrl}
            quality={state.quality ?? { status: 'good', reason: null }}
            prediction={state.prediction}
            explanation={state.explanation}
            onBackToResult={() => navigate('RESULT')}
            onAnalyzeAnother={handleReset}
          />
        );

      case 'API_ERROR':
        return (
          <div className="screen screen--center">
            <Card>
              <StatusMessage tone="error" icon={<IconError />} heading={t('error.title')}>
                <p>{t('error.description')}</p>
              </StatusMessage>
              <div className="error-actions">
                <Button onClick={startAnalysis} icon={<IconRefresh />}>
                  {t('error.tryAgain')}
                </Button>
                <Button variant="secondary" onClick={removeImage}>
                  {t('error.chooseAnother')}
                </Button>
              </div>
            </Card>
          </div>
        );

      default:
        return null;
    }
  }, [state, t, navigate, handleSelectImage, handleReset, removeImage, startAnalysis, goHome, loadFromHistory]);

  const navValue = useMemo(
    () => ({ navigate, goHome }),
    [navigate, goHome],
  );

  return (
    <NavContext.Provider value={navValue}>
      <AppShell>
        <ErrorBoundary>
          <div className="app-content">
            <AnimatePresence mode="wait">
              <motion.div
                key={state.appState}
                initial={reducedMotion ? { opacity: 0 } : { opacity: 0, y: 22, scale: 0.985, filter: 'blur(8px)' }}
                animate={reducedMotion ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1, filter: 'blur(0px)' }}
                exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -18, scale: 0.99, filter: 'blur(6px)' }}
                transition={{ duration: reducedMotion ? 0 : 0.32, ease: [0.22, 1, 0.36, 1] }}
              >
                {screen}
              </motion.div>
            </AnimatePresence>
          </div>
        </ErrorBoundary>
      </AppShell>
    </NavContext.Provider>
  );
}

export default ScreeningDashboard;