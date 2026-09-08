import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useLocalization } from '@/i18n';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { Button } from '@/components/common/Button';
import { Card } from '@/components/common/Card';
import { IconCheck } from '@/components/common/Icons';
import { ThreeCanvas } from '@/components/three/ThreeCanvas';
import { RetinalHero } from '@/components/three/RetinalHero';
import type { AppLanguage } from '@/types/screening';

type LanguageSelectorProps = {
  onContinue: (language: AppLanguage) => void;
};

type LanguageOption = {
  code: AppLanguage;
  label: string;
  secondary: string;
};

const OPTIONS: LanguageOption[] = [
  { code: 'en', label: 'English', secondary: 'English' },
  { code: 'hi', label: 'हिन्दी', secondary: 'Hindi' },
];

export function LanguageSelector({ onContinue }: LanguageSelectorProps) {
  const { t } = useLocalization();
  const reducedMotion = useReducedMotion();
  const [selected, setSelected] = useState<AppLanguage | null>(null);

  function confirm() {
    if (selected) onContinue(selected);
  }

  return (
    <div className="language-screen">
      <div className="language-screen__hero" aria-hidden="true">
        <ThreeCanvas camera={{ position: [0, 0.1, 3.4], fov: 45 }} fallbackMessage="">
          <RetinalHero reducedMotion={reducedMotion} small interactive />
        </ThreeCanvas>
      </div>

      <Card className="language-screen__card">
        <h1 className="page-title">{t('language.title')}</h1>
        <p className="language-screen__subtitle">{t('language.subtitle')}</p>
        <p className="language-screen__choice">{t('language.chooseLanguage')}</p>

        <div className="language-options" role="group" aria-label={t('language.title')}>
          {OPTIONS.map((option) => {
            const isSelected = selected === option.code;
            return (
              <motion.button
                key={option.code}
                type="button"
                className={`language-option${isSelected ? ' language-option--selected' : ''}`}
                onClick={() => setSelected(option.code)}
                initial={{ opacity: 0, y: reducedMotion ? 0 : 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                aria-pressed={isSelected}
              >
                <span className="language-option__label">
                  <span className="language-option__name">{option.label}</span>
                  <span className="language-option__secondary">{option.secondary}</span>
                </span>
                <span className="language-option__check" aria-hidden="true">
                  {isSelected && <IconCheck />}
                </span>
              </motion.button>
            );
          })}
        </div>

        <div className="language-screen__actions">
          <AnimatePresence>
            {selected && (
              <motion.div
                initial={{ opacity: 0, scale: reducedMotion ? 1 : 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
              >
                <Button onClick={confirm} fullWidth>
                  {t('common.continue')}
                </Button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </div>
  );
}