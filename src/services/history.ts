export type HistoryEntry = {
  id: string;
  filename: string;
  grade: number;
  confidence: number;
  referable: boolean;
  previewUrl: string | null;
  date: string;
};

const STORAGE_KEY = 'neurovista.screening-history';
const MAX_ENTRIES = 20;

function readAll(): HistoryEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return (parsed as HistoryEntry[]).filter(
      (entry) =>
        !entry.previewUrl || (entry.previewUrl.startsWith('data:') || entry.previewUrl.startsWith('http')),
    );
  } catch {
    return [];
  }
}

export function saveHistoryEntry(entry: Omit<HistoryEntry, 'id' | 'date'>): HistoryEntry {
  const all = readAll();
  const saved: HistoryEntry = {
    ...entry,
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    date: new Date().toISOString(),
  };
  const next = [saved, ...all].slice(0, MAX_ENTRIES);
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    /* storage full or unavailable — ignore */
  }
  return saved;
}

export function getHistoryEntries(): HistoryEntry[] {
  return readAll();
}

export function clearHistory(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}
