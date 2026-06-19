/**
 * jobs.ts
 * -------
 * Pure DATA: the ten-tier corporate ladder. The array order IS the career
 * progression — index 0 is your first job, the last index is the top.
 *
 * Each tier defines:
 *  - baseOutput:      passive Work Output / second at this tier
 *  - salaryPerOutput: how much Salary each unit of Work Output is worth
 *                     (this is the main reward for getting promoted)
 *  - requirement:     resource totals + skill levels needed to be promoted
 *                     INTO this tier from the previous one
 *
 * Promotion logic lives in engine/promotions.ts and reads these generically.
 */
import type { JobDef } from '../types';

export const JOBS: JobDef[] = [
  {
    level: 0,
    title: 'Intern',
    description: 'Unpaid in spirit. Here for "the experience."',
    baseOutput: 1,
    salaryPerOutput: 0.5,
    perk: 'Access to the good coffee machine (sometimes).',
    // No requirement — this is where everyone starts.
  },
  {
    level: 1,
    title: 'Junior Analyst',
    description: 'You now have a chair with armrests. Big day.',
    baseOutput: 2,
    salaryPerOutput: 1,
    requirement: { resources: { reputation: 30 } },
    perk: 'Unlocks: Write Status Report.',
  },
  {
    level: 2,
    title: 'Analyst',
    description: 'People cc you on emails now. Run.',
    baseOutput: 4,
    salaryPerOutput: 1.8,
    requirement: {
      resources: { reputation: 90, salary: 250 },
      skills: { spreadsheetMastery: 3 },
    },
    perk: 'Unlocks: Network With Manager, Training Modules.',
  },
  {
    level: 3,
    title: 'Senior Analyst',
    description: 'Same job, fancier title, suspiciously similar pay.',
    baseOutput: 7,
    salaryPerOutput: 3,
    requirement: {
      resources: { reputation: 220, salary: 1200 },
      skills: { spreadsheetMastery: 5, corporateJargon: 3 },
    },
    perk: 'Unlocks: Create PowerPoint Deck.',
  },
  {
    level: 4,
    title: 'Manager',
    description: 'You now attend meetings ABOUT meetings.',
    baseOutput: 12,
    salaryPerOutput: 5,
    requirement: {
      resources: { reputation: 500, salary: 4000, politicalCapital: 20 },
      skills: { meetingEndurance: 5, networking: 4 },
    },
    perk: 'Direct reports who do the actual work.',
  },
  {
    level: 5,
    title: 'Senior Manager',
    description: 'Manager of managers. The org chart fears you.',
    baseOutput: 20,
    salaryPerOutput: 8,
    requirement: {
      resources: { reputation: 1100, salary: 12000, politicalCapital: 60 },
      skills: { networking: 6, strategicThinking: 4 },
    },
    perk: 'A reserved parking spot. Status: achieved.',
  },
  {
    level: 6,
    title: 'Director',
    description: 'You set "strategy" and let others figure out what that means.',
    baseOutput: 34,
    salaryPerOutput: 13,
    requirement: {
      resources: { reputation: 2600, salary: 35000, politicalCapital: 140 },
      skills: { strategicThinking: 7, networking: 8 },
    },
    perk: 'Your calendar is now a full-time job.',
  },
  {
    level: 7,
    title: 'VP',
    description: 'Vice President of Saying Things Confidently.',
    baseOutput: 55,
    salaryPerOutput: 22,
    requirement: {
      resources: { reputation: 6000, salary: 100000, politicalCapital: 320 },
      skills: { strategicThinking: 9, corporateJargon: 8 },
    },
    perk: 'An assistant who guards your calendar with their life.',
  },
  {
    level: 8,
    title: 'Senior VP',
    description: 'You have opinions about "the market." People nod.',
    baseOutput: 90,
    salaryPerOutput: 36,
    requirement: {
      resources: { reputation: 14000, salary: 300000, politicalCapital: 700 },
      skills: { strategicThinking: 12, networking: 11 },
    },
    perk: 'Stock options you pretend to understand.',
  },
  {
    level: 9,
    title: 'C-Suite Executive',
    description: 'You have ascended. The ladder was inside you all along.',
    baseOutput: 150,
    salaryPerOutput: 60,
    requirement: {
      resources: { reputation: 35000, salary: 1000000, politicalCapital: 1500 },
      skills: { strategicThinking: 15, networking: 14, corporateJargon: 12 },
    },
    perk: 'A golden parachute, just in case.',
  },
];

/** The highest reachable tier index. */
export const MAX_JOB_INDEX = JOBS.length - 1;
