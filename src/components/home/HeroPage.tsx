import { motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { useRef } from 'react';
import { ThreeCanvas } from '@/components/three/ThreeCanvas';
import { RetinalHero } from '@/components/three/RetinalHero';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { IconUpload, IconScan, IconEye, IconReport } from '@/components/common/Icons';

type HeroPageProps = {
  onStartScreening: () => void;
};

const WORKFLOW_STEPS = [
  { icon: IconEye, titleKey: 'home.workflow.1.title', descKey: 'home.workflow.1.desc' },
  { icon: IconScan, titleKey: 'home.workflow.2.title', descKey: 'home.workflow.2.desc' },
  { icon: IconUpload, titleKey: 'home.workflow.3.title', descKey: 'home.workflow.3.desc' },
  { icon: IconReport, titleKey: 'home.workflow.4.title', descKey: 'home.workflow.4.desc' },
];

export function HeroPage({ onStartScreening }: HeroPageProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const workflowRef = useRef<HTMLElement | null>(null);

  function scrollToWorkflow() {
    workflowRef.current?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
  }

  const container = {
    hidden: {},
    show: { transition: { staggerChildren: reducedMotion ? 0 : 0.12 } },
  };

  const item = {
    hidden: reducedMotion ? { opacity: 0 } : { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' } },
  };

  return (
    <div className="home">
      <div className="home__hero">
        <motion.div
          className="home__content"
          variants={container}
          initial="hidden"
          animate="show"
          data-testid="home-content"
        >
          <motion.div variants={item}>
            <span className="home__badge">
              <span className="home__badge-dot" aria-hidden="true" />
              {t('home.badge')}
            </span>
          </motion.div>

          <motion.h1 variants={item} className="home__title">
            {t('home.title')}
          </motion.h1>

          <motion.p variants={item} className="home__subtitle">
            {t('home.subtitle')}
          </motion.p>

          <motion.div variants={item} className="home__actions">
            <Button onClick={onStartScreening} icon={<IconUpload />}>
              {t('home.start')}
            </Button>
            <Button variant="secondary" onClick={scrollToWorkflow}>
              {t('home.learn')}
            </Button>
          </motion.div>

          <motion.p variants={item} className="home__secondary-info">
            {t('home.secondaryInfo')}
          </motion.p>
        </motion.div>

        <div className="home__visual" aria-hidden="true">
          <ThreeCanvas camera={{ position: [0, 0.1, 3.6], fov: 45 }} fallbackMessage="">
            <RetinalHero interactive />
          </ThreeCanvas>
        </div>
      </div>

      <motion.section
        ref={workflowRef}
        className="home__section"
        initial={reducedMotion ? undefined : { opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        aria-label={t('home.workflow.title')}
      >
        <h2 className="home__section-title">{t('home.workflow.title')}</h2>
        <div className="workflow">
          {WORKFLOW_STEPS.map((step, index) => {
            const WorkflowIcon = step.icon;
            return (
              <Card
                key={step.titleKey}
                className="workflow-step"
                data-testid={`workflow-step-${index + 1}`}
              >
                <span className="workflow-step__icon">
                  <WorkflowIcon />
                </span>
                <span className="workflow-step__num">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <h3 className="workflow-step__title">{t(step.titleKey)}</h3>
                <p className="workflow-step__desc">{t(step.descKey)}</p>
              </Card>
            );
          })}
        </div>
      </motion.section>
    </div>
  );
}
