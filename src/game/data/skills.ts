/**
 * skills.ts
 * ---------
 * Pure DATA: the six skills. Skills gain XP from tasks and, per level, boost
 * global Work Output. The leveling MATH lives in engine/skills.ts so that the
 * data here stays declarative and easy to tune.
 */
import type { SkillDef, SkillId } from '../types';

export const SKILLS: SkillDef[] = [
  {
    id: 'emailEfficiency',
    name: 'Email Efficiency',
    icon: '📧',
    description: 'Reply-all faster than the speed of thought.',
    baseXpToLevel: 25,
    xpGrowth: 1.45,
    outputBonusPerLevel: 0.04,
  },
  {
    id: 'spreadsheetMastery',
    name: 'Spreadsheet Mastery',
    icon: '📊',
    description: 'VLOOKUP is a personality trait now.',
    baseXpToLevel: 30,
    xpGrowth: 1.5,
    outputBonusPerLevel: 0.05,
  },
  {
    id: 'meetingEndurance',
    name: 'Meeting Endurance',
    icon: '🪑',
    description: 'Survive 90-minute syncs that could have been an email.',
    baseXpToLevel: 35,
    xpGrowth: 1.5,
    outputBonusPerLevel: 0.04,
  },
  {
    id: 'networking',
    name: 'Networking',
    icon: '🌐',
    description: 'Laugh at the right jokes; remember the right names.',
    baseXpToLevel: 40,
    xpGrowth: 1.55,
    outputBonusPerLevel: 0.03,
  },
  {
    id: 'corporateJargon',
    name: 'Corporate Jargon',
    icon: '🗣️',
    description: "Let's circle back and synergize our core competencies.",
    baseXpToLevel: 30,
    xpGrowth: 1.5,
    outputBonusPerLevel: 0.04,
  },
  {
    id: 'strategicThinking',
    name: 'Strategic Thinking',
    icon: '🧠',
    description: 'See the chessboard while everyone else plays checkers.',
    baseXpToLevel: 50,
    xpGrowth: 1.6,
    outputBonusPerLevel: 0.06,
  },
];

export const SKILL_MAP: Record<SkillId, SkillDef> = Object.fromEntries(
  SKILLS.map((s) => [s.id, s]),
) as Record<SkillId, SkillDef>;
