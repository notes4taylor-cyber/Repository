/**
 * Header — the top bar: game title, current job, a live efficiency gauge
 * (driven by burnout), play-time, and the Reset Save button (with confirm).
 */
import { useGame } from '../game/GameContext';
import { currentJob } from '../game/engine/promotions';
import { efficiency } from '../game/engine/tick';
import { formatDuration } from '../game/format';

export function Header() {
  const { state, resetGame } = useGame();
  const job = currentJob(state);
  const eff = Math.round(efficiency(state) * 100);

  // Color the efficiency readout by health: green / amber / red.
  const effColor = eff >= 75 ? '#34d399' : eff >= 45 ? '#fbbf24' : '#f87171';

  const onReset = () => {
    if (
      window.confirm(
        'Resign and wipe your save? Your salary, titles, and carefully cultivated political capital will all be lost. (This cannot be undone.)',
      )
    ) {
      resetGame();
    }
  };

  return (
    <header className="header">
      <div className="header__brand">
        <span className="header__logo">🏢</span>
        <div>
          <h1 className="header__title">Corporate Climber Idle</h1>
          <p className="header__subtitle">
            {job.title} · {formatDuration(state.totalPlayTime)} on the clock
          </p>
        </div>
      </div>

      <div className="header__right">
        <div className="header__efficiency" title="Productivity, reduced by Burnout">
          <span className="header__efflabel">Efficiency</span>
          <span className="header__effvalue" style={{ color: effColor }}>
            {eff}%
          </span>
        </div>
        <button className="btn btn--danger" onClick={onReset}>
          Resign &amp; Reset
        </button>
      </div>
    </header>
  );
}
