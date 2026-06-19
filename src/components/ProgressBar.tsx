/**
 * ProgressBar — a tiny reusable bar. `value` is 0..1. Purely presentational.
 */
interface Props {
  value: number;
  color?: string;
  /** Optional text overlaid in the centre of the bar. */
  label?: string;
  height?: number;
}

export function ProgressBar({ value, color = '#60a5fa', label, height = 8 }: Props) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div className="progress" style={{ height }}>
      <div className="progress__fill" style={{ width: `${pct}%`, background: color }} />
      {label && <span className="progress__label">{label}</span>}
    </div>
  );
}
