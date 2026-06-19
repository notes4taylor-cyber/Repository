/**
 * engine/skills.ts
 * ----------------
 * The MATH for skill leveling and the bonuses skills provide. Kept separate
 * from the skill DATA (data/skills.ts) so designers can tune numbers without
 * touching logic, and logic without touching numbers.
 */
import type { GameState, SkillId, SkillState } from '../types';
import { SKILLS, SKILL_MAP } from '../data/skills';

/**
 * XP required to advance FROM the given level TO the next one.
 * Costs grow geometrically: each level multiplies the previous cost by
 * the skill's `xpGrowth`.
 */
export function xpToNext(skillId: SkillId, level: number): number {
  const def = SKILL_MAP[skillId];
  return Math.round(def.baseXpToLevel * Math.pow(def.xpGrowth, level - 1));
}

/**
 * Add XP to a skill and apply as many level-ups as the XP allows.
 * Mutates the passed-in SkillState (callers work on a cloned draft).
 */
export function addSkillXp(skill: SkillState, skillId: SkillId, amount: number): void {
  skill.xp += amount;
  // A single big XP grant could span multiple levels — loop until it doesn't.
  let needed = xpToNext(skillId, skill.level);
  while (skill.xp >= needed) {
    skill.xp -= needed;
    skill.level += 1;
    needed = xpToNext(skillId, skill.level);
  }
}

/**
 * The global Work Output multiplier contributed by ALL skills combined.
 * Returns e.g. 1.32 for "+32% output". Level 1 is the baseline and adds
 * nothing; every level above 1 contributes `outputBonusPerLevel`.
 */
export function skillOutputMultiplier(state: GameState): number {
  let bonus = 0;
  for (const def of SKILLS) {
    const level = state.skills[def.id].level;
    bonus += (level - 1) * def.outputBonusPerLevel;
  }
  return 1 + bonus;
}
