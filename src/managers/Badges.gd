extends Node
## Badges (autoload)
## Computes set-completion badges from the live collection (derived state, not
## stored). Tiers: bronze/silver/gold (base %), diamond (100% base),
## black (100% base + Holo-or-better of every card), mythic (+ high grade).

const TIER_ORDER := ["bronze", "silver", "gold", "diamond", "black", "mythic"]

## Returns a report for one set.
func set_report(set_id: String) -> Dictionary:
	var set_def := ContentDB.get_set(set_id)
	var total := set_def.size()
	var owned_base := {}     # card_id -> true (any variant owned)
	var owned_holo := {}     # card_id -> true (holo-or-better owned)
	var owned_mythic := {}   # card_id -> true (grade >= MYTHIC_GRADE owned)

	for inst in Game.collection:
		var def := ContentDB.get_card(inst.card_id)
		if def == null or def.set_id != set_id:
			continue
		owned_base[inst.card_id] = true
		if inst.variant >= Enums.Variant.HOLO:
			owned_holo[inst.card_id] = true
		if inst.graded and inst.grade >= Balance.MYTHIC_GRADE:
			owned_mythic[inst.card_id] = true

	var base_pct := float(owned_base.size()) / maxf(1.0, total)
	var holo_pct := float(owned_holo.size()) / maxf(1.0, total)
	var mythic_pct := float(owned_mythic.size()) / maxf(1.0, total)

	var tiers := {
		"bronze": base_pct >= Balance.BADGE_BRONZE,
		"silver": base_pct >= Balance.BADGE_SILVER,
		"gold": base_pct >= Balance.BADGE_GOLD,
		"diamond": base_pct >= Balance.BADGE_DIAMOND,
		"black": base_pct >= 1.0 and holo_pct >= 1.0,
		"mythic": base_pct >= 1.0 and holo_pct >= 1.0 and mythic_pct >= 1.0,
	}
	return {
		"set_id": set_id, "total": total,
		"base_owned": owned_base.size(), "base_pct": base_pct,
		"holo_owned": owned_holo.size(), "holo_pct": holo_pct,
		"mythic_owned": owned_mythic.size(), "mythic_pct": mythic_pct,
		"tiers": tiers,
	}

func highest_tier(set_id: String) -> String:
	var rep := set_report(set_id)
	var best := ""
	for t in TIER_ORDER:
		if rep["tiers"][t]:
			best = t
	return best

func earned_tiers(set_id: String) -> Array:
	var rep := set_report(set_id)
	var out: Array = []
	for t in TIER_ORDER:
		if rep["tiers"][t]:
			out.append(t)
	return out

## Total PC bonus from every badge earned across all sets.
func total_badge_pc_bonus() -> float:
	var total := 0.0
	for set_id in ContentDB.set_order:
		for t in earned_tiers(set_id):
			total += Balance.BADGE_PC_BONUS.get(t, 0.0)
	return total

func total_badges_earned() -> int:
	var n := 0
	for set_id in ContentDB.set_order:
		n += earned_tiers(set_id).size()
	return n

func tier_color(tier: String) -> Color:
	match tier:
		"bronze": return Color("#cd7f32")
		"silver": return Color("#c0c0c0")
		"gold": return Color("#ffd24a")
		"diamond": return Color("#9be7ff")
		"black": return Color("#6b6b80")
		"mythic": return Color("#ff5cf0")
		_: return Color("#555555")
