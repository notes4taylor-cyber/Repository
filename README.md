# Prestige Packs

A single-player, fictional **CCG collecting simulator** built in **Godot 4**.
Open packs, chase grails, complete sets, grade cards, trade with NPC collectors,
and grow your **Prestige**. There is **no card battling** — this is a collecting
and economy game in the spirit of sports-card / TCG collecting, set in a wholly
fictional universe (no real IP, brands, grading companies, or card art).

> Status: **First playable / vertical slice.** Real systems, real state,
> save/load, and enough content to test the full loop. Not a finished game.

---

## Running the project

1. Install **Godot 4.2+** (standard, non-.NET build).
2. Open Godot, **Import** this folder (it contains `project.godot`).
3. Press **Play** (F5). The main scene is `res://src/ui/Main.tscn`.

From the command line:

```bash
godot --path . # opens the editor
godot          # run from inside the project folder
```

### Headless self-test (dev harness)

A scripted test exercises the full loop (buy → open → sell → grade → trade →
display → save/load → invariant checks → odds distribution):

```bash
godot --headless res://tools/SelfTest.tscn
```

It prints `PASS`/`FAIL` lines and exits non-zero if anything fails.

---

## The economy: Prestige

| Term | Abbr | Meaning |
|------|------|---------|
| Total Prestige | **P** | `P = PC + PL` |
| Prestige Collection | **PC** | Value locked in cards, sealed product, displayed items, badge bonuses. Not spendable. |
| Prestige Liquid | **PL** | Spendable currency for packs, singles, grading, trades. |

- **Buying** converts PL → sealed PC (P unchanged).
- **Opening** converts sealed PC → card PC based on what you pull (luck moves P).
- **Selling** converts a card's market value (PC) → PL (minus a vendor spread).
- A house edge on sealed product means buying-then-dumping is never a guaranteed
  profit, so you can't money-pump PL.

---

## Implemented systems

- **Main menu**: New Game, Continue, inline Settings, Quit, build label.
- **Save/Load**: versioned local JSON (`user://prestige_packs_save.json`),
  autosave after major actions, manual save, delete-with-confirmation, and a
  migration hook. RNG state is persisted so reloading can't reroll luck.
- **Shop**: 6 product tiers per set (Pack, 3-Pack Bundle, Blaster, Booster Box,
  Collector Box, Sealed Case) with data-driven pricing/odds. Buy to keep sealed
  or **Buy & Open**.
- **Season 1**: 8 fictional sets, each with a **procedurally generated** checklist
  (~700+ cards total), deterministic from a content seed.
- **Rarities**: Common, Uncommon, Rare, Legendary, plus Serialized & 1-of-1
  (achieved via chase variants).
- **Variants**: Base, Holo, Rainbow, Gold, Shadow, Signature, Serialized, 1-of-1.
  Serialized cards get real serial numbers (e.g. `014/100`); **1-of-1s are unique
  per save** and never reappear once pulled (even if sold).
- **Pack opening**: reveal one-by-one, reveal all, or skip to summary; grail
  pulls get stronger treatment; new-vs-duplicate and value shown.
- **Card condition** on pull (Damaged → Gem Candidate), affecting value & grading.
- **Collection binder**: search, filter (set/rarity/variant/owned/graded), sort
  (value/rarity/number/qty/condition/grade/newest), per-card details dialog with
  **instance-level** sell/grade/display so the correct copy is always acted on,
  "sell all duplicates (keep best copy)", and set completion %.
- **Grading**: one fictional grader (*Prestige Grading Co.*), fee, 1–10 grade
  biased by condition (10 is rare), value recalculated, confirmation on
  high-value cards.
- **Market**: NPC-driven demand & hype trends for factions / sets / variants that
  rise and decay over time and feed the value formula.
- **NPC trades**: 8 collector archetypes with distinct tastes make offers
  (want one of your items, give PL/sealed/cards), with value comparison and
  high-value confirmation. NPC-given cards are never unique, so constraints hold.
- **Badges**: per-set Bronze/Silver/Gold/Diamond/Black/Mythic tiers that grant PC
  bonuses and feed reputation.
- **Reputation**: 9 collector categories with tiers and a dynamic title.
- **Display room**: featured card, on-display slots (unlocked by Prestige
  milestones, granting PC bonus), top 5, rarest pull, sealed shelf, favorite
  badge.
- **Achievements**: 12 internal milestones (event- and stat-driven).
- **Progression**: in-game days; market & trades refresh over time / on
  "Advance Day".
- **Debug panel** (toggle with **F1**): add PL, generate/open packs, simulate
  10k variant rolls, force Legendary/Serialized/1-of-1, complete a set, reset
  market, recalc prestige, validate save / unique constraints / balance tables.

---

## Architecture

Data-driven, manager-based. UI never mutates complex state directly — it calls
manager methods, which emit signals that refresh the UI.

```
src/core/
  Enums.gd            # rarities, variants, conditions + labels/colors
  Balance.gd      (autoload) ALL tunable numbers & odds tables
  RNGService.gd   (autoload) seeded gameplay + deterministic content RNG
  ContentDB.gd    (autoload) generates & stores sets/cards/products
  Game.gd         (autoload) central player state + economy actions (+ debug)
  SaveManager.gd  (autoload) versioned JSON save/load + validators
src/data/
  CardDefinition / SetDefinition / ProductDefinition / CardInstance
src/managers/   (autoloads)
  PrestigeCalc / PackEngine / Market / Grading / Badges / Reputation /
  Achievements / Trades
src/ui/
  Main.tscn + Main.gd            # nav, header, toasts, confirmations
  UI.gd / ScreenBase.gd          # shared widget helpers + screen base
  screens/*.gd                   # one file per screen, built in code
tools/
  SelfTest.tscn + SelfTest.gd    # headless loop test
```

Key rules followed: one **PrestigeCalc** owns all value/Prestige math (consistent
across every screen); odds live only in **Balance**; serialized/1-of-1 uniqueness
is reserved through **Game** ledgers; every owned card is a tracked
**CardInstance** so the wrong duplicate is never destroyed.

---

## Where to tune balance

Everything lives in **`src/core/Balance.gd`**:

- Starting PL, sell spread, sealed factor, high-value confirm threshold.
- `VARIANT_ODDS`, `RARITY_PICK_WEIGHT`, `CONDITION_ODDS` (validated to sum to 1.0).
- Value multipliers: rarity / variant / condition / grade, demand & hype ranges,
  age, serial-quality.
- Grading fee + condition→grade means.
- Market trend counts/boosts/decay.
- Product markup per kind + `MARKET_EV_FACTOR` (drives shop prices).
- Set sizes, rarity split, base-value ranges, serial print runs.
- Badge thresholds + PC bonuses, display slots/milestones/bonus.

Content generation seed: `Balance.CONTENT_SEED`.

---

## Known limitations / stubs

- **No final art / audio**: placeholder card frames (color-coded), no SFX.
- **Opening granularity**: a box opens as one unit (all its packs at once) rather
  than pack-by-pack within the box. Reveal pacing is per-card.
- Pack reveal caps drawn tiles at 60 for big products (the rest are still added
  to the collection and counted in the summary).
- Collection/grading lists cap rendered rows for performance; use filters.
- Grading resolves instantly (no simulated delay).
- Market is intentionally simple (random faction/set/variant trends with decay).
- NPC trades request a single player item per offer.
- Prestige recomputes from scratch (fine for thousands of cards; not optimized
  for tens of thousands).

---

## Suggested next features

- Pack-by-pack box opening with animation/SFX and a proper reveal sequence.
- Cached/incremental Prestige & badge computation for very large collections.
- Richer market (event chains, set rotations, demand tied to your own selling).
- Multi-item NPC trades + a counter-offer flow.
- More sets/seasons, alternate art templates, and an in-game checklist export.
- Steam-style achievements, statistics, and onboarding tutorial.

---

## Testing checklist (acceptance)

Launch → New Game → see P/PC/PL → Shop: buy a pack → Open Packs: reveal → cards
appear in Collection → see duplicates → sell a card (PC/PL/P update) → grade a
card and get a 1–10 result → Sets & Badges shows completion progress → Trades:
accept/decline an offer → Display Room: feature a card → Settings: Save, reload
via Continue and confirm nothing is lost. All of the above is also asserted by
`tools/SelfTest.tscn`.
