# 🏢 Corporate Climber Idle

A satirical, browser-based **idle / progression game**. Start as an unpaid-in-spirit
Intern and claw your way to C-Suite Executive by answering emails, attending
meetings that could have been emails, building beautiful spreadsheets, and —
when all else fails — pretending to be busy.

This repository is an **MVP foundation**: a small, clean, fully-working game loop
built with a data-driven architecture so new content (tasks, skills, jobs,
resources) can be added with little or no new code.

> Built with React + TypeScript + Vite. No backend. Saves to your browser's
> LocalStorage.

---

## ▶️ Running it locally

You need [Node.js](https://nodejs.org/) 18+ installed.

```bash
# 1. Install dependencies
npm install

# 2. Start the dev server (hot-reloads as you edit)
npm run dev
# -> open the printed URL, usually http://localhost:5173

# 3. (Optional) Make a production build
npm run build      # type-checks + bundles into dist/
npm run preview    # serve the production build locally
```

That's it. The game auto-saves every few seconds and when you close the tab.

---

## 🎮 How to play

- **Tasks** generate resources. Click **Do it** to run a task once; it fills a
  progress bar and pays out when it completes. Toggle **Auto** to repeat it
  automatically while you have the energy.
- **Energy** (🔋) is spent to start tasks and regenerates over time.
- **Burnout** (🔥) goes up as you work and slowly recovers when you rest. High
  burnout tanks your **Efficiency**, which multiplies *all* production — so
  don't grind yourself into the ground.
- **Skills** level up automatically as tasks grant XP. Higher skills mean more
  **Work Output** (passive income) and bigger task payouts.
- **Work Output** (📈) is generated passively by your job + skills and converts
  into **Salary** (💵).
- **Promotions** unlock when you meet a role's requirements (reputation, salary,
  political capital, skill levels). Each promotion boosts your pay rate and
  unlocks new tasks.
- **Resign & Reset** wipes your save and starts over (with a confirmation).

The game also simulates **offline progress**: come back later and the machine
will have kept earning for you (capped at 8 hours).

---

## 🏗️ Architecture overview

The guiding principle is **strict separation of game DATA, game LOGIC, and UI**.

```
src/
├── main.tsx                 # React entry point
├── App.tsx                  # Page layout only — NO game logic
├── styles.css               # Global "corporate dashboard from hell" theme
│
├── game/                    # ── Everything non-visual lives here ──
│   ├── types.ts             # All TypeScript interfaces + ID unions
│   ├── format.ts            # Number/currency/time display helpers
│   ├── GameContext.tsx      # React bridge: runs the tick, autosaves, exposes actions
│   │
│   ├── data/                # ── Pure DATA. Tweak these to add content. ──
│   │   ├── resources.ts     #   the 6 resources
│   │   ├── skills.ts        #   the 6 skills
│   │   ├── tasks.ts         #   the 8 tasks   <-- you'll edit this most
│   │   └── jobs.ts          #   the 10-tier career ladder
│   │
│   └── engine/              # ── Pure LOGIC. No React in here. ──
│       ├── state.ts         #   fresh-game factory + resource clamping
│       ├── tick.ts          #   THE game loop (passive gen, tasks, burnout)
│       ├── skills.ts        #   XP/leveling math + output bonuses
│       ├── tasks.ts         #   start task / unlock checks
│       ├── promotions.ts    #   requirement checks + promote
│       └── save.ts          #   LocalStorage save/load + offline catch-up
│
└── components/              # ── Dumb, presentational React components ──
    ├── Header.tsx           #   title, current job, efficiency, reset
    ├── ResourcePanel.tsx    #   the top strip of resource counters
    ├── TaskCard.tsx / TaskList.tsx
    ├── SkillList.tsx
    ├── PromotionPanel.tsx
    └── ProgressBar.tsx      #   reusable bar
```

### The core systems

| System | Where | What it does |
|---|---|---|
| **Resources** | `data/resources.ts` | Declarative list of every resource and how it's displayed. |
| **Skills** | `data/skills.ts` + `engine/skills.ts` | Data declares XP curves & bonuses; engine does the leveling math. |
| **Tasks** | `data/tasks.ts` + `engine/tasks.ts` | Data declares cost/reward/unlock; engine handles starting/unlocking. |
| **Promotions** | `data/jobs.ts` + `engine/promotions.ts` | Data declares the ladder & requirements; engine evaluates eligibility. |
| **Game tick** | `engine/tick.ts` | A **pure function** `tick(state, dt)` that advances the whole world. |
| **Save/Load** | `engine/save.ts` | Serializes `GameState` to LocalStorage; applies offline progress on load. |
| **React glue** | `GameContext.tsx` | Runs the tick on an interval, autosaves, exposes actions via `useGame()`. |

### The data flow (one direction)

```
   data/* (content)  ─┐
                      ├─►  engine/* (pure logic)  ─►  GameContext  ─►  components/* (UI)
   GameState ─────────┘            ▲                                        │
                                   └──────────── player actions ◄───────────┘
```

Components **never** mutate state directly — they call actions from
`useGame()`, which run pure engine functions that return a *new* `GameState`.

---

## ➕ How to extend it (recipes)

Because the game is data-driven, most additions are just edits to `data/`:

**Add a new task**
1. Add its id to the `TaskId` union in `types.ts`.
2. Add an entry to the `TASKS` array in `data/tasks.ts` (name, duration, costs,
   rewards, optional `requirement`).
3. Done — it appears in the UI automatically, locked until its requirement is met.

**Add a new skill** → add its id to `SkillId`, add an entry to `SKILLS`. It will
start at level 1 in every new save and auto-render.

**Add a new job tier** → add an entry to `JOBS` (the array order is the ladder)
with its `requirement`. The promotion panel picks it up automatically.

**Add a new resource** → add its id to `ResourceId` and an entry to `RESOURCES`.

**Tune the balance** → numbers like energy regen, burnout decay, and the
burnout→efficiency curve live as named constants at the top of `engine/tick.ts`.

> Save format note: `GameState` is versioned (`SAVE_VERSION` in `engine/state.ts`).
> Old saves are merged onto a fresh state, so *adding* content is safe. If you
> make an incompatible change, bump `SAVE_VERSION` to retire old saves cleanly.

---

## 🧭 What was built (MVP scope)

✅ Working game screen & corporate-dashboard UI (responsive / mobile-friendly)
✅ Resource display with live per-second rates
✅ Clickable tasks with progress bars + auto-repeat
✅ Passive idle generation (Work Output → Salary)
✅ Automatic skill leveling with XP curves
✅ 10-tier promotion system with live requirement checklists
✅ Burnout → efficiency penalty system
✅ LocalStorage save/load + offline progress + reset button
✅ Pure-function game tick
✅ Fully data-driven content (tasks/skills/jobs/resources)

## 🔜 Suggested next milestone

1. **Upgrades / shop** — spend Salary or Political Capital on permanent
   multipliers (e.g. "Ergonomic Chair: +10% energy regen"). The data/engine
   split makes this a natural next `data/upgrades.ts` + `engine/upgrades.ts`.
2. **Random office events** — satirical pop-ups ("Reorg!", "Free pizza in the
   break room") that grant or drain resources, adding variety to the idle loop.
3. **Prestige layer** — "Quit and join a startup" to reset for a permanent
   meta-currency, the classic idle-game long-term hook.
4. **Light testing** — `tick.ts` and the engine are pure functions; add Vitest
   unit tests to lock in game balance as content grows.

---

*Corporate Climber Idle is a parody. Any resemblance to your actual job is
purely coincidental and also we're very sorry.*
