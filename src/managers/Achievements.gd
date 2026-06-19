extends Node
## Achievements (autoload)
## Internal milestone tracking. Event-driven unlocks plus stat sweeps.

signal achievement_unlocked(id, name)

const DEFS := [
	{"id": "first_pack", "name": "First Rip", "desc": "Open your first pack."},
	{"id": "first_legendary", "name": "Legend Found", "desc": "Pull your first Legendary."},
	{"id": "first_serialized", "name": "Numbered!", "desc": "Pull your first Serialized card."},
	{"id": "first_oneofone", "name": "One of One", "desc": "Pull a true 1-of-1."},
	{"id": "first_badge", "name": "Badge Earner", "desc": "Earn your first set badge."},
	{"id": "p_10k", "name": "Five Figures", "desc": "Reach 10,000 Total Prestige."},
	{"id": "p_100k", "name": "Six Figures", "desc": "Reach 100,000 Total Prestige."},
	{"id": "first_grade", "name": "Slabbed", "desc": "Grade your first card."},
	{"id": "first_gem", "name": "Perfect Ten", "desc": "Receive your first grade 10."},
	{"id": "first_trade", "name": "Dealmaker", "desc": "Complete your first NPC trade."},
	{"id": "unique_100", "name": "Curator", "desc": "Own 100 unique cards."},
	{"id": "cards_1000", "name": "Hoarder", "desc": "Own 1,000 total cards."},
]

var unlocked: Dictionary = {}   # id -> true

func reset() -> void:
	unlocked.clear()

func is_unlocked(id: String) -> bool:
	return unlocked.has(id)

func unlock(id: String) -> void:
	if unlocked.has(id):
		return
	unlocked[id] = true
	achievement_unlocked.emit(id, name_of(id))

func name_of(id: String) -> String:
	for d in DEFS:
		if d["id"] == id:
			return d["name"]
	return id

func count_unlocked() -> int:
	return unlocked.size()

## Sweep stat-based achievements. Call after economy-changing actions.
func evaluate_stats() -> void:
	var p := PrestigeCalc.total_prestige()
	if p >= 10000.0:
		unlock("p_10k")
	if p >= 100000.0:
		unlock("p_100k")
	if Game.unique_card_count() >= 100:
		unlock("unique_100")
	if Game.collection.size() >= 1000:
		unlock("cards_1000")

func to_dict() -> Dictionary:
	return {"unlocked": unlocked.duplicate()}

func from_dict(d: Dictionary) -> void:
	reset()
	unlocked = d.get("unlocked", {}).duplicate()
