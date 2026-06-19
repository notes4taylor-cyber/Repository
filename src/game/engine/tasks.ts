/**
 * engine/tasks.ts
 * ---------------
 * Player-driven task actions and unlock logic. Starting a task pays its energy
 * cost up front; the tick engine then advances it to completion.
 */
import type { GameState, TaskDef } from '../types';

/**
 * Is a task unlocked for the player yet? Checks the (optional) job-level and
 * skill-level requirements declared on the task data.
 */
export function isTaskUnlocked(state: GameState, task: TaskDef): boolean {
  const req = task.requirement;
  if (!req) return true;
  if (req.minJobLevel !== undefined && state.jobIndex < req.minJobLevel) return false;
  if (req.skill && state.skills[req.skill.id].level < req.skill.level) return false;
  return true;
}

/** Can the player start a fresh cycle of this task right now? */
export function canStartTask(state: GameState, task: TaskDef): boolean {
  if (!isTaskUnlocked(state, task)) return false;
  if (state.tasks[task.id].running) return false;
  return state.resources.energy >= task.energyCost;
}

/**
 * Start one cycle of a task. Returns a NEW state. Spends energy immediately;
 * the reward is paid out by the tick engine when the cycle completes.
 */
export function startTask(state: GameState, task: TaskDef): GameState {
  if (!canStartTask(state, task)) return state;
  return {
    ...state,
    resources: { ...state.resources, energy: state.resources.energy - task.energyCost },
    tasks: {
      ...state.tasks,
      [task.id]: { ...state.tasks[task.id], running: true, progress: 0 },
    },
  };
}

/** Toggle a task's auto-repeat flag. Returns a NEW state. */
export function toggleTaskAuto(state: GameState, taskId: TaskDef['id']): GameState {
  const rt = state.tasks[taskId];
  return {
    ...state,
    tasks: { ...state.tasks, [taskId]: { ...rt, auto: !rt.auto } },
  };
}
