import { useEffect, useRef, useState, type ReactNode } from 'react';
import { useLocalization } from '@/i18n';
import { useTheme } from '@/theme/ThemeProvider';
import { useNav } from '@/navigation/NavContext';
import { IconDots, IconGlobe, IconMoon, IconSun, IconHome, IconBook, IconClock } from '@/components/common/Icons';

type MenuItem = {
  id: string;
  label: string;
  icon: ReactNode;
};

export function Header() {
  const { locale, setLocale, t } = useLocalization();
  const { theme, toggleTheme } = useTheme();
  const { navigate, goHome } = useNav();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const items: MenuItem[] = [
    { id: 'home', label: t('nav.home'), icon: <IconHome /> },
    { id: 'explore', label: t('nav.explore'), icon: <IconBook /> },
    { id: 'history', label: t('nav.history'), icon: <IconClock /> },
  ];

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onPointerDown);
    return () => document.removeEventListener('mousedown', onPointerDown);
  }, [open]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  function handleSelect(id: string) {
    setOpen(false);
    if (id === 'home') goHome();
    else if (id === 'explore') navigate('EXPLORE');
    else if (id === 'history') navigate('HISTORY');
  }

  function toggleLanguage() {
    setLocale(locale === 'en' ? 'hi' : 'en');
  }

  return (
    <header className="header">
      <div className="header__inner">
        <button
          type="button"
          className="header__brand"
          onClick={goHome}
          aria-label={t('nav.home')}
        >
          <span className="header__logo" aria-hidden="true" />
          <span className="header__name">{t('brand.name')}</span>
        </button>
        <div className="header__actions">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme'}
            title={theme === 'light' ? 'Dark mode' : 'Light mode'}
          >
            {theme === 'light' ? <IconMoon /> : <IconSun />}
          </button>
          <button
            type="button"
            className="lang-toggle"
            onClick={toggleLanguage}
            aria-label={locale === 'en' ? 'Switch language to हिन्दी' : 'भाषा को English में बदलें'}
          >
            <IconGlobe />
            <span className="lang-toggle__label">{locale === 'en' ? 'हिन्दी' : 'English'}</span>
          </button>

          <div className="nav-menu" ref={menuRef}>
            <button
              type="button"
              className="nav-menu__trigger"
              aria-haspopup="menu"
              aria-expanded={open}
              aria-label={t('nav.menu')}
              onClick={() => setOpen((v) => !v)}
            >
              <IconDots />
            </button>
            {open && (
              <div className="nav-menu__dropdown" role="menu">
                {items.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    role="menuitem"
                    className="nav-menu__item"
                    onClick={() => handleSelect(item.id)}
                  >
                    <span className="nav-menu__icon" aria-hidden="true">
                      {item.icon}
                    </span>
                    {item.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
