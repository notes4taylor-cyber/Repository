class_name CardDefinition
extends RefCounted
## Immutable definition of a card in the checklist (the "what exists").
## Runtime owned copies are CardInstance objects that point back here by id.

var id: String              # globally unique, e.g. "S1_ARC_017"
var set_id: String
var number: int             # card number within the set (1-based)
var name: String
var faction: String         # theme / faction, e.g. "Dragons"
var rarity: int             # Enums.Rarity (COMMON..LEGENDARY for base checklist)
var base_value: float       # baseline PL value before all multipliers
var demand_base: float      # 0..1 intrinsic collector demand
var hype_base: float        # 0..1 intrinsic hype
var age_modifier: float = 1.0   # static per-card age/scarcity nudge
var available_variants: Array = []  # Array[int] of Enums.Variant this card can appear in
var serial_run: int = 0         # print run size for the SERIALIZED variant (0 = none)

func can_be_serialized() -> bool:
	return available_variants.has(Enums.Variant.SERIALIZED)

func can_be_oneofone() -> bool:
	return available_variants.has(Enums.Variant.ONEOFONE)

func to_dict() -> Dictionary:
	return {
		"id": id, "set_id": set_id, "number": number, "name": name,
		"faction": faction, "rarity": rarity, "base_value": base_value,
		"demand_base": demand_base, "hype_base": hype_base,
		"age_modifier": age_modifier, "available_variants": available_variants,
	}
