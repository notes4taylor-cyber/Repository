extends Node
## RNGService (autoload)
## Centralized, seedable randomness so gameplay luck is reproducible per save
## and content generation is deterministic. Keeps two streams:
##   - gameplay: seeded by the save's world seed, state persisted in saves
##   - content : seeded by Balance.CONTENT_SEED, used to build the checklist

var gameplay := RandomNumberGenerator.new()
var content := RandomNumberGenerator.new()

func _ready() -> void:
	content.seed = Balance.CONTENT_SEED
	gameplay.randomize()

func set_world_seed(world_seed: int) -> void:
	gameplay.seed = world_seed
	gameplay.state = world_seed

func reset_content() -> void:
	content.seed = Balance.CONTENT_SEED
	content.state = Balance.CONTENT_SEED

# --- gameplay convenience ---
func randf() -> float:
	return gameplay.randf()

func randi_range(a: int, b: int) -> int:
	return gameplay.randi_range(a, b)

func randf_range(a: float, b: float) -> float:
	return gameplay.randf_range(a, b)

func randfn(mean: float, dev: float) -> float:
	return gameplay.randfn(mean, dev)

## Weighted pick from a Dictionary {key: weight}. Returns a key.
func weighted_pick(weights: Dictionary):
	var total := 0.0
	for w in weights.values():
		total += float(w)
	if total <= 0.0:
		return weights.keys()[0]
	var roll := gameplay.randf() * total
	var acc := 0.0
	for k in weights.keys():
		acc += float(weights[k])
		if roll <= acc:
			return k
	return weights.keys()[weights.size() - 1]

## Weighted pick on the deterministic content stream.
func content_weighted_pick(weights: Dictionary):
	var total := 0.0
	for w in weights.values():
		total += float(w)
	var roll := content.randf() * total
	var acc := 0.0
	for k in weights.keys():
		acc += float(weights[k])
		if roll <= acc:
			return k
	return weights.keys()[weights.size() - 1]
