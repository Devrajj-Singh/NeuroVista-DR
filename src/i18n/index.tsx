import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import en from './en.json';
import hi from './hi.json';
import type { AppLanguage, TranslationMap } from '@/types/screening';

const TRANSLATIONS: Record<AppLanguage, TranslationMap> = { en, hi };
const STORAGE_KEY = 'neurovista-locale';

type LocalizationContextValue = {
  locale: AppLanguage;
  setLocale: (locale: AppLanguage) => void;
  t: (key: string) => string;
};

const LocalizationContext = createContext<LocalizationContextValue | null>(null);

function resolveKey(translations: TranslationMap, key: string): string | undefined {
  const parts = key.split('.');
  let node: TranslationMap = translations;

  for (const part of parts) {
    const next = node[part];
    if (next === undefined) return undefined;
    if (typeof next === 'string') {
      return part === parts[parts.length - 1] ? next : undefined;
    }
    node = next;
  }

  return undefined;
}

function getInitialLocale(): AppLanguage {
  if (typeof window === 'undefined') return 'en';
  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === 'en' || saved === 'hi') return saved;
  return 'en';
}

export function LocalizationProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<AppLanguage>(getInitialLocale);

  const setLocale = useCallback((next: AppLanguage) => {
    setLocaleState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage unavailable — ignore.
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const t = useCallback(
    (key: string) => resolveKey(TRANSLATIONS[locale], key) ?? key,
    [locale],
  );

  const value = useMemo<LocalizationContextValue>(
    () => ({ locale, setLocale, t }),
    [locale, setLocale, t],
  );

  return <LocalizationContext.Provider value={value}>{children}</LocalizationContext.Provider>;
}

export function useLocalization(): LocalizationContextValue {
  const ctx = useContext(LocalizationContext);
  if (!ctx) {
    throw new Error('useLocalization must be used within a LocalizationProvider');
  }
  return ctx;
}
