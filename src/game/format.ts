/**
 * format.ts
 * ---------
 * Small display helpers. Idle games throw huge numbers at you, so we abbreviate
 * (1.2K, 3.4M, 5.6B...). Pure functions, used only by the UI layer.
 */
import type { ResourceFormat } from './types';

const SUFFIXES = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp'];

/** Abbreviate a large number, e.g. 12345 -> "12.3K". */
export function abbreviate(value: number): string {
  if (!isFinite(value)) return '∞';
  const sign = value < 0 ? '-' : '';
  let n = Math.abs(value);
  if (n < 1000) {
    // Show up to 1 decimal for small values, none for whole numbers.
    return sign + (Number.isInteger(n) ? n.toString() : n.toFixed(1));
  }
  let tier = 0;
  while (n >= 1000 && tier < SUFFIXES.length - 1) {
    n /= 1000;
    tier++;
  }
  return `${sign}${n.toFixed(2)}${SUFFIXES[tier]}`;
}

/** Format a resource value according to its declared display format. */
export function formatResource(value: number, format: ResourceFormat): string {
  switch (format) {
    case 'currency':
      return '$' + abbreviate(value);
    case 'percent':
      return Math.round(value) + '%';
    case 'number':
    default:
      return abbreviate(value);
  }
}

/** Format a per-second rate, e.g. "+12.3/s". */
export function formatRate(value: number, format: ResourceFormat = 'number'): string {
  const prefix = format === 'currency' ? '$' : '';
  return `+${prefix}${abbreviate(value)}/s`;
}

/** Turn a count of seconds into "2h 14m" style text. */
export function formatDuration(totalSeconds: number): string {
  const s = Math.floor(totalSeconds);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}
