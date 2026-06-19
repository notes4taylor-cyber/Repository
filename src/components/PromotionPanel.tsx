/**
 * PromotionPanel — your career ladder. Shows the current title, the next role
 * with a live requirements checklist, and a Promote button that lights up once
 * every requirement is met. Requirements/labels are derived from data.
 */
import { useGame } from '../game/GameContext';
import {
  currentJob,
  nextJob,
  evaluateRequirement,
  canPromote,
} from '../game/engine/promotions';
import { RESOURCE_MAP } from '../game/data/resources';
import { SKILL_MAP } from '../game/data/skills';
import { abbreviate } from '../game/format';

/** Turn an internal requirement label like "reputation" into a pretty name. */
function prettyLabel(label: string): string {
  const base = label.replace(' (lvl)', '');
  if (base in RESOURCE_MAP) return RESOURCE_MAP[base as keyof typeof RESOURCE_MAP].name;
  if (base in SKILL_MAP) return `${SKILL_MAP[base as keyof typeof SKILL_MAP].name} (lvl)`;
  return label;
}

export function PromotionPanel() {
  const { state, doPromote } = useGame();
  const job = currentJob(state);
  const next = nextJob(state);
  const ready = canPromote(state);

  return (
    <div className="card promotion">
      <div className="promotion__current">
        <span className="promotion__label">Current Role</span>
        <h2 className="promotion__title">{job.title}</h2>
        <p className="promotion__desc">{job.description}</p>
        {job.perk && <p className="promotion__perk">🎖 {job.perk}</p>}
      </div>

      {next ? (
        <div className="promotion__next">
          <span className="promotion__label">Next Role</span>
          <h3 className="promotion__nexttitle">{next.title}</h3>
          <ul className="req-list">
            {evaluateRequirement(state, next.requirement).map((r) => (
              <li key={r.label} className={r.met ? 'req req--met' : 'req req--unmet'}>
                <span>{r.met ? '✓' : '○'} {prettyLabel(r.label)}</span>
                <span className="req__nums">
                  {abbreviate(r.current)} / {abbreviate(r.needed)}
                </span>
              </li>
            ))}
          </ul>
          <button className="btn btn--promote" disabled={!ready} onClick={doPromote}>
            {ready ? `🚀 Get Promoted to ${next.title}` : 'Requirements not met'}
          </button>
        </div>
      ) : (
        <div className="promotion__next">
          <h3 className="promotion__nexttitle">🏆 Top of the Ladder</h3>
          <p className="promotion__desc">
            You are a C-Suite Executive. There is nowhere left to climb — only
            quarterly earnings calls, forever.
          </p>
        </div>
      )}
    </div>
  );
}
