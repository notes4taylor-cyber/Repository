/**
 * engine/save.ts
 * --------------
 * LocalStorage persistence + offline-progress catch-up. The entire GameState
 * is JSON-serialisable, so saving is just `JSON.stringify`. On load we run the
 * tick engine once for however long the player was away (capped) so the game
 * keeps "playing" while closed.
 */
import type { GameState } from '../types';
import { createInitialState, SAVE_VERSION } from './state';
import { tick } from './tick';

const STORAGE_KEY = 'corporate-climber-idle:save';

/** Don't reward more than this much offline time (8 hours), to stay sane. */
const MAX_OFFLINE_SECONDS = 8 * 60 * 60;

/** Persist the game state to LocalStorage. Fails quietly if storage is full. */
export function saveGame(state: GameState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...state, lastTick: Date.now() }));
  } catch (err) {
    // Private-mode browsers / quota errors shouldn't crash the game.
    console.warn('Could not save game:', err);
  }
}

/**
 * Load a saved game, or return a fresh state if none/invalid exists.
 * Applies offline progress for the elapsed real time since the last save.
 * Returns the state plus how many seconds of offline time were credited
 * (so the UI can show a "welcome back" summary).
 */
export function loadGame(): { state: GameState; offlineSeconds: number } {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return { state: createInitialState(), offlineSeconds: 0 };

  try {
    const parsed = JSON.parse(raw) as GameState;

    // If the save format changed, start fresh rather than crash on bad data.
    if (parsed.version !== SAVE_VERSION) {
      return { state: createInitialState(), offlineSeconds: 0 };
    }

    // Merge onto a fresh state so any newly-added resources/skills/tasks
    // (not present in an older save) get sensible defaults.
    const base = createInitialState();
    const merged: GameState = {
      ...base,
      ...parsed,
      resources: { ...base.resources, ...parsed.resources },
      skills: { ...base.skills, ...parsed.skills },
      tasks: { ...base.tasks, ...parsed.tasks },
    };

    const elapsedMs = Date.now() - (parsed.lastTick ?? Date.now());
    const offlineSeconds = Math.min(MAX_OFFLINE_SECONDS, Math.max(0, elapsedMs / 1000));

    const state = offlineSeconds > 0 ? tick(merged, offlineSeconds) : merged;
    return { state, offlineSeconds };
  } catch (err) {
    console.warn('Save was corrupt, starting fresh:', err);
    return { state: createInitialState(), offlineSeconds: 0 };
  }
}

/** Wipe the save. The UI confirms with the user before calling this. */
export function clearSave(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.warn('Could not clear save:', err);
  }
}
