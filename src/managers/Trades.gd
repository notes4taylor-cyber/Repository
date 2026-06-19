extends Node
## Trades (autoload)
## Offline NPC collectors with distinct preferences make trade offers based on
## the player's current inventory. Offers ask for ONE player item and give back
## a bundle of PL / sealed product / cards. NPC-given cards are never Serialized
## or 1-of-1, so unique-card constraints can never be violated.

signal offers_refreshed

# type, friendly description, sample names, "overpay" factor for wanted items.
const NPC_TYPES := [
	{"type": "Set Completionist", "desc": "Needs cards to finish sets.", "factor": 1.15,
		"names": ["Dana the Lister", "Completist Cal", "Margo Pages"]},
	{"type": "Holo Hunter", "desc": "Obsessed with shiny finishes.", "factor": 1.25,
		"names": ["Shiny Sed", "Glint Gary", "Prisma Pat"]},
	{"type": "Sealed Investor", "desc": "Hoards sealed product.", "factor": 1.1,
		"names": ["Vault Vera", "Sealed Sam", "Holdco Hugo"]},
	{"type": "Legendary Chaser", "desc": "Only the biggest hits.", "factor": 1.35,
		"names": ["Grail Greta", "Chase Chen", "Apex Ada"]},
	{"type": "Budget Collector", "desc": "Loves cheap bulk.", "factor": 1.05,
		"names": ["Bargain Bo", "Penny Priya", "Thrift Tom"]},
	{"type": "Whale", "desc": "Deep pockets, big wants.", "factor": 1.4,
		"names": ["Tycoon Tess", "Magnate Max", "Baron Bill"]},
	{"type": "Condition Snob", "desc": "Mint or nothing.", "factor": 1.3,
		"names": ["Gem Gwen", "Pristine Pete", "Flawless Fay"]},
	{"type": "Theme Collector", "desc": "Chases one faction.", "factor": 1.2,
		"names": ["Faction Finn", "Theme Thea", "Lore Lena"]},
]

const MAX_OFFERS := 5

var offers: Array = []   # Array[Dictionary]
var _next_offer_id: int = 1

func reset() -> void:
	offers.clear()
	_next_offer_id = 1

func refresh() -> void:
	offers.clear()
	var attempts := 0
	while offers.size() < MAX_OFFERS and attempts < 40:
		attempts += 1
		var npc = NPC_TYPES[RNGService.randi_range(0, NPC_TYPES.size() - 1)]
		var offer := _build_offer(npc)
		if not offer.is_empty():
			offers.append(offer)
	offers_refreshed.emit()

func _build_offer(npc: Dictionary) -> Dictionary:
	var want := _pick_want(npc)
	if want.is_empty():
		return {}
	var want_value: float = want["value"]
	var factor: float = npc["factor"]
	var give_target := want_value * factor
	var give := _build_give(give_target)
	var give_value: float = give["value"]

	var offer := {
		"id": _next_offer_id,
		"npc_name": npc["names"][RNGService.randi_range(0, npc["names"].size() - 1)],
		"npc_type": npc["type"],
		"npc_desc": npc["desc"],
		"want": want["ref"],          # {kind:"card",uid:int} or {kind:"sealed",product_id,qty}
		"want_label": want["label"],
		"want_value": want_value,
		"give": give["spec"],         # {pl:float, sealed:{id:qty}, cards:[CardInstance]}
		"give_label": give["label"],
		"give_value": give_value,
	}
	_next_offer_id += 1
	return offer

# ---------------------------------------------------------------------------
# What the NPC wants from the player (one item), shaped by NPC type.
# ---------------------------------------------------------------------------
func _pick_want(npc: Dictionary) -> Dictionary:
	var t: String = npc["type"]
	if t == "Sealed Investor" and not Game.sealed_inventory.is_empty():
		var pid: String = Game.sealed_inventory.keys()[RNGService.randi_range(0, Game.sealed_inventory.size() - 1)]
		var prod := ContentDB.get_product(pid)
		return {"ref": {"kind": "sealed", "product_id": pid, "qty": 1},
			"label": "1x %s" % prod.name, "value": prod.price * Balance.SEALED_PC_FACTOR}

	# Otherwise the NPC wants a card. Prefer duplicates so the player keeps best.
	var candidates := _card_candidates_for(t)
	if candidates.is_empty():
		return {}
	var inst: CardInstance = candidates[RNGService.randi_range(0, candidates.size() - 1)]
	var def := ContentDB.get_card(inst.card_id)
	return {"ref": {"kind": "card", "uid": inst.uid},
		"label": "%s (%s %s)" % [def.name, Enums.variant_name(inst.variant), Enums.condition_name(inst.condition)],
		"value": PrestigeCalc.card_value(inst)}

func _card_candidates_for(t: String) -> Array:
	var dup_uids := Game.duplicate_instance_uids()   # safe to give away
	var out: Array = []
	for uid in dup_uids:
		var inst := Game.get_instance(uid)
		if inst == null:
			continue
		# Never let NPCs target unique/serialized as a "want" preference target
		# beyond value; they can still want them, but we keep it simple here.
		var def := ContentDB.get_card(inst.card_id)
		var wants := false
		match t:
			"Holo Hunter": wants = inst.variant >= Enums.Variant.HOLO
			"Legendary Chaser": wants = def.rarity >= Enums.Rarity.LEGENDARY or inst.variant >= Enums.Variant.GOLD
			"Condition Snob": wants = inst.condition >= Enums.Condition.MINT or (inst.graded and inst.grade >= 9)
			"Whale": wants = PrestigeCalc.card_value(inst) >= Balance.HIGH_VALUE_THRESHOLD
			"Budget Collector": wants = PrestigeCalc.card_value(inst) <= 25.0
			"Set Completionist": wants = true
			"Theme Collector": wants = true
			_: wants = true
		if wants:
			out.append(inst)
	# Fallbacks so an offer can still be made.
	if out.is_empty():
		for uid in dup_uids:
			var i2 := Game.get_instance(uid)
			if i2 != null:
				out.append(i2)
	return out

# ---------------------------------------------------------------------------
# What the NPC gives back, targeting `target` PL of value.
# ---------------------------------------------------------------------------
func _build_give(target: float) -> Dictionary:
	var spec := {"pl": 0.0, "sealed": {}, "cards": []}
	var remaining := target
	var labels: Array = []

	# Sometimes throw in a card (never serialized / 1-of-1).
	if RNGService.randf() < 0.5 and remaining > 8.0:
		var inst := _generate_giveable_card(remaining * 0.7)
		if inst != null:
			spec["cards"].append(inst)
			var v := PrestigeCalc.card_value(inst)
			remaining -= v
			var def := ContentDB.get_card(inst.card_id)
			labels.append("%s (%s)" % [def.name, Enums.variant_name(inst.variant)])

	# Sometimes a cheap sealed product.
	if RNGService.randf() < 0.3 and remaining > 0.0:
		var pid := _cheap_product_under(remaining)
		if pid != "":
			spec["sealed"][pid] = 1
			remaining -= ContentDB.get_product(pid).price * Balance.SEALED_PC_FACTOR
			labels.append("1x %s" % ContentDB.get_product(pid).name)

	# Remainder in PL (never negative).
	var pl := snappedf(maxf(0.0, remaining), 1.0)
	spec["pl"] = pl
	if pl > 0.0:
		labels.append("%d PL" % int(pl))
	if labels.is_empty():
		labels.append("%d PL" % int(target))
		spec["pl"] = snappedf(target, 1.0)

	var total_val: float = spec["pl"]
	for c in spec["cards"]:
		total_val += PrestigeCalc.card_value(c)
	for pid in spec["sealed"].keys():
		total_val += ContentDB.get_product(pid).price * Balance.SEALED_PC_FACTOR * spec["sealed"][pid]
	return {"spec": spec, "label": " + ".join(labels), "value": total_val}

## Build a non-unique card roughly worth up to `budget`. uid stays 0 until accept.
func _generate_giveable_card(budget: float) -> CardInstance:
	# Pick a random set & a card whose plausible value fits, variant up to GOLD.
	var set_id: String = ContentDB.set_order[RNGService.randi_range(0, ContentDB.set_order.size() - 1)]
	var set_def := ContentDB.get_set(set_id)
	var cid: String = set_def.card_ids[RNGService.randi_range(0, set_def.card_ids.size() - 1)]
	var inst := CardInstance.new()
	inst.uid = 0
	inst.card_id = cid
	var safe_variants := [Enums.Variant.BASE, Enums.Variant.HOLO, Enums.Variant.RAINBOW, Enums.Variant.GOLD]
	var def := ContentDB.get_card(cid)
	var allowed: Array = []
	for v in safe_variants:
		if def.available_variants.has(v):
			allowed.append(v)
	if allowed.is_empty():
		allowed = [Enums.Variant.BASE]
	inst.variant = allowed[RNGService.randi_range(0, allowed.size() - 1)]
	inst.condition = PackEngine._roll_condition()
	return inst

func _cheap_product_under(budget: float) -> String:
	var best := ""
	var best_price := 0.0
	for pid in ContentDB.product_order:
		var prod := ContentDB.get_product(pid)
		if prod.price <= budget and prod.price > best_price and prod.kind == "pack":
			best = pid
			best_price = prod.price
	return best

# ---------------------------------------------------------------------------
# Accept / decline
# ---------------------------------------------------------------------------
func get_offer(offer_id: int) -> Dictionary:
	for o in offers:
		if o["id"] == offer_id:
			return o
	return {}

## Returns {ok:bool, reason:String}
func accept(offer_id: int) -> Dictionary:
	var offer := get_offer(offer_id)
	if offer.is_empty():
		return {"ok": false, "reason": "Offer no longer available."}
	var want = offer["want"]

	# Validate & remove the wanted item.
	if want["kind"] == "card":
		var inst := Game.get_instance(want["uid"])
		if inst == null:
			offers.erase(offer)
			return {"ok": false, "reason": "You no longer own that card."}
		Game.remove_instance(want["uid"])
	elif want["kind"] == "sealed":
		if Game.sealed_inventory.get(want["product_id"], 0) < want["qty"]:
			offers.erase(offer)
			return {"ok": false, "reason": "You no longer own that sealed product."}
		Game.remove_sealed(want["product_id"], want["qty"])

	# Grant the give bundle.
	var give = offer["give"]
	Game.pl += give.get("pl", 0.0)
	for pid in give.get("sealed", {}).keys():
		Game.add_sealed(pid, give["sealed"][pid])
	for c in give.get("cards", []):
		var inst2: CardInstance = c
		inst2.uid = Game.next_uid()
		inst2.acquired_seq = Game.next_acquired_seq()
		Game.collection.append(inst2)

	Reputation.add("Master Trader", 25.0)
	Achievements.unlock("first_trade")
	offers.erase(offer)
	Game.on_state_changed()
	Game.autosave("trade")
	return {"ok": true, "reason": "Trade complete."}

func decline(offer_id: int) -> void:
	var offer := get_offer(offer_id)
	if not offer.is_empty():
		offers.erase(offer)

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
func to_dict() -> Dictionary:
	var out_offers: Array = []
	for o in offers:
		var oc: Dictionary = o.duplicate(true)
		var give_cards: Array = []
		for c in o["give"].get("cards", []):
			give_cards.append(c.to_dict())
		oc["give"] = o["give"].duplicate(true)
		oc["give"]["cards"] = give_cards
		out_offers.append(oc)
	return {"offers": out_offers, "next_offer_id": _next_offer_id}

func from_dict(d: Dictionary) -> void:
	reset()
	_next_offer_id = int(d.get("next_offer_id", 1))
	for o in d.get("offers", []):
		var oc: Dictionary = o.duplicate(true)
		var cards: Array = []
		for cd in o["give"].get("cards", []):
			cards.append(CardInstance.from_dict(cd))
		oc["give"]["cards"] = cards
		# normalize want uid / qty ints
		if oc["want"].get("kind", "") == "card":
			oc["want"]["uid"] = int(oc["want"]["uid"])
		offers.append(oc)
