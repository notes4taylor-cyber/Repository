/**
 * App — top-level layout. Composes the dashboard from independent panels.
 * Notice there is NO game logic here: App only arranges components, each of
 * which reads what it needs from `useGame()`.
 */
import { useState } from 'react';
import { useGame } from './game/GameContext';
import { Header } from './components/Header';
import { ResourcePanel } from './components/ResourcePanel';
import { TaskList } from './components/TaskList';
import { SkillList } from './components/SkillList';
import { PromotionPanel } from './components/PromotionPanel';
import { formatDuration } from './game/format';

/** A dismissible "welcome back" banner summarizing offline progress. */
function OfflineBanner() {
  const { offlineSeconds } = useGame();
  const [dismissed, setDismissed] = useState(false);
  if (dismissed || offlineSeconds < 60) return null;
  return (
    <div className="offline-banner">
      <span>
        👋 Welcome back! You were "working from home" for{' '}
        <strong>{formatDuration(offlineSeconds)}</strong>. The machine kept
        earning without you.
      </span>
      <button className="btn btn--ghost" onClick={() => setDismissed(true)}>
        Dismiss
      </button>
    </div>
  );
}

export function App() {
  return (
    <div className="app">
      <Header />
      <OfflineBanner />
      <ResourcePanel />

      <main className="layout">
        <section className="layout__main">
          <h2 className="section-title">📋 Tasks</h2>
          <p className="section-hint">
            Click <em>Do it</em> to run a task. Toggle <em>Auto</em> to repeat it
            while you have the energy. Watch your Burnout.
          </p>
          <TaskList />
        </section>

        <aside className="layout__side">
          <h2 className="section-title">🪜 Career</h2>
          <PromotionPanel />

          <h2 className="section-title">🎓 Skills</h2>
          <p className="section-hint">Skills level up automatically as you work.</p>
          <SkillList />
        </aside>
      </main>

      <footer className="footer">
        Corporate Climber Idle · an MVP · progress auto-saves every few seconds.
      </footer>
    </div>
  );
}
