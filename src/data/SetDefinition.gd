class_name SetDefinition
extends RefCounted
## Definition of a Season 1 set and its ordered checklist.

var id: String              # e.g. "S1_ARC"
var name: String            # e.g. "Arcane Origins"
var theme: String           # flavor theme string
var factions: Array = []    # Array[String] factions present in this set
var card_ids: Array = []    # ordered Array[String] of CardDefinition ids
var release_day: int = 0    # in-game day this set "released" (older = more age value)

func size() -> int:
	return card_ids.size()
