/**
 * resources.ts
 * ------------
 * Pure DATA: the six resources the game tracks. Add a new resource by adding
 * an entry here (and to the `ResourceId` union in types.ts). The UI renders
 * whatever is in `RESOURCES`, so no component changes are required.
 */
import type { ResourceDef, ResourceId } from '../types';

export const RESOURCES: ResourceDef[] = [
  {
    id: 'salary',
    name: 'Salary',
    icon: '💵',
    description: 'Your accumulated compensation. The whole point. Allegedly.',
    initial: 0,
    format: 'currency',
    color: '#34d399',
  },
  {
    id: 'workOutput',
    name: 'Work Output',
    icon: '📈',
    description: 'Raw productivity generated over time. Converts into salary.',
    initial: 0,
    format: 'number',
    color: '#60a5fa',
  },
  {
    id: 'reputation',
    name: 'Reputation',
    icon: '⭐',
    description: 'How much the company *thinks* you matter. Gates promotions.',
    initial: 0,
    format: 'number',
    color: '#fbbf24',
  },
  {
    id: 'politicalCapital',
    name: 'Political Capital',
    icon: '🤝',
    description: 'Favors, alliances, and knowing where the bodies are buried.',
    initial: 0,
    format: 'number',
    color: '#a78bfa',
  },
  {
    id: 'energy',
    name: 'Energy',
    icon: '🔋',
    description: 'Spent to start tasks. Regenerates slowly while you exist.',
    initial: 100,
    max: 100,
    format: 'percent',
    color: '#22d3ee',
  },
  {
    id: 'burnout',
    name: 'Burnout',
    icon: '🔥',
    description: 'The silent productivity killer. High burnout tanks your output.',
    initial: 0,
    max: 100,
    format: 'percent',
    color: '#f87171',
  },
];

/** Quick lookup map: `RESOURCE_MAP.salary` -> the Salary definition. */
export const RESOURCE_MAP: Record<ResourceId, ResourceDef> = Object.fromEntries(
  RESOURCES.map((r) => [r.id, r]),
) as Record<ResourceId, ResourceDef>;
