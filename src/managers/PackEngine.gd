extends Node
## PackEngine (autoload)
## Generates card pulls: variant roll, card selection, condition, and reserves
## serialized numbers / 1-of-1 uniqueness through Game. Pure pull logic lives
## here; economy (PL/PC) is handled by Game.open_product.

## Generate `count` pulls from a set. Instances are fully built (uid + serial
## assigned, uniqueness reserved) but NOT yet added to the collection — the
## caller commits them so reveal UI can show them first.
func generate_pulls(set_id: String, count: int, luck: float) -> Array:
	var out: Array = []
	for _i in range(count):
		out.append(_generate_one(set_id, luck))
	return out

func _generate_one(set_id: String, luck: float) -> CardInstance:
	var set_def := ContentDB.get_set(set_id)
	var variant := _roll_variant(luck)
	var inst := CardInstance.new()
	inst.uid = Game.next_uid()
	inst.acquired_seq = Game.next_acquired_seq()
	inst.condition = _roll_condition()

	match variant:
		Enums.Variant.ONEOFONE:
			var cid := _pick_oneofone_card(set_def)
			if cid == "":
				# No 1/1 left in this set -> downgrade to a Signature chase.
				variant = Enums.Variant.SIGNATURE
				inst.card_id = _pick_card_for_variant(set_def, variant)
			else:
				inst.card_id = cid
				Game.reserve_oneofone(cid)
				inst.serial_index = 1
				inst.serial_max = 1
		Enums.Variant.SERIALIZED:
			var res := _pick_serialized_card(set_def)
			if res.is_empty():
				variant = Enums.Variant.GOLD
				inst.card_id = _pick_card_for_variant(set_def, variant)
			else:
				inst.card_id = res["card_id"]
				inst.serial_index = res["serial_index"]
				inst.serial_max = res["serial_max"]
		_:
			inst.card_id = _pick_card_for_variant(set_def, variant)

	inst.variant = variant
	return inst

# ---------------------------------------------------------------------------
# Variant roll (luck boosts the rarer finishes, then re-normalize).
# ---------------------------------------------------------------------------
func _roll_variant(luck: float) -> int:
	var weights := {}
	for v in Balance.VARIANT_ODDS.keys():
		var w: float = Balance.VARIANT_ODDS[v]
		if v >= Enums.Variant.RAINBOW:
			w *= luck
		weights[v] = w
	return RNGService.weighted_pick(weights)

func _roll_condition() -> int:
	return RNGService.weighted_pick(Balance.CONDITION_ODDS)

# ---------------------------------------------------------------------------
# Card selection
# ---------------------------------------------------------------------------
func _pick_card_for_variant(set_def: SetDefinition, variant: int) -> String:
	var weights := {}
	for cid in set_def.card_ids:
		var def: CardDefinition = ContentDB.get_card(cid)
		if def.available_variants.has(variant):
			weights[cid] = Balance.RARITY_PICK_WEIGHT.get(def.rarity, 1.0)
	if weights.is_empty():
		# Fallback: any card in base/holo terms.
		for cid in set_def.card_ids:
			var def2: CardDefinition = ContentDB.get_card(cid)
			weights[cid] = Balance.RARITY_PICK_WEIGHT.get(def2.rarity, 1.0)
	return RNGService.weighted_pick(weights)

func _pick_oneofone_card(set_def: SetDefinition) -> String:
	var candidates: Array = []
	for cid in set_def.card_ids:
		var def: CardDefinition = ContentDB.get_card(cid)
		if def.can_be_oneofone() and not Game.is_oneofone_taken(cid):
			candidates.append(cid)
	if candidates.is_empty():
		return ""
	return candidates[RNGService.randi_range(0, candidates.size() - 1)]

func _pick_serialized_card(set_def: SetDefinition) -> Dictionary:
	var candidates: Array = []
	for cid in set_def.card_ids:
		var def: CardDefinition = ContentDB.get_card(cid)
		if def.can_be_serialized() and def.serial_run > 0:
			if Game.serials_remaining(cid, def.serial_run) > 0:
				candidates.append(cid)
	if candidates.is_empty():
		return {}
	var card_id: String = candidates[RNGService.randi_range(0, candidates.size() - 1)]
	var def := ContentDB.get_card(card_id)
	var idx := Game.reserve_serial(card_id, def.serial_run)
	if idx <= 0:
		return {}
	return {"card_id": card_id, "serial_index": idx, "serial_max": def.serial_run}

# ---------------------------------------------------------------------------
# Debug / analysis: simulate many pulls without mutating state.
# Returns a distribution report Dictionary.
# ---------------------------------------------------------------------------
func simulate_distribution(samples: int, luck: float = 1.0) -> Dictionary:
	var variant_counts := {}
	for v in Balance.VARIANT_ODDS.keys():
		variant_counts[v] = 0
	for _i in range(samples):
		variant_counts[_roll_variant(luck)] += 1
	return {"samples": samples, "luck": luck, "variants": variant_counts}
