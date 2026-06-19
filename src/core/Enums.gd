class_name Enums
extends RefCounted
## Central enum + label definitions for Prestige Packs.
## Use the static helpers so display strings live in exactly one place.

# Base checklist rarities. Serialized / OneOfOne are achieved via variants,
# but are also exposed here so a card's *effective* rarity can be reported.
enum Rarity { COMMON, UNCOMMON, RARE, LEGENDARY, SERIALIZED, ONEOFONE }

enum Variant { BASE, HOLO, RAINBOW, GOLD, SHADOW, SIGNATURE, SERIALIZED, ONEOFONE }

enum Condition { DAMAGED, PLAYED, EXCELLENT, NEAR_MINT, MINT, GEM_CANDIDATE }

const RARITY_NAMES := ["Common", "Uncommon", "Rare", "Legendary", "Serialized", "1-of-1"]
const VARIANT_NAMES := ["Base", "Holo", "Rainbow", "Gold", "Shadow", "Signature", "Serialized", "1-of-1"]
const CONDITION_NAMES := ["Damaged", "Played", "Excellent", "Near Mint", "Mint", "Gem Candidate"]

# Hex colors used for placeholder card frames / rarity accents.
const RARITY_COLORS := ["#9aa0b5", "#5bd16a", "#4aa8ff", "#c46bff", "#ff8a3d", "#ffd24a"]
const VARIANT_COLORS := ["#9aa0b5", "#6fd0ff", "#ff9ce0", "#ffd24a", "#7a6bff", "#ff7a7a", "#ff8a3d", "#ffd24a"]

static func rarity_name(r: int) -> String:
	return RARITY_NAMES[clampi(r, 0, RARITY_NAMES.size() - 1)]

static func variant_name(v: int) -> String:
	return VARIANT_NAMES[clampi(v, 0, VARIANT_NAMES.size() - 1)]

static func condition_name(c: int) -> String:
	return CONDITION_NAMES[clampi(c, 0, CONDITION_NAMES.size() - 1)]

static func rarity_color(r: int) -> Color:
	return Color(RARITY_COLORS[clampi(r, 0, RARITY_COLORS.size() - 1)])

static func variant_color(v: int) -> Color:
	return Color(VARIANT_COLORS[clampi(v, 0, VARIANT_COLORS.size() - 1)])

## A card pulled in the SERIALIZED or ONEOFONE variant outranks its base rarity.
static func effective_rarity(base_rarity: int, variant: int) -> int:
	if variant == Variant.ONEOFONE:
		return Rarity.ONEOFONE
	if variant == Variant.SERIALIZED:
		return Rarity.SERIALIZED
	return base_rarity

## Is this pull a "grail" worthy of strong visual treatment?
static func is_grail(base_rarity: int, variant: int) -> bool:
	var er := effective_rarity(base_rarity, variant)
	if er >= Rarity.LEGENDARY:
		return true
	return variant >= Variant.GOLD
