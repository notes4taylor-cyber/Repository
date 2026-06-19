/**
 * engine/promotions.ts
 * --------------------
 * Promotion eligibility + the act of getting promoted. All requirements are
 * read generically from data/jobs.ts, so new tiers and requirement types
 * (any resource, any skill) work without code changes.
 */
import type { GameState, JobRequirement, ResourceId, SkillId } from '../types';
import { JOBS, MAX_JOB_INDEX } from '../data/jobs';

/** A single unmet requirement, used to explain WHY you can't be promoted yet. */
export interface RequirementProgress {
  label: string;
  current: number;
  needed: number;
  met: boolean;
}

/** The job the player currently holds. */
export function currentJob(state: GameState) {
  return JOBS[state.jobIndex];
}

/** The next job up the ladder, or `null` if already at the top. */
export function nextJob(state: GameState) {
  return state.jobIndex < MAX_JOB_INDEX ? JOBS[state.jobIndex + 1] : null;
}

/**
 * Break a job's requirement down into a checklist with progress. The UI uses
 * this to render "Reputation 12 / 30 ✓/✗" rows.
 */
export function evaluateRequirement(
  state: GameState,
  req: JobRequirement | undefined,
): RequirementProgress[] {
  if (!req) return [];
  const rows: RequirementProgress[] = [];

  if (req.resources) {
    for (const [id, needed] of Object.entries(req.resources) as [ResourceId, number][]) {
      const current = state.resources[id];
      rows.push({
        label: id,
        current,
        needed,
        met: current >= needed,
      });
    }
  }
  if (req.skills) {
    for (const [id, needed] of Object.entries(req.skills) as [SkillId, number][]) {
      const current = state.skills[id].level;
      rows.push({
        label: `${id} (lvl)`,
        current,
        needed,
        met: current >= needed,
      });
    }
  }
  return rows;
}

/** True if every requirement for the next job is satisfied. */
export function canPromote(state: GameState): boolean {
  const next = nextJob(state);
  if (!next) return false;
  return evaluateRequirement(state, next.requirement).every((r) => r.met);
}

/**
 * Apply a promotion. Returns a NEW state (does not mutate the input).
 * Promotions are a clean reward: we bump the job tier. We intentionally do
 * NOT spend the resources — they're thresholds, not currencies — which keeps
 * the early game feeling generous and the satire intact.
 */
export function promote(state: GameState): GameState {
  if (!canPromote(state)) return state;
  return { ...state, jobIndex: state.jobIndex + 1 };
}
