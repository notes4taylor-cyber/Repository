class_name CardInstance
extends RefCounted
## A specific owned copy of a card. Every copy is tracked individually so that
## selling / grading / trading / displaying never touches the wrong duplicate.

var uid: int = 0            # unique within a save file
var card_id: String         # -> CardDefinition.id
var variant: int = Enums.Variant.BASE
var condition: int = Enums.Condition.EXCELLENT
var grade: int = 0          # 0 = ungraded (raw), else 1..10
var graded: bool = false
var serial_index: int = 0   # for serialized / 1-of-1 (e.g. 14)
var serial_max: int = 0     # for serialized / 1-of-1 (e.g. 100)
var acquired_seq: int = 0   # monotonically increasing acquisition order (newest sort)
var favorite: bool = false

func is_serialized() -> bool:
	return variant == Enums.Variant.SERIALIZED or variant == Enums.Variant.ONEOFONE

func is_oneofone() -> bool:
	return variant == Enums.Variant.ONEOFONE

func effective_rarity_for(def: CardDefinition) -> int:
	return Enums.effective_rarity(def.rarity, variant)

## "014/100", "1/1", or "" when not serialized.
func serial_label() -> String:
	if serial_max <= 0:
		return ""
	if variant == Enums.Variant.ONEOFONE:
		return "1/1"
	var width := str(serial_max).length()
	return str(serial_index).pad_zeros(width) + "/" + str(serial_max)

func to_dict() -> Dictionary:
	return {
		"uid": uid, "card_id": card_id, "variant": variant, "condition": condition,
		"grade": grade, "graded": graded, "serial_index": serial_index,
		"serial_max": serial_max, "acquired_seq": acquired_seq, "favorite": favorite,
	}

static func from_dict(d: Dictionary) -> CardInstance:
	var c := CardInstance.new()
	c.uid = int(d.get("uid", 0))
	c.card_id = String(d.get("card_id", ""))
	c.variant = int(d.get("variant", Enums.Variant.BASE))
	c.condition = int(d.get("condition", Enums.Condition.EXCELLENT))
	c.grade = int(d.get("grade", 0))
	c.graded = bool(d.get("graded", false))
	c.serial_index = int(d.get("serial_index", 0))
	c.serial_max = int(d.get("serial_max", 0))
	c.acquired_seq = int(d.get("acquired_seq", 0))
	c.favorite = bool(d.get("favorite", false))
	return c
