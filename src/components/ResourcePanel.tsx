/**
 * ResourcePanel — the dashboard strip of resource counters along the top.
 * Renders whatever is in RESOURCES; Energy/Burnout also show a mini bar since
 * they're capped 0..100. Live per-second rates are shown for Output & Salary.
 */
import { useGame } from '../game/GameContext';
import { RESOURCES } from '../game/data/resources';
import { formatResource, formatRate } from '../game/format';
import { outputPerSecond, salaryPerSecond } from '../game/engine/tick';
import { ProgressBar } from './ProgressBar';

export function ResourcePanel() {
  const { state } = useGame();
  const outRate = outputPerSecond(state);
  const salRate = salaryPerSecond(state);

  return (
    <section className="resource-panel" aria-label="Resources">
      {RESOURCES.map((res) => {
        const value = state.resources[res.id];
        const capped = res.max !== undefined;

        // Per-second rate hint for the two passive-income resources.
        let rate: string | null = null;
        if (res.id === 'workOutput') rate = formatRate(outRate);
        if (res.id === 'salary') rate = formatRate(salRate, 'currency');

        return (
          <div className="resource" key={res.id} title={res.description}>
            <div className="resource__top">
              <span className="resource__icon">{res.icon}</span>
              <span className="resource__name">{res.name}</span>
            </div>
            <div className="resource__value" style={{ color: res.color }}>
              {formatResource(value, res.format)}
            </div>
            {rate && <div className="resource__rate">{rate}</div>}
            {capped && (
              <ProgressBar value={value / res.max!} color={res.color} height={6} />
            )}
          </div>
        );
      })}
    </section>
  );
}
