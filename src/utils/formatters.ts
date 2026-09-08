export function formatConfidence(confidence: number): number {
  return Math.round(confidence * 100);
}

export function formatPercent(fraction: number): string {
  return `${formatConfidence(fraction)}%`;
}
