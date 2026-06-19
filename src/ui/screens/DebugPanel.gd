extends ScreenBase
## Debug / Dev tools. Hidden behind the debug flag (toggle with F1).

var _log: RichTextLabel

func build() -> void:
	var root := UI.vbox(8)
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(root)
	root.add_child(UI.label("Debug / Dev Tools", 24, UI.COL_BAD))
	root.add_child(UI.label("For testing only. Toggle the Debug nav button with F1.", 12, UI.COL_MUTED))

	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	root.add_child(grid)

	_add(grid, "Add 1,000 PL", func(): Game.debug_add_pl(1000.0); _print("Added 1,000 PL."))
	_add(grid, "Add 50,000 PL", func(): Game.debug_add_pl(50000.0); _print("Added 50,000 PL."))
	_add(grid, "Generate Random Pack", func():
		var r := Game.debug_open_random()
		_print("Opened random product: %s (+%s PC)." % [r.get("reason", "?"), UI.money(r.get("gain", 0.0))]))
	_add(grid, "Simulate 10k Variant Rolls", _sim_pulls)
	_add(grid, "Add 100 Random Packs", _open_100)
	_add(grid, "Force Legendary", func(): _force("legendary"))
	_add(grid, "Force Serialized", func(): _force("serialized"))
	_add(grid, "Force 1-of-1", func(): _force("oneofone"))
	_add(grid, "Complete First Set", func():
		var n := Game.debug_complete_set(ContentDB.set_order[0])
		_print("Completed %s: added %d cards." % [ContentDB.get_set(ContentDB.set_order[0]).name, n]))
	_add(grid, "Reset Market Trends", func():
		Market.reset(); Market.refresh(); Game.on_state_changed()
		_print("Market reset. " + Market.trend_summary()))
	_add(grid, "Recalculate Prestige", func():
		Game.on_state_changed()
		_print("Total P = %s (PC %s + PL %s)" % [UI.money(PrestigeCalc.total_prestige()), UI.money(PrestigeCalc.collection_prestige()), UI.money(Game.pl)]))
	_add(grid, "Validate Save File", func():
		var probs := SaveManager.validate_save()
		_print("Save validation: " + ("OK" if probs.is_empty() else "; ".join(probs))))
	_add(grid, "Validate Unique Cards", func():
		var probs := SaveManager.validate_unique_constraints(Game)
		_print("Unique constraints: " + ("OK (no duplicate 1/1s or serials)" if probs.is_empty() else "; ".join(probs))))
	_add(grid, "Validate Balance Tables", func():
		var probs := Balance.validate()
		_print("Balance tables: " + ("OK (odds sum to 1.0)" if probs.is_empty() else "; ".join(probs))))

	root.add_child(UI.label("Output", 16, UI.COL_ACCENT))
	_log = RichTextLabel.new()
	_log.bbcode_enabled = false
	_log.scroll_following = true
	_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_log.custom_minimum_size = Vector2(0, 200)
	_log.add_theme_color_override("default_color", UI.COL_TEXT)
	root.add_child(_log)

func _add(grid: GridContainer, text: String, cb: Callable) -> void:
	grid.add_child(UI.button(text, cb))

func _print(text: String) -> void:
	if _log:
		_log.add_text(text + "\n")

func _force(kind: String) -> void:
	var inst := Game.debug_force_pull(kind)
	if inst == null:
		_print("Could not force %s (none available)." % kind)
		return
	var def := ContentDB.get_card(inst.card_id)
	_print("Forced %s: %s %s %s — %s PL" % [kind, def.name, Enums.variant_name(inst.variant), inst.serial_label(), UI.money(PrestigeCalc.card_value(inst))])

func _sim_pulls() -> void:
	var report := PackEngine.simulate_distribution(10000, 1.0)
	var lines: String = "Variant distribution over %d rolls:" % report["samples"]
	for v in report["variants"].keys():
		var n: int = report["variants"][v]
		lines += "\n  %s: %d (%.3f%%)" % [Enums.variant_name(v), n, 100.0 * n / report["samples"]]
	_print(lines)

func _open_100() -> void:
	var total_cards := 0
	var total_value := 0.0
	for _i in range(100):
		var set_id: String = ContentDB.set_order[RNGService.randi_range(0, ContentDB.set_order.size() - 1)]
		var pulls := PackEngine.generate_pulls(set_id, 6, 1.0)
		Game.debug_commit(pulls)
		for inst in pulls:
			total_cards += 1
			total_value += PrestigeCalc.card_value(inst)
	Game.autosave("debug_100")
	_print("Opened 100 packs: %d cards, +%s PC." % [total_cards, UI.money(total_value)])
