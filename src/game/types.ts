/**
 * types.ts
 * ---------
 * Central type definitions for Corporate Climber Idle.
 *
 * Everything in the game is described by these interfaces. Game *data*
 * (the actual tasks, skills, jobs, etc.) lives in `src/game/data/` and is
 * typed against these interfaces. Game *logic* lives in `src/game/engine/`.
 * The UI never invents its own shapes — it consumes these types.
 *
 * Keeping IDs as string-literal unions (instead of plain `string`) means the
 * TypeScript compiler will catch typos like `'workOutpt'` for you.
 */

/* ------------------------------------------------------------------ */
/* Resources                                                          */
/* ------------------------------------------------------------------ */

export type ResourceId =
  | 'salary'
  | 'workOutput'
  | 'reputation'
  | 'politicalCapital'
  | 'burnout'
  | 'energy';

export type ResourceFormat = 'number' | 'currency' | 'percent';

export interface ResourceDef {
  id: ResourceId;
  name: string;
  /** A short emoji used as a lightweight, zero-asset icon. */
  icon: string;
  description: string;
  /** Starting value when a new game begins. */
  initial: number;
  /** Optional hard cap (e.g. Energy and Burnout are capped at 100). */
  max?: number;
  /** How the number should be rendered in the UI. */
  format: ResourceFormat;
  /** CSS color used for the resource's accent / progress bar. */
  color: string;
}

/* ------------------------------------------------------------------ */
/* Skills                                                             */
/* ------------------------------------------------------------------ */

export type SkillId =
  | 'emailEfficiency'
  | 'spreadsheetMastery'
  | 'meetingEndurance'
  | 'networking'
  | 'corporateJargon'
  | 'strategicThinking';

export interface SkillDef {
  id: SkillId;
  name: string;
  icon: string;
  description: string;
  /** XP required to go from level 1 -> 2. */
  baseXpToLevel: number;
  /** Each subsequent level costs `previousCost * xpGrowth`. */
  xpGrowth: number;
  /**
   * Each level of this skill adds this fraction to *global* output.
   * e.g. 0.03 means "+3% Work Output per level".
   */
  outputBonusPerLevel: number;
}

/** Per-skill mutable save data. */
export interface SkillState {
  level: number;
  xp: number;
}

/* ------------------------------------------------------------------ */
/* Tasks                                                              */
/* ------------------------------------------------------------------ */

export type TaskId =
  | 'answerEmails'
  | 'attendMeeting'
  | 'buildSpreadsheet'
  | 'writeStatusReport'
  | 'networkWithManager'
  | 'completeTraining'
  | 'createPowerpoint'
  | 'pretendToBeBusy';

/** What a single completed task cycle pays out. */
export interface TaskReward {
  /** Flat resource amounts (positive = gain). */
  resources?: Partial<Record<ResourceId, number>>;
  /** XP granted to one or more skills. */
  skillXp?: Partial<Record<SkillId, number>>;
}

/** Conditions under which a task becomes available. */
export interface TaskRequirement {
  /** Minimum job tier index (see jobs.ts). 0 = available from the start. */
  minJobLevel?: number;
  /** Requires a particular skill at a particular level. */
  skill?: { id: SkillId; level: number };
}

export interface TaskDef {
  id: TaskId;
  name: string;
  description: string;
  /** Seconds for one cycle of the task to complete. */
  duration: number;
  /** Energy spent up-front when a cycle starts. */
  energyCost: number;
  /** Burnout added when a cycle completes. */
  burnoutCost: number;
  /** Payout granted when a cycle completes. */
  rewards: TaskReward;
  /**
   * Optional skill whose level scales this task's resource rewards.
   * (Higher relevant skill -> bigger payouts.)
   */
  primarySkill?: SkillId;
  /** When the task unlocks. Omitted = always available. */
  requirement?: TaskRequirement;
}

/** Per-task mutable save data describing its live state. */
export interface TaskRuntime {
  /** Is a cycle currently in progress? */
  running: boolean;
  /** Cycle progress in the range [0, 1]. */
  progress: number;
  /** Auto-repeat: restart the cycle automatically when it finishes. */
  auto: boolean;
}

/* ------------------------------------------------------------------ */
/* Jobs / Promotions                                                  */
/* ------------------------------------------------------------------ */

export interface JobRequirement {
  /** Minimum resource totals needed to qualify (e.g. reputation, salary). */
  resources?: Partial<Record<ResourceId, number>>;
  /** Minimum skill levels needed to qualify. */
  skills?: Partial<Record<SkillId, number>>;
}

export interface JobDef {
  /** 0-based tier. Index in the JOBS array === career level. */
  level: number;
  title: string;
  description: string;
  /** Base Work Output generated per second at this tier (before bonuses). */
  baseOutput: number;
  /** Salary earned per unit of Work Output produced. Rises with promotions. */
  salaryPerOutput: number;
  /** What it takes to be promoted INTO this job from the previous one. */
  requirement?: JobRequirement;
  /** Flavorful note about perks unlocked at this tier. */
  perk?: string;
}

/* ------------------------------------------------------------------ */
/* Top-level game state (this is what gets saved to LocalStorage)     */
/* ------------------------------------------------------------------ */

export interface GameState {
  resources: Record<ResourceId, number>;
  skills: Record<SkillId, SkillState>;
  tasks: Record<TaskId, TaskRuntime>;
  /** Index into the JOBS array — the player's current career tier. */
  jobIndex: number;
  /** Timestamp (ms) of the last processed tick, used for offline progress. */
  lastTick: number;
  /** Total seconds played, just for fun stats. */
  totalPlayTime: number;
  /** Save-format version, so we can migrate/clear old incompatible saves. */
  version: number;
}
