extends Node
## Game (autoload)
## Central player state + the only place economy mutations happen. UI calls these
## methods; it never edits collection/PL directly. Emits `changed` so screens
## refresh, and `notify` for transient toasts (pulls, achievements).

signal changed
signal notify(text)
signal pulls_ready(pulls)        # emitted when a product is opened (Array[CardInstance])

# --- core economy / progression ---
var pl: float = 0.0
var day: int = 0
var world_seed: int = 0
var action_count: int = 0

# --- collection & inventory ---
var collection: Array = []           # Array[CardInstance]
var sealed_inventory: Dictionary = {}  # product_id -> count(int)

# --- counters & uniqueness ledgers ---
var uid_counter: int = 0
var acquired_counter: int = 0
var used_oneofones: Dictionary = {}   # card_id -> true
var used_serials: Dictionary = {}     # card_id -> Array[int] used serial indices

# --- display room ---
var display_card_uids: Array = []     # ordered Array[int]
var display_sealed: Array = []        # Array[String] product ids
var display_badge_set: String = ""
var featured_uid: int = -1

# --- misc ---
var recent_pulls: Array = []          # Array[Dictionary] last notable pulls
var settings: Dictionary = {
	"master_volume": 1.0, "reduce_flashing": false, "fast_reveal": false,
}

func _ready() -> void:
	# Connect achievement toasts to the notify channel.
	Achievements.achievement_unlocked.connect(func(_id, aname): notify.emit("Achievement: " + aname))

# ===========================================================================
# Lifecycle
# ===========================================================================
func new_game(seed_value: int = -1) -> void:
	if seed_value < 0:
		seed_value = int(Time.get_unix_time_from_system()) ^ (randi() & 0x7fffffff)
	world_seed = seed_value
	RNGService.set_world_seed(world_seed)

	pl = Balance.STARTING_PL
	day = 0
	action_count = 0
	collection.clear()
	sealed_inventory.clear()
	uid_counter = 0
	acquired_counter = 0
	used_oneofones.clear()
	used_serials.clear()
	display_card_uids.clear()
	display_sealed.clear()
	display_badge_set = ""
	featured_uid = -1
	recent_pulls.clear()

	Market.reset()
	Market.refresh()
	Trades.reset()
	Trades.refresh()
	Reputation.reset()
	Achievements.reset()
	on_state_changed()

# ===========================================================================
# Counters / lookups
# ===========================================================================
func next_uid() -> int:
	uid_counter += 1
	return uid_counter

func next_acquired_seq() -> int:
	acquired_counter += 1
	return acquired_counter

func get_instance(uid: int) -> CardInstance:
	for inst in collection:
		if inst.uid == uid:
			return inst
	return null

func remove_instance(uid: int) -> bool:
	for i in range(collection.size()):
		if collection[i].uid == uid:
			collection.remove_at(i)
			display_card_uids.erase(uid)
			if featured_uid == uid:
				featured_uid = -1
			return true
	return false

func unique_card_count() -> int:
	var seen := {}
	for inst in collection:
		seen[inst.card_id] = true
	return seen.size()

# ===========================================================================
# Uniqueness ledgers (used by PackEngine during generation)
# ===========================================================================
func is_oneofone_taken(card_id: String) -> bool:
	return used_oneofones.has(card_id)

func reserve_oneofone(card_id: String) -> void:
	used_oneofones[card_id] = true

func serials_remaining(card_id: String, run_size: int) -> int:
	return run_size - used_serials.get(card_id, []).size()

func reserve_serial(card_id: String, run_size: int) -> int:
	var used: Array = used_serials.get(card_id, [])
	if used.size() >= run_size:
		return -1
	var idx := -1
	var attempts := 0
	while attempts < run_size * 3:
		var candidate := RNGService.randi_range(1, run_size)
		if not used.has(candidate):
			idx = candidate
			break
		attempts += 1
	if idx < 0:
		for i in range(1, run_size + 1):
			if not used.has(i):
				idx = i
				break
	if idx > 0:
		used.append(idx)
		used_serials[card_id] = used
	return idx

# ===========================================================================
# Shop: buy sealed product
# ===========================================================================
func buy_product(product_id: String) -> Dictionary:
	var prod := ContentDB.get_product(product_id)
	if prod == null:
		return {"ok": false, "reason": "Unknown product."}
	if pl < prod.price:
		return {"ok": false, "reason": "Not enough PL."}
	pl -= prod.price
	add_sealed(product_id, 1)

	Reputation.add("Sealed Investor", prod.price * 0.04)
	if prod.price >= 1000.0:
		Reputation.add("Whale Collector", prod.price * 0.02)
	if prod.kind == "pack" or prod.price <= 50.0:
		Reputation.add("Budget Grinder", 5.0)

	on_state_changed()
	autosave("buy")
	return {"ok": true, "reason": "Purchased %s." % prod.name}

func add_sealed(product_id: String, qty: int) -> void:
	sealed_inventory[product_id] = sealed_inventory.get(product_id, 0) + qty

func remove_sealed(product_id: String, qty: int) -> bool:
	var have: int = sealed_inventory.get(product_id, 0)
	if have < qty:
		return false
	if have == qty:
		sealed_inventory.erase(product_id)
	else:
		sealed_inventory[product_id] = have - qty
	display_sealed_cleanup()
	return true

func display_sealed_cleanup() -> void:
	for pid in display_sealed.duplicate():
		if not sealed_inventory.has(pid):
			display_sealed.erase(pid)

# ===========================================================================
# Open product (one unit) -> generates all its cards, commits to collection
# ===========================================================================
func open_unit(product_id: String) -> Dictionary:
	var prod := ContentDB.get_product(product_id)
	if prod == null:
		return {"ok": false, "reason": "Unknown product."}
	if sealed_inventory.get(product_id, 0) < 1:
		return {"ok": false, "reason": "You don't own that sealed product."}
	remove_sealed(product_id, 1)

	# Snapshot which (card_id, variant) keys are already owned for new/dup flag.
	var owned_keys := {}
	for inst in collection:
		owned_keys[_key(inst)] = true

	var pulls := PackEngine.generate_pulls(prod.set_id, prod.total_cards(), prod.luck)
	var gain := 0.0
	for inst in pulls:
		var def := ContentDB.get_card(inst.card_id)
		var is_new: bool = not owned_keys.has(_key(inst))
		owned_keys[_key(inst)] = true
		collection.append(inst)
		gain += PrestigeCalc.card_value(inst)
		_handle_pull_rewards(inst, def, is_new)

	action_count += 1
	# Market & trends evolve over time as you play.
	if action_count % 3 == 0:
		Market.refresh()
		Trades.refresh()

	Achievements.unlock("first_pack")
	on_state_changed()
	pulls_ready.emit(pulls)
	autosave("open")
	return {"ok": true, "reason": "Opened %s." % prod.name, "pulls": pulls,
		"gain": gain, "spent_pc": prod.price}

func _handle_pull_rewards(inst: CardInstance, def: CardDefinition, is_new: bool) -> void:
	var er := Enums.effective_rarity(def.rarity, inst.variant)
	if er == Enums.Rarity.LEGENDARY:
		Achievements.unlock("first_legendary")
		Reputation.add("Grail Hunter", 30.0)
	if inst.variant == Enums.Variant.SERIALIZED:
		Achievements.unlock("first_serialized")
		Reputation.add("Grail Hunter", 60.0)
	if inst.variant == Enums.Variant.ONEOFONE:
		Achievements.unlock("first_oneofone")
		Reputation.add("OneOfOne Owner", 150.0)
		Reputation.add("Grail Hunter", 100.0)
	if inst.variant >= Enums.Variant.HOLO:
		Reputation.add("Variant Hunter", 3.0)

	# Record notable pulls for the dashboard feed.
	if Enums.is_grail(def.rarity, inst.variant) or recent_pulls.size() < 1 or is_new:
		recent_pulls.push_front({
			"label": def.name,
			"sub": "%s %s%s" % [Enums.variant_name(inst.variant), Enums.rarity_name(er),
				(" " + inst.serial_label()) if inst.serial_label() != "" else ""],
			"value": PrestigeCalc.card_value(inst),
			"grail": Enums.is_grail(def.rarity, inst.variant),
			"new": is_new,
		})
		while recent_pulls.size() > 12:
			recent_pulls.pop_back()

func _key(inst: CardInstance) -> String:
	return "%s:%d" % [inst.card_id, inst.variant]

# ===========================================================================
# Selling
# ===========================================================================
func sell_instance(uid: int) -> Dictionary:
	var inst := get_instance(uid)
	if inst == null:
		return {"ok": false, "reason": "Card not found."}
	var value := PrestigeCalc.sell_value(inst)
	remove_instance(uid)
	pl += value
	Reputation.add("Master Trader", 2.0)
	on_state_changed()
	autosave("sell")
	return {"ok": true, "reason": "Sold for %d PL." % int(value), "value": value}

## Sell every duplicate (all copies except the single best copy per card_id).
func sell_all_duplicates() -> Dictionary:
	var dupes := duplicate_instance_uids()
	var total := 0.0
	for uid in dupes:
		var inst := get_instance(uid)
		if inst == null:
			continue
		total += PrestigeCalc.sell_value(inst)
		remove_instance(uid)
	if dupes.size() > 0:
		pl += total
		Reputation.add("Master Trader", float(dupes.size()))
		on_state_changed()
		autosave("sell_dupes")
	return {"ok": true, "count": dupes.size(), "total": total}

# ===========================================================================
# Grading
# ===========================================================================
func grade_instance(uid: int) -> Dictionary:
	var inst := get_instance(uid)
	if inst == null:
		return {"ok": false, "reason": "Card not found."}
	if inst.graded:
		return {"ok": false, "reason": "Already graded."}
	var fee := Grading.fee()
	if pl < fee:
		return {"ok": false, "reason": "Not enough PL for grading fee."}
	pl -= fee
	inst.grade = Grading.roll_grade(inst.condition)
	inst.graded = true
	Achievements.unlock("first_grade")
	if inst.grade >= 10:
		Achievements.unlock("first_gem")
	Reputation.add("Grading Specialist", 15.0)
	on_state_changed()
	autosave("grade")
	return {"ok": true, "reason": "Graded %d/10." % inst.grade, "grade": inst.grade}

# ===========================================================================
# Duplicates / best copy
# ===========================================================================
func best_copy_uid(card_id: String) -> int:
	var best := -1
	var best_val := -1.0
	for inst in collection:
		if inst.card_id == card_id:
			var v := PrestigeCalc.card_value(inst)
			if v > best_val:
				best_val = v
				best = inst.uid
	return best

func is_best_copy(uid: int) -> bool:
	var inst := get_instance(uid)
	if inst == null:
		return false
	return best_copy_uid(inst.card_id) == uid

## All instance uids that are duplicates (not the best copy of their card).
func duplicate_instance_uids() -> Array:
	var best_by_card := {}
	for inst in collection:
		var cur: float = best_by_card.get(inst.card_id, {"uid": -1, "val": -1.0})["val"]
		var v := PrestigeCalc.card_value(inst)
		if v > cur:
			best_by_card[inst.card_id] = {"uid": inst.uid, "val": v}
	var out: Array = []
	for inst in collection:
		if best_by_card[inst.card_id]["uid"] != inst.uid:
			out.append(inst.uid)
	return out

func quantity_of(card_id: String, variant: int = -1) -> int:
	var n := 0
	for inst in collection:
		if inst.card_id == card_id and (variant < 0 or inst.variant == variant):
			n += 1
	return n

# ===========================================================================
# Display room
# ===========================================================================
func display_slots_unlocked() -> int:
	var slots := Balance.DISPLAY_BASE_SLOTS
	var p := PrestigeCalc.total_prestige()
	for milestone in Balance.DISPLAY_SLOT_MILESTONES:
		if p >= milestone:
			slots += 1
	return slots

func is_displayed(uid: int) -> bool:
	return display_card_uids.has(uid)

func toggle_display(uid: int) -> Dictionary:
	if display_card_uids.has(uid):
		display_card_uids.erase(uid)
		if featured_uid == uid:
			featured_uid = -1
		on_state_changed()
		autosave("display")
		return {"ok": true, "reason": "Removed from display."}
	if display_card_uids.size() >= display_slots_unlocked():
		return {"ok": false, "reason": "All display slots are full. Unlock more with Prestige."}
	display_card_uids.append(uid)
	if featured_uid < 0:
		featured_uid = uid
	on_state_changed()
	autosave("display")
	return {"ok": true, "reason": "Added to display."}

func set_featured(uid: int) -> void:
	if display_card_uids.has(uid):
		featured_uid = uid
		on_state_changed()
		autosave("display")

## PC bonus contributed by displayed items.
func display_bonus_pc() -> float:
	var bonus := 0.0
	for uid in display_card_uids:
		var inst := get_instance(uid)
		if inst != null:
			bonus += PrestigeCalc.card_value(inst) * Balance.DISPLAY_PC_BONUS
	return bonus

# ===========================================================================
# Progression
# ===========================================================================
func advance_day() -> void:
	day += 1
	action_count += 1
	Market.refresh()
	Trades.refresh()
	on_state_changed()
	autosave("day")
	notify.emit("A new day dawns. The market shifts.")

# ===========================================================================
# Dashboard helpers
# ===========================================================================
func best_card_instance() -> CardInstance:
	var best: CardInstance = null
	var best_val := -1.0
	for inst in collection:
		var v := PrestigeCalc.card_value(inst)
		if v > best_val:
			best_val = v
			best = inst
	return best

func next_milestone_text() -> String:
	var p := PrestigeCalc.total_prestige()
	for m in [10000.0, 100000.0, 250000.0, 1000000.0]:
		if p < m:
			return "%s P toward %s P" % [_fmt(p), _fmt(m)]
	return "Prestige legend! (%s P)" % _fmt(p)

func _fmt(v: float) -> String:
	return String.num(v, 0)

# ===========================================================================
# State change hook
# ===========================================================================
func on_state_changed() -> void:
	Achievements.evaluate_stats()
	if Badges.total_badges_earned() > 0:
		Achievements.unlock("first_badge")
	changed.emit()

func autosave(reason: String) -> void:
	SaveManager.save_game(self, reason)

# ===========================================================================
# Debug / dev helpers (used by the Debug panel)
# ===========================================================================
func debug_add_pl(amount: float) -> void:
	pl += amount
	on_state_changed()

func debug_open_random() -> Dictionary:
	var pid: String = ContentDB.product_order[RNGService.randi_range(0, ContentDB.product_order.size() - 1)]
	add_sealed(pid, 1)
	return open_unit(pid)

## Commit a list of pre-generated instances directly (debug).
func debug_commit(pulls: Array) -> void:
	for inst in pulls:
		collection.append(inst)
	on_state_changed()

## Force a specific kind of pull: "legendary" | "serialized" | "oneofone".
func debug_force_pull(kind: String) -> CardInstance:
	var inst := CardInstance.new()
	inst.uid = next_uid()
	inst.acquired_seq = next_acquired_seq()
	inst.condition = PackEngine._roll_condition()
	match kind:
		"legendary":
			var cid := _debug_pick_card_by_rarity(Enums.Rarity.LEGENDARY)
			if cid == "":
				return null
			inst.card_id = cid
			inst.variant = Enums.Variant.HOLO
		"serialized":
			var found := ""
			for cid2 in ContentDB.cards.keys():
				var def: CardDefinition = ContentDB.cards[cid2]
				if def.can_be_serialized() and serials_remaining(cid2, def.serial_run) > 0:
					found = cid2
					break
			if found == "":
				return null
			var d := ContentDB.get_card(found)
			inst.card_id = found
			inst.variant = Enums.Variant.SERIALIZED
			inst.serial_index = reserve_serial(found, d.serial_run)
			inst.serial_max = d.serial_run
		"oneofone":
			var found2 := ""
			for cid3 in ContentDB.cards.keys():
				var def3: CardDefinition = ContentDB.cards[cid3]
				if def3.can_be_oneofone() and not is_oneofone_taken(cid3):
					found2 = cid3
					break
			if found2 == "":
				return null
			inst.card_id = found2
			inst.variant = Enums.Variant.ONEOFONE
			inst.serial_index = 1
			inst.serial_max = 1
			reserve_oneofone(found2)
		_:
			return null
	collection.append(inst)
	_handle_pull_rewards(inst, ContentDB.get_card(inst.card_id), true)
	on_state_changed()
	return inst

func _debug_pick_card_by_rarity(rarity: int) -> String:
	var matches: Array = []
	for cid in ContentDB.cards.keys():
		if ContentDB.cards[cid].rarity == rarity:
			matches.append(cid)
	if matches.is_empty():
		return ""
	return matches[RNGService.randi_range(0, matches.size() - 1)]

## Fill in every missing base card of a set with a Base copy (debug).
func debug_complete_set(set_id: String) -> int:
	var set_def := ContentDB.get_set(set_id)
	if set_def == null:
		return 0
	var owned := {}
	for inst in collection:
		owned[inst.card_id] = true
	var added := 0
	for cid in set_def.card_ids:
		if owned.has(cid):
			continue
		var inst := CardInstance.new()
		inst.uid = next_uid()
		inst.acquired_seq = next_acquired_seq()
		inst.card_id = cid
		inst.variant = Enums.Variant.BASE
		inst.condition = Enums.Condition.NEAR_MINT
		collection.append(inst)
		added += 1
	on_state_changed()
	return added

# ===========================================================================
# Serialization
# ===========================================================================
func to_dict() -> Dictionary:
	var insts: Array = []
	for inst in collection:
		insts.append(inst.to_dict())
	return {
		"pl": pl, "day": day, "world_seed": world_seed, "action_count": action_count,
		"rng_state": str(RNGService.gameplay.state),
		"uid_counter": uid_counter, "acquired_counter": acquired_counter,
		"collection": insts, "sealed_inventory": sealed_inventory.duplicate(),
		"used_oneofones": used_oneofones.duplicate(),
		"used_serials": used_serials.duplicate(true),
		"display_card_uids": display_card_uids.duplicate(),
		"display_sealed": display_sealed.duplicate(),
		"display_badge_set": display_badge_set,
		"featured_uid": featured_uid,
		"recent_pulls": recent_pulls.duplicate(true),
		"settings": settings.duplicate(),
		"market": Market.to_dict(),
		"trades": Trades.to_dict(),
		"reputation": Reputation.to_dict(),
		"achievements": Achievements.to_dict(),
	}

func from_dict(d: Dictionary) -> void:
	pl = float(d.get("pl", Balance.STARTING_PL))
	day = int(d.get("day", 0))
	world_seed = int(d.get("world_seed", 0))
	action_count = int(d.get("action_count", 0))
	uid_counter = int(d.get("uid_counter", 0))
	acquired_counter = int(d.get("acquired_counter", 0))
	RNGService.set_world_seed(world_seed)
	if d.has("rng_state"):
		RNGService.gameplay.state = int(str(d["rng_state"]))

	collection.clear()
	for cd in d.get("collection", []):
		collection.append(CardInstance.from_dict(cd))

	sealed_inventory.clear()
	for k in d.get("sealed_inventory", {}).keys():
		sealed_inventory[k] = int(d["sealed_inventory"][k])

	used_oneofones = d.get("used_oneofones", {}).duplicate()

	used_serials.clear()
	for k in d.get("used_serials", {}).keys():
		var arr: Array = []
		for n in d["used_serials"][k]:
			arr.append(int(n))
		used_serials[k] = arr

	display_card_uids.clear()
	for u in d.get("display_card_uids", []):
		display_card_uids.append(int(u))
	display_sealed = d.get("display_sealed", []).duplicate()
	display_badge_set = String(d.get("display_badge_set", ""))
	featured_uid = int(d.get("featured_uid", -1))
	recent_pulls = d.get("recent_pulls", []).duplicate(true)
	settings = d.get("settings", settings).duplicate()

	Market.from_dict(d.get("market", {}))
	Trades.from_dict(d.get("trades", {}))
	Reputation.from_dict(d.get("reputation", {}))
	Achievements.from_dict(d.get("achievements", {}))
	changed.emit()
