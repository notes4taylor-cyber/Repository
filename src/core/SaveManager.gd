extends Node
## SaveManager (autoload)
## Versioned local JSON save/load with migration hook + validation utilities.

signal saved(reason)

const SAVE_PATH := "user://prestige_packs_save.json"
const SAVE_VERSION := 1

var last_save_reason: String = ""
var last_save_time: int = 0

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func save_game(game, reason: String = "manual") -> bool:
	var payload := {
		"version": SAVE_VERSION,
		"saved_at": int(Time.get_unix_time_from_system()),
		"reason": reason,
		"data": game.to_dict(),
	}
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null:
		push_error("[SaveManager] Could not open save file for writing.")
		return false
	f.store_string(JSON.stringify(payload))
	f.close()
	last_save_reason = reason
	last_save_time = payload["saved_at"]
	saved.emit(reason)
	return true

func load_game(game) -> bool:
	if not has_save():
		return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null:
		push_error("[SaveManager] Could not open save file for reading.")
		return false
	var text := f.get_as_text()
	f.close()
	var parsed = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("[SaveManager] Save file is corrupt.")
		return false
	var payload: Dictionary = parsed
	var version := int(payload.get("version", 0))
	var data: Dictionary = payload.get("data", {})
	data = _migrate(data, version)
	last_save_reason = String(payload.get("reason", ""))
	last_save_time = int(payload.get("saved_at", 0))
	game.from_dict(data)
	return true

## Migration entry point for future save format changes.
func _migrate(data: Dictionary, from_version: int) -> Dictionary:
	# v0/legacy -> current. No migrations needed yet; structured for the future.
	if from_version == SAVE_VERSION:
		return data
	# Example pattern:
	# if from_version < 1: data = _migrate_v0_to_v1(data)
	return data

func delete_save() -> bool:
	if not has_save():
		return false
	var err := DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
	if err != OK:
		# Fallback for user:// path removal.
		var d := DirAccess.open("user://")
		if d != null:
			d.remove("prestige_packs_save.json")
	return true

# ---------------------------------------------------------------------------
# Validation utilities (used by the debug panel)
# ---------------------------------------------------------------------------
func validate_save() -> Array:
	var problems: Array = []
	if not has_save():
		problems.append("No save file present.")
		return problems
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		problems.append("Save file is not valid JSON.")
		return problems
	for key in ["version", "data"]:
		if not parsed.has(key):
			problems.append("Missing top-level key: " + key)
	if parsed.has("data"):
		for key in ["pl", "collection", "world_seed"]:
			if not parsed["data"].has(key):
				problems.append("Missing data key: " + key)
	return problems

## Verify unique-card invariants on the live Game state.
func validate_unique_constraints(game) -> Array:
	var problems: Array = []
	var oneofone_seen := {}
	var serial_seen := {}   # "card_id:index" -> true
	for inst in game.collection:
		var def := ContentDB.get_card(inst.card_id)
		if def == null:
			problems.append("Instance %d references unknown card %s" % [inst.uid, inst.card_id])
			continue
		if inst.variant == Enums.Variant.ONEOFONE:
			if oneofone_seen.has(inst.card_id):
				problems.append("Duplicate 1/1 for card %s" % inst.card_id)
			oneofone_seen[inst.card_id] = true
		if inst.variant == Enums.Variant.SERIALIZED:
			if inst.serial_index < 1 or inst.serial_index > inst.serial_max:
				problems.append("Serial out of range on %s: %d/%d" % [inst.card_id, inst.serial_index, inst.serial_max])
			var key := "%s:%d" % [inst.card_id, inst.serial_index]
			if serial_seen.has(key):
				problems.append("Duplicate serial %s" % key)
			serial_seen[key] = true
	return problems
