extends Node
## ContentDB (autoload)
## Generates and stores all immutable game definitions: Season 1 sets, their
## (large, procedurally-generated) card checklists, and shop products.
## Generation is deterministic (Balance.CONTENT_SEED) so the checklist is stable
## across saves and runs. Per-save uniqueness (1/1s, market) lives in Game.

var sets: Dictionary = {}          # set_id -> SetDefinition
var set_order: Array = []          # ordered Array[String] of set ids
var cards: Dictionary = {}         # card_id -> CardDefinition
var products: Dictionary = {}      # product_id -> ProductDefinition
var product_order: Array = []      # ordered Array[String] of product ids

# Season 1 sets: id suffix, display name, theme, faction pool.
const SET_BLUEPRINTS := [
	["ARC", "Arcane Origins", "Founding spellcraft", ["Mages", "Spirits", "Runes"]],
	["NEO", "Neon Beasts", "Synthwave fauna", ["Beasts", "Dragons", "Cyber"]],
	["REL", "Relic Realms", "Ancient ruins", ["Relics", "Guardians", "Tombs"]],
	["SHA", "Shadow Circuit", "Dark machinery", ["Shadow", "Cyber", "Phantoms"]],
	["MYT", "Mythic Grove", "Living wilds", ["Beasts", "Spirits", "Druids"]],
	["CHR", "Chrome Coliseum", "Arena champions", ["Gladiators", "Cyber", "Titans"]],
	["AST", "Astral Siege", "Cosmic war", ["Celestials", "Dragons", "Void"]],
	["ETR", "Eternal Vault", "Sealed treasures", ["Relics", "Titans", "Runes"]],
]

# Word banks for procedural card names.
const NAME_PREFIX := ["Ancient", "Blazing", "Cursed", "Divine", "Eternal", "Frozen",
	"Gilded", "Hidden", "Iron", "Jade", "Lunar", "Molten", "Noble", "Obsidian",
	"Primal", "Radiant", "Savage", "Twilight", "Umbral", "Verdant", "Wandering", "Zephyr"]
const NAME_NOUN := ["Sentinel", "Warden", "Drake", "Oracle", "Colossus", "Phantom",
	"Seraph", "Golem", "Reaver", "Sovereign", "Familiar", "Harbinger", "Construct",
	"Wyrm", "Champion", "Specter", "Behemoth", "Acolyte", "Marauder", "Paragon",
	"Effigy", "Revenant", "Templar", "Juggernaut"]
const NAME_SUFFIX := ["of Ash", "of the Deep", "Prime", "Reborn", "of Storms",
	"Ascendant", "of Echoes", "the Bound", "of Ruin", "the Eternal", "of Dawn", ""]

func _ready() -> void:
	var problems := Balance.validate()
	for p in problems:
		push_warning("[Balance] " + p)
	_generate()

func _generate() -> void:
	RNGService.reset_content()
	var rng := RNGService.content
	for i in range(SET_BLUEPRINTS.size()):
		var bp = SET_BLUEPRINTS[i]
		var set_def := SetDefinition.new()
		set_def.id = "S1_" + bp[0]
		set_def.name = bp[1]
		set_def.theme = bp[2]
		set_def.factions = bp[3]
		# Older sets (earlier index) "released" earlier -> more age value.
		set_def.release_day = -(SET_BLUEPRINTS.size() - i) * 7
		var count := Balance.SET_BASE_SIZE + i * Balance.SET_SIZE_GROWTH
		_generate_cards_for_set(set_def, count, rng)
		sets[set_def.id] = set_def
		set_order.append(set_def.id)
	_generate_products()

func _generate_cards_for_set(set_def: SetDefinition, count: int, rng: RandomNumberGenerator) -> void:
	# Distribute rarities across the checklist according to the split.
	var rarity_counts := {}
	var assigned := 0
	for r in Balance.SET_RARITY_SPLIT.keys():
		var n := int(round(Balance.SET_RARITY_SPLIT[r] * count))
		rarity_counts[r] = n
		assigned += n
	# Fix rounding drift by adjusting commons.
	rarity_counts[Enums.Rarity.COMMON] += (count - assigned)

	var rarity_pool: Array = []
	for r in rarity_counts.keys():
		for _j in range(rarity_counts[r]):
			rarity_pool.append(r)
	# Shuffle deterministically so rarities are mixed through the numbering.
	_det_shuffle(rarity_pool, rng)

	for idx in range(rarity_pool.size()):
		var rarity: int = rarity_pool[idx]
		var card := CardDefinition.new()
		card.number = idx + 1
		card.id = "%s_%03d" % [set_def.id, card.number]
		card.set_id = set_def.id
		card.faction = set_def.factions[rng.randi() % set_def.factions.size()]
		card.name = _make_name(rng)
		card.rarity = rarity
		var vr: Vector2 = Balance.RARITY_BASE_VALUE[rarity]
		card.base_value = snappedf(rng.randf_range(vr.x, vr.y), 0.5)
		card.demand_base = clampf(rng.randf_range(0.2, 0.8) + _rarity_demand_bias(rarity), 0.0, 1.0)
		card.hype_base = clampf(rng.randf_range(0.1, 0.6), 0.0, 1.0)
		card.age_modifier = 1.0
		card.available_variants = _variants_for_rarity(rarity)
		if card.available_variants.has(Enums.Variant.SERIALIZED):
			card.serial_run = Balance.SERIAL_RUNS[rng.randi() % Balance.SERIAL_RUNS.size()]
		cards[card.id] = card
		set_def.card_ids.append(card.id)

func _rarity_demand_bias(rarity: int) -> float:
	match rarity:
		Enums.Rarity.LEGENDARY: return 0.2
		Enums.Rarity.RARE: return 0.1
		_: return 0.0

func _variants_for_rarity(rarity: int) -> Array:
	# Common cards have fewer chase finishes; rarer cards unlock more.
	var v := [Enums.Variant.BASE, Enums.Variant.HOLO]
	if rarity >= Enums.Rarity.UNCOMMON:
		v.append(Enums.Variant.RAINBOW)
	if rarity >= Enums.Rarity.RARE:
		v.append_array([Enums.Variant.GOLD, Enums.Variant.SHADOW])
	if rarity >= Enums.Rarity.RARE:
		v.append(Enums.Variant.SIGNATURE)
	# Serialized & 1/1 only on Rare+ cards (chase cards).
	if rarity >= Enums.Rarity.RARE:
		v.append_array([Enums.Variant.SERIALIZED, Enums.Variant.ONEOFONE])
	return v

func _make_name(rng: RandomNumberGenerator) -> String:
	var p: String = NAME_PREFIX[rng.randi() % NAME_PREFIX.size()]
	var n: String = NAME_NOUN[rng.randi() % NAME_NOUN.size()]
	var s: String = NAME_SUFFIX[rng.randi() % NAME_SUFFIX.size()]
	var name := p + " " + n
	if s != "":
		name += " " + s
	return name

func _det_shuffle(arr: Array, rng: RandomNumberGenerator) -> void:
	for i in range(arr.size() - 1, 0, -1):
		var j := rng.randi() % (i + 1)
		var tmp = arr[i]
		arr[i] = arr[j]
		arr[j] = tmp

# ---------------------------------------------------------------------------
# Products: one full ladder per set.
# ---------------------------------------------------------------------------
func _generate_products() -> void:
	# kind, label, packs, cards_per_pack, luck
	var ladder := [
		["pack", "Single Pack", 1, 6, 1.0],
		["bundle", "3-Pack Bundle", 3, 6, 1.05],
		["blaster", "Blaster Box", 7, 6, 1.15],
		["booster_box", "Booster Box", 24, 6, 1.25],
		["collector_box", "Collector Box", 12, 8, 1.6],
		["case", "Sealed Case", 144, 6, 1.3],
	]
	for set_id in set_order:
		var set_def: SetDefinition = sets[set_id]
		var ev := _expected_pull_value(set_def)   # average realized market value per pull
		for spec in ladder:
			var prod := ProductDefinition.new()
			prod.kind = spec[0]
			prod.name = "%s %s" % [set_def.name, spec[1]]
			prod.set_id = set_id
			prod.packs = spec[2]
			prod.cards_per_pack = spec[3]
			prod.luck = spec[4]
			var markup: float = Balance.PRODUCT_MARKUP.get(prod.kind, 1.1)
			prod.price = snappedf(prod.total_cards() * ev * markup, 5.0)
			prod.price = maxf(prod.price, 10.0)
			prod.id = "%s_%s" % [set_id, prod.kind]
			prod.description = "%d packs x %d cards. Set: %s." % [prod.packs, prod.cards_per_pack, set_def.name]
			products[prod.id] = prod
			product_order.append(prod.id)

## Expected realized market value of a single random pull (used for pricing).
## Weights card selection by pick odds (commons dominate), applies the expected
## finish and condition multipliers, and the average market multiplier.
func _expected_pull_value(set_def: SetDefinition) -> float:
	var tw := 0.0
	var num := 0.0
	for cid in set_def.card_ids:
		var c: CardDefinition = cards[cid]
		var w: float = Balance.RARITY_PICK_WEIGHT.get(c.rarity, 1.0)
		tw += w
		num += w * c.base_value * Balance.RARITY_VALUE_MULT[c.rarity]
	var base_exp := num / maxf(1.0, tw)
	var fin := 0.0
	for v in Balance.VARIANT_ODDS.keys():
		fin += Balance.VARIANT_ODDS[v] * Balance.VARIANT_VALUE_MULT[v]
	var cond := 0.0
	for cc in Balance.CONDITION_ODDS.keys():
		cond += Balance.CONDITION_ODDS[cc] * Balance.CONDITION_VALUE_MULT[cc]
	return base_exp * fin * cond * Balance.MARKET_EV_FACTOR

# ---------------------------------------------------------------------------
# Lookups
# ---------------------------------------------------------------------------
func get_card(card_id: String) -> CardDefinition:
	return cards.get(card_id, null)

func get_set(set_id: String) -> SetDefinition:
	return sets.get(set_id, null)

func get_product(product_id: String) -> ProductDefinition:
	return products.get(product_id, null)

func products_for_set(set_id: String) -> Array:
	var out: Array = []
	for pid in product_order:
		if products[pid].set_id == set_id:
			out.append(products[pid])
	return out

func total_card_count() -> int:
	return cards.size()
