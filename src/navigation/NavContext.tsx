import { createContext, useContext } from 'react';
import type { AppState } from '@/types/screening';

type NavContextValue = {
  navigate: (to: AppState) => void;
  goHome: () => void;
};

export const NavContext = createContext<NavContextValue>({
  navigate: () => undefined,
  goHome: () => undefined,
});

export function useNav(): NavContextValue {
  return useContext(NavContext);
}
