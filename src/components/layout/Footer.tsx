import { useLocalization } from '@/i18n';

export function Footer() {
  const { t } = useLocalization();
  return (
    <footer className="footer">
      <p>{t('brand.disclaimer')}</p>
    </footer>
  );
}