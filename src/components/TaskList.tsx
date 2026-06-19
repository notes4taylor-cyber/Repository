/**
 * TaskList — renders all unlocked tasks as cards, and a muted "locked" hint
 * for tasks the player hasn't qualified for yet (so progression feels visible).
 */
import { useGame } from '../game/GameContext';
import { TASKS } from '../game/data/tasks';
import { isTaskUnlocked } from '../game/engine/tasks';
import { SKILL_MAP } from '../game/data/skills';
import { JOBS } from '../game/data/jobs';
import { TaskCard } from './TaskCard';

export function TaskList() {
  const { state } = useGame();

  const unlocked = TASKS.filter((t) => isTaskUnlocked(state, t));
  const locked = TASKS.filter((t) => !isTaskUnlocked(state, t));

  return (
    <div>
      <div className="task-grid">
        {unlocked.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>

      {locked.length > 0 && (
        <div className="locked-list">
          {locked.map((task) => {
            const req = task.requirement!;
            const parts: string[] = [];
            if (req.minJobLevel !== undefined) parts.push(JOBS[req.minJobLevel].title);
            if (req.skill) parts.push(`${SKILL_MAP[req.skill.id].name} Lv.${req.skill.level}`);
            return (
              <div className="locked-item" key={task.id}>
                🔒 <strong>{task.name}</strong> — requires {parts.join(' + ')}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
