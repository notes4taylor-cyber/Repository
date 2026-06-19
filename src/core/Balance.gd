extends Node
## Balance (autoload singleton)
## Single source of truth for every tunable number in the game.
## Designers tune the game here; nothing else should hardcode economy values.

# Preloaded so the enum values are available as constant expressions while this
# autoload's const tables are evaluated (global class_name may not be registered
# this early during project load).
const Enums = preload("res://src/core/Enums.gd")

# ---------------------------------------------------------------------------
# Economy
# ---------------------------------------------------------------------------
const STARTING_PL: float = 1500.0

## When you sell a card you receive market value * SELL_FACTOR (vendor spread).
const SELL_FACTOR: float = 0.90

## Sealed product's locked PC value = purchase price * SEALED_PC_FACTOR.
const SEALED_PC_FACTOR: float = 1.0

## Confirmation required before selling/trading items worth at least this much PL.
const HIGH_VALUE_THRESHOLD: float = 250.0

## Average demand*hype*age multiplier, used ONLY to price product realistically
## (so packs aren't priced off the rare-heavy checklist average). Tunable.
const MARKET_EV_FACTOR: float = 1.45

## House edge per product kind. Must stay above SELL_FACTOR so buying then
## selling everything can never be a guaranteed-profit money pump.
const PRODUCT_MARKUP := {
	"pack": 1.10, "bundle": 1.08, "blaster": 1.06,
	"booster_box": 1.05, "collector_box": 1.25, "case": 1.03,
}

# ---------------------------------------------------------------------------
# Variant pull odds (MUST sum to 1.0 — validated at startup).
# ---------------------------------------------------------------------------
const VARIANT_ODDS := {
	Enums.Variant.BASE: 0.7000,
	Enums.Variant.HOLO: 0.1800,
	Enums.Variant.RAINBOW: 0.0600,
	Enums.Variant.GOLD: 0.0350,
	Enums.Variant.SHADOW: 0.0180,
	Enums.Variant.SIGNATURE: 0.0050,
	Enums.Variant.SERIALIZED: 0.0018,
	Enums.Variant.ONEOFONE: 0.0002,
}

## Selection weight for "which base card" when the finish is a common variant.
## Rarer cards are less likely to be the chosen card.
const RARITY_PICK_WEIGHT := {
	Enums.Rarity.COMMON: 1000.0,
	Enums.Rarity.UNCOMMON: 380.0,
	Enums.Rarity.RARE: 110.0,
	Enums.Rarity.LEGENDARY: 22.0,
}

## Value multiplier from the card's base rarity.
const RARITY_VALUE_MULT := {
	Enums.Rarity.COMMON: 1.0,
	Enums.Rarity.UNCOMMON: 2.2,
	Enums.Rarity.RARE: 6.0,
	Enums.Rarity.LEGENDARY: 22.0,
	Enums.Rarity.SERIALIZED: 60.0,
	Enums.Rarity.ONEOFONE: 250.0,
}

## Value multiplier from the finish/variant.
const VARIANT_VALUE_MULT := {
	Enums.Variant.BASE: 1.0,
	Enums.Variant.HOLO: 1.8,
	Enums.Variant.RAINBOW: 3.2,
	Enums.Variant.GOLD: 5.0,
	Enums.Variant.SHADOW: 7.5,
	Enums.Variant.SIGNATURE: 12.0,
	Enums.Variant.SERIALIZED: 28.0,
	Enums.Variant.ONEOFONE: 140.0,
}

# ---------------------------------------------------------------------------
# Condition
# ---------------------------------------------------------------------------
const CONDITION_ODDS := {
	Enums.Condition.DAMAGED: 0.02,
	Enums.Condition.PLAYED: 0.08,
	Enums.Condition.EXCELLENT: 0.30,
	Enums.Condition.NEAR_MINT: 0.35,
	Enums.Condition.MINT: 0.20,
	Enums.Condition.GEM_CANDIDATE: 0.05,
}

const CONDITION_VALUE_MULT := {
	Enums.Condition.DAMAGED: 0.35,
	Enums.Condition.PLAYED: 0.6,
	Enums.Condition.EXCELLENT: 0.85,
	Enums.Condition.NEAR_MINT: 1.0,
	Enums.Condition.MINT: 1.15,
	Enums.Condition.GEM_CANDIDATE: 1.35,
}

## Mean grade a raw card of each condition tends to receive (sampled with noise).
const CONDITION_GRADE_MEAN := {
	Enums.Condition.DAMAGED: 3.0,
	Enums.Condition.PLAYED: 5.0,
	Enums.Condition.EXCELLENT: 7.0,
	Enums.Condition.NEAR_MINT: 8.2,
	Enums.Condition.MINT: 9.0,
	Enums.Condition.GEM_CANDIDATE: 9.6,
}
const GRADE_NOISE: float = 1.1   # std-dev-ish spread on grading rolls

# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------
const GRADER_NAME: String = "Prestige Grading Co."
const GRADING_FEE: float = 60.0
const GRADING_DELAY_ACTIONS: int = 0   # 0 = instant result (MVP)

## Graded value multiplier by grade (1..10). Index 0 unused.
const GRADE_VALUE_MULT := [0.0, 0.4, 0.5, 0.6, 0.75, 0.9, 1.1, 1.4, 1.9, 2.8, 4.5]
## Raw (ungraded) baseline multiplier for comparison vs graded.
const RAW_VALUE_MULT: float = 1.0

# ---------------------------------------------------------------------------
# Market / demand / hype
# ---------------------------------------------------------------------------
## Demand & hype each scale value within these bounds.
const DEMAND_VALUE_RANGE := Vector2(0.7, 1.6)   # maps demand 0..1
const HYPE_VALUE_RANGE := Vector2(0.85, 1.8)    # maps hype 0..1
## How strongly an active trend boosts the affected demand/hype (additive 0..1).
const TREND_BOOST: float = 0.45
const TREND_COOL: float = 0.30
## Number of active "hot" trends after each refresh.
const MARKET_TRENDS_PER_REFRESH: int = 3
## Each day, hype values drift back toward base by this fraction.
const HYPE_DECAY: float = 0.25

# ---------------------------------------------------------------------------
# Age (older sets are worth slightly more)
# ---------------------------------------------------------------------------
const AGE_VALUE_PER_DAY: float = 0.01    # +1% value per in-game day of age
const AGE_VALUE_MAX: float = 0.5         # capped at +50%

# ---------------------------------------------------------------------------
# Serialized quality (lower serial numbers are worth more)
# ---------------------------------------------------------------------------
const SERIAL_LOW_BONUS: float = 0.8      # extra multiplier for #1, fades to 0

# ---------------------------------------------------------------------------
# Display room
# ---------------------------------------------------------------------------
const DISPLAY_BASE_SLOTS: int = 3
## Each milestone (in total P) unlocks another display slot.
const DISPLAY_SLOT_MILESTONES := [5000.0, 20000.0, 60000.0, 150000.0, 400000.0]
## Displayed item grants this fraction of its value as a PC bonus.
const DISPLAY_PC_BONUS: float = 0.05

# ---------------------------------------------------------------------------
# Content generation
# ---------------------------------------------------------------------------
const CONTENT_SEED: int = 20240131   # deterministic checklist generation
const SET_BASE_SIZE: int = 84        # cards per set baseline (+ index growth)
const SET_SIZE_GROWTH: int = 6       # extra cards per later set

# Per-set rarity split (fractions of the checklist).
const SET_RARITY_SPLIT := {
	Enums.Rarity.COMMON: 0.58,
	Enums.Rarity.UNCOMMON: 0.27,
	Enums.Rarity.RARE: 0.12,
	Enums.Rarity.LEGENDARY: 0.03,
}

# Base value ranges per rarity (pre-multiplier).
const RARITY_BASE_VALUE := {
	Enums.Rarity.COMMON: Vector2(2.0, 5.0),
	Enums.Rarity.UNCOMMON: Vector2(5.0, 12.0),
	Enums.Rarity.RARE: Vector2(12.0, 30.0),
	Enums.Rarity.LEGENDARY: Vector2(40.0, 90.0),
}

# Serial print runs available for serialized cards (chosen per card).
const SERIAL_RUNS := [10, 25, 50, 99, 100, 150, 250]

# ---------------------------------------------------------------------------
# Badges (set completion thresholds)
# ---------------------------------------------------------------------------
const BADGE_BRONZE: float = 0.25
const BADGE_SILVER: float = 0.50
const BADGE_GOLD: float = 0.75
const BADGE_DIAMOND: float = 1.0    # 100% base checklist
# Black = 100% base + own Holo-or-better of every card.
# Mythic = Black + own a grade >= MYTHIC_GRADE copy of every card.
const MYTHIC_GRADE: int = 9
## Flat Prestige (PC) bonus per badge tier earned, summed across sets.
const BADGE_PC_BONUS := {
	"bronze": 50.0, "silver": 150.0, "gold": 400.0,
	"diamond": 1200.0, "black": 4000.0, "mythic": 12000.0,
}

# ---------------------------------------------------------------------------
# Validation helper (called by ContentDB at startup / debug panel)
# ---------------------------------------------------------------------------
func validate() -> Array:
	var problems: Array = []
	var s := 0.0
	for v in VARIANT_ODDS.values():
		s += v
	if abs(s - 1.0) > 0.0001:
		problems.append("VARIANT_ODDS sum to %f (expected 1.0)" % s)
	var cs := 0.0
	for v in CONDITION_ODDS.values():
		cs += v
	if abs(cs - 1.0) > 0.0001:
		problems.append("CONDITION_ODDS sum to %f (expected 1.0)" % cs)
	var rs := 0.0
	for v in SET_RARITY_SPLIT.values():
		rs += v
	if abs(rs - 1.0) > 0.0001:
		problems.append("SET_RARITY_SPLIT sums to %f (expected 1.0)" % rs)
	return problems
