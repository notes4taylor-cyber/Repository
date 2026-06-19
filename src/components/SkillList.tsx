/**
 * SkillList — shows each skill's level, XP progress to the next level, and the
 * global output bonus it currently provides. Skills level up automatically as
 * tasks grant XP, so there's nothing to click here — it's a live readout.
 */
import { useGame } from '../game/GameContext';
import { SKILLS } from '../game/data/skills';
import { xpToNext } from '../game/engine/skills';
import { ProgressBar } from './ProgressBar';

export function SkillList() {
  const { state } = useGame();

  return (
    <div className="skill-list">
      {SKILLS.map((skill) => {
        const s = state.skills[skill.id];
        const needed = xpToNext(skill.id, s.level);
        const bonus = Math.round((s.level - 1) * skill.outputBonusPerLevel * 100);
        return (
          <div className="card skill" key={skill.id} title={skill.description}>
            <div className="skill__top">
              <span className="skill__icon">{skill.icon}</span>
              <span className="skill__name">{skill.name}</span>
              <span className="skill__level">Lv. {s.level}</span>
            </div>
            <ProgressBar
              value={s.xp / needed}
              color="#fbbf24"
              height={7}
              label={`${Math.floor(s.xp)}/${needed} xp`}
            />
            <div className="skill__bonus">+{bonus}% output</div>
          </div>
        );
      })}
    </div>
  );
}
