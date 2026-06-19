extends Node
## Market (autoload)
## Offline NPC-driven demand & hype. Holds per-save serializable trend state.
## Trends boost demand/hype for a faction, set, or variant; hype decays daily.

signal market_refreshed(trends)

# Additive offsets applied on top of each card's intrinsic base values.
var faction_hype: Dictionary = {}   # faction(String) -> float
var set_hype: Dictionary = {}       # set_id(String) -> float
var variant_hype: Dictionary = {}   # variant(int) -> float
var active_trends: Array = []       # Array[Dictionary]: {scope,key,label,kind}

func reset() -> void:
	faction_hype.clear()
	set_hype.clear()
	variant_hype.clear()
	active_trends.clear()

## Pick a fresh batch of trends. Called on day advance / market refresh.
func refresh() -> void:
	# Decay existing hype toward 0.
	_decay(faction_hype)
	_decay(set_hype)
	_decay(variant_hype)
	active_trends.clear()

	var all_factions := _all_factions()
	for _i in range(Balance.MARKET_TRENDS_PER_REFRESH):
		var scope := RNGService.randi_range(0, 2)
		var hot := RNGService.randf() < 0.7   # mostly heating up
		var boost: float = (Balance.TREND_BOOST if hot else -Balance.TREND_COOL)
		var trend := {}
		match scope:
			0: # faction
				var f: String = all_factions[RNGService.randi_range(0, all_factions.size() - 1)]
				faction_hype[f] = clampf(faction_hype.get(f, 0.0) + boost, -0.6, 0.9)
				trend = {"scope": "faction", "key": f,
					"label": "%s cards are %s" % [f, "trending" if hot else "cooling off"], "kind": hot}
			1: # set
				var sid: String = ContentDB.set_order[RNGService.randi_range(0, ContentDB.set_order.size() - 1)]
				set_hype[sid] = clampf(set_hype.get(sid, 0.0) + boost, -0.6, 0.9)
				trend = {"scope": "set", "key": sid,
					"label": "%s is %s" % [ContentDB.get_set(sid).name, "heating up" if hot else "cooling off"], "kind": hot}
			2: # variant (chase finishes)
				var variants := [Enums.Variant.HOLO, Enums.Variant.RAINBOW, Enums.Variant.GOLD,
					Enums.Variant.SHADOW, Enums.Variant.SIGNATURE]
				var v: int = variants[RNGService.randi_range(0, variants.size() - 1)]
				variant_hype[v] = clampf(variant_hype.get(v, 0.0) + boost, -0.6, 0.9)
				trend = {"scope": "variant", "key": v,
					"label": "Collectors are %s %s variants" % ["chasing" if hot else "dumping", Enums.variant_name(v)], "kind": hot}
		active_trends.append(trend)
	market_refreshed.emit(active_trends)

func _decay(d: Dictionary) -> void:
	for k in d.keys():
		d[k] = d[k] * (1.0 - Balance.HYPE_DECAY)
		if abs(d[k]) < 0.02:
			d.erase(k)

func _all_factions() -> Array:
	var seen := {}
	for sid in ContentDB.set_order:
		for f in ContentDB.get_set(sid).factions:
			seen[f] = true
	return seen.keys()

# --- queries used by PrestigeCalc ---
func demand_for(def: CardDefinition) -> float:
	var d := def.demand_base
	d += faction_hype.get(def.faction, 0.0) * 0.6
	d += set_hype.get(def.set_id, 0.0) * 0.5
	return clampf(d, 0.0, 1.0)

func hype_for(def: CardDefinition, variant: int) -> float:
	var h := def.hype_base
	h += faction_hype.get(def.faction, 0.0)
	h += set_hype.get(def.set_id, 0.0)
	h += variant_hype.get(variant, 0.0)
	return clampf(h, 0.0, 1.0)

func trend_summary() -> String:
	if active_trends.is_empty():
		return "Market is calm."
	var parts: Array = []
	for t in active_trends:
		parts.append(t["label"])
	return " • ".join(parts)

func to_dict() -> Dictionary:
	# Variant keys are ints; JSON dict keys become strings, handled on load.
	return {
		"faction_hype": faction_hype,
		"set_hype": set_hype,
		"variant_hype": variant_hype,
		"active_trends": active_trends,
	}

func from_dict(d: Dictionary) -> void:
	reset()
	faction_hype = d.get("faction_hype", {}).duplicate()
	set_hype = d.get("set_hype", {}).duplicate()
	var vh: Dictionary = d.get("variant_hype", {})
	for k in vh.keys():
		variant_hype[int(k)] = float(vh[k])
	active_trends = d.get("active_trends", []).duplicate(true)
	# Normalize trend keys for variant scope back to int.
	for t in active_trends:
		if t.get("scope", "") == "variant":
			t["key"] = int(t["key"])
