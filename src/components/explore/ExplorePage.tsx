import { lazy, Suspense } from 'react';
import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';

const EyeAnatomyViewer = lazy(() => import('@/components/eye/EyeAnatomyViewer'));

export function ExplorePage() {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      className="explore-page"
      initial={{ opacity: 0, y: reducedMotion ? 0 : 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: reducedMotion ? 0 : 0.35 }}
    >
      <div className="screen__intro">
        <h1 className="page-title">{t('explore.title')}</h1>
        <p className="screen__desc">{t('explore.subtitle')}</p>
      </div>

      <Suspense
        fallback={
          <div className="eye-viewer__loading" role="status">
            {t('explore.loading')}
          </div>
        }
      >
        <EyeAnatomyViewer />
      </Suspense>
    </motion.div>
  );
}
