/**
 * engine/tick.ts
 * --------------
 * THE game loop. `tick(state, dt)` advances the world by `dt` seconds and
 * returns a new state. It is a pure function (no React, no timers, no I/O),
 * which makes it easy to reason about, test, and reuse for offline progress.
 *
 * Responsibilities each tick:
 *   1. Passive recovery   — Energy regenerates, Burnout slowly decays.
 *   2. Passive production  — your job + skills generate Work Output -> Salary.
 *   3. Active tasks        — advance any running task; on completion pay out
 *                            rewards and (if auto) start the next cycle.
 *
 * Burnout is the central penalty: high Burnout multiplies all production by a
 * low "efficiency" factor.
 */
import type { GameState, ResourceId, TaskDef } from '../types';
import { RESOURCE_MAP } from '../data/resources';
import { TASKS } from '../data/tasks';
import { JOBS } from '../data/jobs';
import { addSkillXp, skillOutputMultiplier } from './skills';
import { clampResource } from './state';

/* ----------------------------- tuning knobs ----------------------------- */
/** Energy regained per second while alive. */
export const ENERGY_REGEN = 4;
/** Burnout naturally shed per second (resting between tasks). */
export const BURNOUT_DECAY = 1.5;
/** Each level of a task's primary skill boosts that task's payout by this. */
export const SKILL_REWARD_BONUS_PER_LEVEL = 0.1;
/** Safety cap so a huge offline `dt` can't spin forever. */
const MAX_CYCLES_PER_TICK = 100_000;

/* --------------------------- derived getters ---------------------------- */

/**
 * Efficiency in [0.2, 1.0], driven by Burnout. At 0 burnout you're at 100%;
 * it falls linearly and bottoms out at 20% so the game is never fully stuck.
 */
export function efficiency(state: GameState): number {
  const eff = 1 - state.resources.burnout / 130;
  return Math.max(0.2, Math.min(1, eff));
}

/** Passive Work Output generated per second, after skills + burnout. */
export function outputPerSecond(state: GameState): number {
  const job = JOBS[state.jobIndex];
  return job.baseOutput * skillOutputMultiplier(state) * efficiency(state);
}

/** Passive Salary earned per second (Work Output × your tier's pay rate). */
export function salaryPerSecond(state: GameState): number {
  return outputPerSecond(state) * JOBS[state.jobIndex].salaryPerOutput;
}

/* ----------------------------- internals -------------------------------- */

/** A running task's progress gained per second. */
function progressPerSecond(task: TaskDef): number {
  return 1 / task.duration;
}

/**
 * Apply one completed cycle of a task: grant scaled resource rewards, add
 * burnout, and award (flat) skill XP. Mutates the draft state.
 */
function completeTaskCycle(state: GameState, task: TaskDef): void {
  const eff = efficiency(state);

  // Reward scaling: efficiency × a bonus from the task's primary skill level.
  let skillBonus = 1;
  if (task.primarySkill) {
    const level = state.skills[task.primarySkill].level;
    skillBonus = 1 + (level - 1) * SKILL_REWARD_BONUS_PER_LEVEL;
  }
  const factor = eff * skillBonus;

  if (task.rewards.resources) {
    for (const [id, amount] of Object.entries(task.rewards.resources) as [
      ResourceId,
      number,
    ][]) {
      state.resources[id] += amount * factor;
    }
  }

  // Burnout cost is flat (it doesn't get cheaper just because you're skilled).
  state.resources.burnout += task.burnoutCost;

  if (task.rewards.skillXp) {
    for (const [skillId, xp] of Object.entries(task.rewards.skillXp)) {
      addSkillXp(state.skills[skillId as keyof GameState['skills']], skillId as never, xp);
    }
  }
}

/* ------------------------------- the tick ------------------------------- */

/**
 * Advance the whole game by `dt` seconds and return a NEW state object.
 * Never mutates the input (so React state updates stay safe).
 */
export function tick(prev: GameState, dt: number): GameState {
  if (dt <= 0) return prev;

  // --- shallow clone, then deep-clone the mutable sub-objects we touch ---
  const state: GameState = {
    ...prev,
    resources: { ...prev.resources },
    skills: Object.fromEntries(
      Object.entries(prev.skills).map(([k, v]) => [k, { ...v }]),
    ) as GameState['skills'],
    tasks: Object.fromEntries(
      Object.entries(prev.tasks).map(([k, v]) => [k, { ...v }]),
    ) as GameState['tasks'],
  };

  // 1) Passive recovery.
  state.resources.energy += ENERGY_REGEN * dt;
  state.resources.burnout -= BURNOUT_DECAY * dt;

  // 2) Passive production from your job + skills, scaled by burnout.
  const output = outputPerSecond(state) * dt;
  state.resources.workOutput += output;
  state.resources.salary += output * JOBS[state.jobIndex].salaryPerOutput;

  // 3) Active tasks.
  for (const task of TASKS) {
    const rt = state.tasks[task.id];
    if (!rt.running) continue;

    rt.progress += progressPerSecond(task) * dt;

    let guard = 0;
    while (rt.progress >= 1 && guard++ < MAX_CYCLES_PER_TICK) {
      completeTaskCycle(state, task);
      rt.progress -= 1;

      // Auto-repeat: only continue if we can afford the next cycle's energy.
      if (rt.auto && state.resources.energy >= task.energyCost) {
        state.resources.energy -= task.energyCost;
      } else {
        rt.running = false;
        rt.progress = 0;
        break;
      }
    }
  }

  // Clamp every resource to its valid range (0..max).
  for (const id of Object.keys(state.resources) as ResourceId[]) {
    clampResource(state.resources, id, RESOURCE_MAP[id].max);
  }

  state.totalPlayTime += dt;
  state.lastTick = Date.now();
  return state;
}
