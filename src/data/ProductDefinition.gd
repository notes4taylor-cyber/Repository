class_name ProductDefinition
extends RefCounted
## Sealed product sold in the shop.

var id: String
var name: String
var set_id: String
var kind: String            # "pack","bundle","blaster","booster_box","collector_box","case"
var price: float
var packs: int              # number of packs contained
var cards_per_pack: int
var luck: float = 1.0       # multiplier applied to rare-variant odds (premium product)
var description: String = ""

func total_cards() -> int:
	return packs * cards_per_pack

func to_dict() -> Dictionary:
	return {
		"id": id, "name": name, "set_id": set_id, "kind": kind,
		"price": price, "packs": packs, "cards_per_pack": cards_per_pack,
		"luck": luck, "description": description,
	}
