/**
 * TaskCard — a single corporate task. Shows flavor, costs, rewards, a live
 * progress bar while running, a Do-it button, and an Auto toggle. All data
 * comes from the TaskDef; this component contains no game balance numbers.
 */
import type { TaskDef } from '../game/types';
import { useGame } from '../game/GameContext';
import { canStartTask } from '../game/engine/tasks';
import { RESOURCE_MAP } from '../game/data/resources';
import { SKILL_MAP } from '../game/data/skills';
import { ProgressBar } from './ProgressBar';

export function TaskCard({ task }: { task: TaskDef }) {
  const { state, startTask, toggleAuto } = useGame();
  const rt = state.tasks[task.id];
  const startable = canStartTask(state, task);

  // Build a compact "reward chips" list straight from the data.
  const rewardChips: { key: string; text: string }[] = [];
  if (task.rewards.resources) {
    for (const [id, amt] of Object.entries(task.rewards.resources)) {
      rewardChips.push({
        key: `r-${id}`,
        text: `${RESOURCE_MAP[id as keyof typeof RESOURCE_MAP].icon} +${amt}`,
      });
    }
  }
  if (task.rewards.skillXp) {
    for (const [id, xp] of Object.entries(task.rewards.skillXp)) {
      rewardChips.push({
        key: `s-${id}`,
        text: `${SKILL_MAP[id as keyof typeof SKILL_MAP].icon} +${xp}xp`,
      });
    }
  }

  return (
    <div className={`card task ${rt.running ? 'task--running' : ''}`}>
      <div className="task__header">
        <h3 className="task__name">{task.name}</h3>
        <span className="task__duration">⏱ {task.duration}s</span>
      </div>
      <p className="task__desc">{task.description}</p>

      <div className="task__chips">
        {rewardChips.map((c) => (
          <span className="chip chip--reward" key={c.key}>
            {c.text}
          </span>
        ))}
        {task.energyCost > 0 && (
          <span className="chip chip--cost">🔋 -{task.energyCost}</span>
        )}
        {task.burnoutCost > 0 && (
          <span className="chip chip--burn">🔥 +{task.burnoutCost}</span>
        )}
      </div>

      <ProgressBar
        value={rt.running ? rt.progress : 0}
        color="#60a5fa"
        height={10}
        label={rt.running ? `${Math.floor(rt.progress * 100)}%` : ''}
      />

      <div className="task__actions">
        <button className="btn btn--primary" disabled={!startable} onClick={() => startTask(task)}>
          {rt.running ? 'Working…' : startable ? 'Do it' : 'No energy'}
        </button>
        <label className="auto-toggle" title="Automatically repeat this task">
          <input
            type="checkbox"
            checked={rt.auto}
            onChange={() => toggleAuto(task.id)}
          />
          Auto
        </label>
      </div>
    </div>
  );
}
