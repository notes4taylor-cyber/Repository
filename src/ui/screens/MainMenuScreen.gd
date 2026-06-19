extends ScreenBase
## Main menu: New Game / Continue / Settings / Quit + version label.

func build() -> void:
	var center := CenterContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(center)

	var box := UI.vbox(14)
	box.custom_minimum_size = Vector2(420, 0)
	center.add_child(box)

	var title := UI.label("PRESTIGE PACKS", 44, UI.COL_GOLD)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	var sub := UI.label("A fictional CCG collecting simulator", 16, UI.COL_MUTED)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(sub)

	box.add_child(_gap(10))

	box.add_child(UI.button("New Game", _on_new, true))
	var cont := UI.button("Continue", _on_continue)
	cont.disabled = not SaveManager.has_save()
	box.add_child(cont)

	# Inline settings
	var sp := UI.panel(UI.COL_PANEL2, 12)
	var sv := UI.vbox(8)
	sp.add_child(sv)
	sv.add_child(UI.label("Settings", 18))
	sv.add_child(_volume_row())
	sv.add_child(_check_row("Reduce flashing effects", "reduce_flashing"))
	sv.add_child(_check_row("Fast reveal (skip animations)", "fast_reveal"))
	box.add_child(sp)

	box.add_child(UI.button("Quit", func(): get_tree().quit()))

	var ver := UI.label("Build %s" % ProjectSettings.get_setting("application/config/version", "0.1.0"), 12, UI.COL_MUTED)
	ver.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(ver)

func _gap(h: int) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(0, h)
	return c

func _volume_row() -> HBoxContainer:
	var h := UI.hbox(8)
	h.add_child(UI.label("Master volume", 14, UI.COL_MUTED))
	var s := HSlider.new()
	s.min_value = 0.0
	s.max_value = 1.0
	s.step = 0.05
	s.value = Game.settings.get("master_volume", 1.0)
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.value_changed.connect(func(v):
		Game.settings["master_volume"] = v
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(0.0001, v))))
	h.add_child(s)
	return h

func _check_row(text: String, key: String) -> CheckBox:
	var cb := CheckBox.new()
	cb.text = text
	cb.button_pressed = Game.settings.get(key, false)
	cb.toggled.connect(func(p): Game.settings[key] = p)
	return cb

func _on_new() -> void:
	if SaveManager.has_save():
		confirm("Start a new game? This overwrites your existing save.", _start_new)
	else:
		_start_new()

func _start_new() -> void:
	Game.new_game()
	SaveManager.save_game(Game, "new_game")
	main.enter_game()

func _on_continue() -> void:
	if SaveManager.load_game(Game):
		main.enter_game()
	else:
		toast("No save found or save was corrupt.")
