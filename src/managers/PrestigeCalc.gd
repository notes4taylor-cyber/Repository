extends Node
## PrestigeCalc (autoload)
## THE single place market value & Prestige are computed. Every screen reads
## value from here so PC/PL/P are always consistent.

## Market value (in PL) of one owned card instance.
func card_value(inst: CardInstance) -> float:
	var def := ContentDB.get_card(inst.card_id)
	if def == null:
		return 0.0
	var v := def.base_value
	v *= Balance.RARITY_VALUE_MULT[def.rarity]
	v *= Balance.VARIANT_VALUE_MULT[inst.variant]
	v *= Balance.CONDITION_VALUE_MULT[inst.condition]

	# Grade vs raw.
	if inst.graded and inst.grade >= 1 and inst.grade <= 10:
		v *= Balance.GRADE_VALUE_MULT[inst.grade]
	else:
		v *= Balance.RAW_VALUE_MULT

	# Market demand & hype.
	v *= _lerp_range(Balance.DEMAND_VALUE_RANGE, Market.demand_for(def))
	v *= _lerp_range(Balance.HYPE_VALUE_RANGE, Market.hype_for(def, inst.variant))

	# Set age.
	v *= age_mult_for_set(def.set_id)
	v *= def.age_modifier

	# Serialized quality (low numbers worth more); 1/1 uniqueness already in mults.
	if inst.variant == Enums.Variant.SERIALIZED and inst.serial_max > 0:
		var quality := 1.0 - (float(inst.serial_index - 1) / float(maxi(1, inst.serial_max)))
		v *= 1.0 + Balance.SERIAL_LOW_BONUS * quality

	return snappedf(maxf(v, 0.5), 0.5)

## Value a card *would* fetch when sold (after vendor spread).
func sell_value(inst: CardInstance) -> float:
	return snappedf(card_value(inst) * Balance.SELL_FACTOR, 0.5)

func age_mult_for_set(set_id: String) -> float:
	var set_def := ContentDB.get_set(set_id)
	if set_def == null:
		return 1.0
	var age_days: int = maxi(0, Game.day - set_def.release_day)
	return 1.0 + minf(Balance.AGE_VALUE_MAX, age_days * Balance.AGE_VALUE_PER_DAY)

func _lerp_range(r: Vector2, t: float) -> float:
	return lerpf(r.x, r.y, clampf(t, 0.0, 1.0))

# ---------------------------------------------------------------------------
# Aggregate Prestige
# ---------------------------------------------------------------------------
## Prestige Collection = value locked in cards + sealed product + display/badge bonuses.
func collection_prestige() -> float:
	var total := 0.0
	for inst in Game.collection:
		total += card_value(inst)
	total += sealed_prestige()
	total += Game.display_bonus_pc()
	total += Badges.total_badge_pc_bonus()
	return total

func sealed_prestige() -> float:
	var total := 0.0
	for product_id in Game.sealed_inventory.keys():
		var prod := ContentDB.get_product(product_id)
		if prod == null:
			continue
		total += prod.price * Balance.SEALED_PC_FACTOR * Game.sealed_inventory[product_id]
	return total

func total_prestige() -> float:
	return collection_prestige() + Game.pl
