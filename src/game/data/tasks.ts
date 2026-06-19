/**
 * tasks.ts
 * --------
 * Pure DATA: the eight starting corporate tasks. This is the file you'll edit
 * most often when adding content. Each task is fully data-driven — duration,
 * costs, rewards, the skill it trains, and when it unlocks. The engine reads
 * these fields generically, so a brand-new task needs ZERO code changes
 * beyond adding its id to the `TaskId` union in types.ts.
 *
 * Reward tuning note: a task's resource rewards are scaled at completion time
 * by (1) the player's current efficiency (burnout) and (2) the level of its
 * `primarySkill`. See engine/tick.ts -> completeTaskCycle().
 */
import type { TaskDef } from '../types';

export const TASKS: TaskDef[] = [
  {
    id: 'answerEmails',
    name: 'Answer Emails',
    description: 'Generate work output while slowly losing your soul.',
    duration: 3,
    energyCost: 5,
    burnoutCost: 3,
    primarySkill: 'emailEfficiency',
    rewards: {
      resources: { workOutput: 8, reputation: 1 },
      skillXp: { emailEfficiency: 6 },
    },
  },
  {
    id: 'pretendToBeBusy',
    name: 'Pretend To Be Busy',
    description: 'Low output, low risk. The classic corporate survival skill.',
    duration: 4,
    energyCost: 1,
    burnoutCost: 0,
    primarySkill: 'corporateJargon',
    rewards: {
      resources: { workOutput: 2, reputation: 2 },
      skillXp: { corporateJargon: 3 },
    },
  },
  {
    id: 'attendMeeting',
    name: 'Attend Meeting',
    description: 'Converts energy into reputation and, inevitably, burnout.',
    duration: 6,
    energyCost: 12,
    burnoutCost: 8,
    primarySkill: 'meetingEndurance',
    rewards: {
      resources: { reputation: 6, workOutput: 3 },
      skillXp: { meetingEndurance: 8, corporateJargon: 2 },
    },
  },
  {
    id: 'buildSpreadsheet',
    name: 'Build Spreadsheet',
    description: 'A pivot table so beautiful it makes finance weep.',
    duration: 7,
    energyCost: 10,
    burnoutCost: 6,
    primarySkill: 'spreadsheetMastery',
    requirement: { skill: { id: 'emailEfficiency', level: 2 } },
    rewards: {
      resources: { workOutput: 18, reputation: 3 },
      skillXp: { spreadsheetMastery: 12 },
    },
  },
  {
    id: 'writeStatusReport',
    name: 'Write Status Report',
    description: 'Summarize a week of chaos into three reassuring bullet points.',
    duration: 8,
    energyCost: 9,
    burnoutCost: 7,
    primarySkill: 'corporateJargon',
    requirement: { minJobLevel: 1 },
    rewards: {
      resources: { workOutput: 14, reputation: 8 },
      skillXp: { corporateJargon: 8, spreadsheetMastery: 3 },
    },
  },
  {
    id: 'networkWithManager',
    name: 'Network With Manager',
    description: 'Trade dignity for Political Capital at the coffee machine.',
    duration: 10,
    energyCost: 14,
    burnoutCost: 5,
    primarySkill: 'networking',
    requirement: { minJobLevel: 2 },
    rewards: {
      resources: { politicalCapital: 5, reputation: 4 },
      skillXp: { networking: 14 },
    },
  },
  {
    id: 'completeTraining',
    name: 'Complete Training Module',
    description: 'Mandatory e-learning. Mostly clicking "Next" until it ends.',
    duration: 12,
    energyCost: 8,
    burnoutCost: 2,
    primarySkill: 'strategicThinking',
    requirement: { minJobLevel: 2 },
    rewards: {
      // Training pays little money but big skill XP across the board.
      resources: { reputation: 2 },
      skillXp: { strategicThinking: 18, spreadsheetMastery: 6, corporateJargon: 6 },
    },
  },
  {
    id: 'createPowerpoint',
    name: 'Create PowerPoint Deck',
    description: 'Forty slides to say what one slide could. Leadership loves it.',
    duration: 14,
    energyCost: 16,
    burnoutCost: 10,
    primarySkill: 'strategicThinking',
    requirement: { minJobLevel: 3, skill: { id: 'corporateJargon', level: 4 } },
    rewards: {
      resources: { workOutput: 40, reputation: 14, politicalCapital: 3 },
      skillXp: { strategicThinking: 16, corporateJargon: 8 },
    },
  },
];

export const TASK_MAP = Object.fromEntries(TASKS.map((t) => [t.id, t])) as Record<
  TaskDef['id'],
  TaskDef
>;
