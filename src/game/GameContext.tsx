/**
 * GameContext.tsx
 * ---------------
 * The bridge between the pure game engine and React. It:
 *   - holds the single GameState in React state,
 *   - runs the real-time tick on an interval (using wall-clock delta time so
 *     the game stays accurate even if the tab throttles the timer),
 *   - auto-saves to LocalStorage periodically,
 *   - exposes player actions (start task, toggle auto, promote, reset).
 *
 * UI components consume this via the `useGame()` hook and never import the
 * engine directly, keeping a clean one-way data flow.
 */
import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import type { GameState, TaskDef, TaskId } from './types';
import { loadGame, saveGame, clearSave } from './engine/save';
import { createInitialState } from './engine/state';
import { tick } from './engine/tick';
import { startTask, toggleTaskAuto } from './engine/tasks';
import { promote } from './engine/promotions';

/** How often the simulation advances (ms). 10 ticks/sec feels smooth. */
const TICK_MS = 100;
/** How often we persist to LocalStorage (ms). */
const SAVE_MS = 5000;

interface GameContextValue {
  state: GameState;
  offlineSeconds: number;
  startTask: (task: TaskDef) => void;
  toggleAuto: (taskId: TaskId) => void;
  doPromote: () => void;
  resetGame: () => void;
}

const GameContext = createContext<GameContextValue | null>(null);

export function GameProvider({ children }: { children: ReactNode }) {
  // Load once on first render (includes offline-progress catch-up).
  const initial = useRef(loadGame());
  const [state, setState] = useState<GameState>(initial.current.state);
  const [offlineSeconds] = useState(initial.current.offlineSeconds);

  // Keep the latest state in a ref so the interval callback always sees it
  // without needing to re-create the interval every render.
  const stateRef = useRef(state);
  stateRef.current = state;

  /* ----------------------------- game loop ----------------------------- */
  useEffect(() => {
    let last = Date.now();
    const id = window.setInterval(() => {
      const now = Date.now();
      const dt = (now - last) / 1000; // real seconds elapsed
      last = now;
      setState((s) => tick(s, dt));
    }, TICK_MS);
    return () => window.clearInterval(id);
  }, []);

  /* ----------------------------- auto-save ----------------------------- */
  useEffect(() => {
    const id = window.setInterval(() => saveGame(stateRef.current), SAVE_MS);
    // Also save when the tab is hidden/closed so progress isn't lost.
    const onHide = () => saveGame(stateRef.current);
    window.addEventListener('beforeunload', onHide);
    document.addEventListener('visibilitychange', onHide);
    return () => {
      window.clearInterval(id);
      window.removeEventListener('beforeunload', onHide);
      document.removeEventListener('visibilitychange', onHide);
    };
  }, []);

  /* ------------------------------ actions ------------------------------ */
  const value: GameContextValue = {
    state,
    offlineSeconds,
    startTask: (task) => setState((s) => startTask(s, task)),
    toggleAuto: (taskId) => setState((s) => toggleTaskAuto(s, taskId)),
    doPromote: () => setState((s) => promote(s)),
    resetGame: () => {
      clearSave();
      setState(createInitialState());
    },
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

/** Hook used by every UI component to read state and dispatch actions. */
export function useGame(): GameContextValue {
  const ctx = useContext(GameContext);
  if (!ctx) throw new Error('useGame must be used within a <GameProvider>');
  return ctx;
}
