/**
 * engine/state.ts
 * ---------------
 * Factory for a brand-new game state plus a couple of small helpers. This is
 * the single source of truth for "what does a fresh save look like" and it is
 * built entirely from the data files, so adding a resource/skill/task here
 * requires no edits — they're picked up automatically.
 */
import type { GameState, ResourceId, TaskId } from '../types';
import { RESOURCES } from '../data/resources';
import { SKILLS } from '../data/skills';
import { TASKS } from '../data/tasks';

/** The current save format. Bump this if the shape changes incompatibly. */
export const SAVE_VERSION = 1;

export function createInitialState(): GameState {
  const resources = Object.fromEntries(
    RESOURCES.map((r) => [r.id, r.initial]),
  ) as Record<ResourceId, number>;

  const skills = Object.fromEntries(
    SKILLS.map((s) => [s.id, { level: 1, xp: 0 }]),
  ) as GameState['skills'];

  const tasks = Object.fromEntries(
    TASKS.map((t) => [t.id, { running: false, progress: 0, auto: false }]),
  ) as Record<TaskId, GameState['tasks'][TaskId]>;

  return {
    resources,
    skills,
    tasks,
    jobIndex: 0,
    lastTick: Date.now(),
    totalPlayTime: 0,
    version: SAVE_VERSION,
  };
}

/**
 * Clamp a resource to its valid range. Resources never go below 0, and
 * capped resources (Energy, Burnout) never exceed their `max`.
 */
export function clampResource(
  resources: Record<ResourceId, number>,
  id: ResourceId,
  max?: number,
): void {
  if (resources[id] < 0) resources[id] = 0;
  if (max !== undefined && resources[id] > max) resources[id] = max;
}
