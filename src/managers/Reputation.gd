extends Node
## Reputation (autoload)
## Tracks what *kind* of collector the player is, separate from Prestige.
## Points accrue from behavior; the dominant category gives a title.

const CATEGORIES := [
	"Set Completionist", "Grail Hunter", "Sealed Investor", "Master Trader",
	"Grading Specialist", "Variant Hunter", "OneOfOne Owner", "Whale Collector",
	"Budget Grinder",
]

var points: Dictionary = {}   # category -> float

func reset() -> void:
	points.clear()
	for c in CATEGORIES:
		points[c] = 0.0

func add(category: String, amount: float) -> void:
	if not points.has(category):
		points[category] = 0.0
	points[category] += amount

func total() -> float:
	var t := 0.0
	for v in points.values():
		t += v
	return t

func top_category() -> String:
	var best := CATEGORIES[0]
	var best_val := -1.0
	for c in CATEGORIES:
		var v: float = points.get(c, 0.0)
		if v > best_val:
			best_val = v
			best = c
	return best

func title() -> String:
	if total() <= 0.0:
		return "Rookie Collector"
	var cat := top_category()
	var tier := tier_for(points.get(cat, 0.0))
	return "%s %s" % [tier, cat]

func tier_for(val: float) -> String:
	if val >= 2000.0: return "Legendary"
	if val >= 800.0: return "Elite"
	if val >= 300.0: return "Seasoned"
	if val >= 80.0: return "Aspiring"
	return "Novice"

func to_dict() -> Dictionary:
	return {"points": points.duplicate()}

func from_dict(d: Dictionary) -> void:
	reset()
	var p: Dictionary = d.get("points", {})
	for k in p.keys():
		points[k] = float(p[k])
