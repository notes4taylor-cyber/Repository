extends ScreenBase
## Settings: audio, accessibility, manual save, delete save, build info.

func build() -> void:
	var root := UI.vbox(12)
	add_child(root)
	root.add_child(UI.label("Settings", 24, UI.COL_GOLD))

	var p := UI.panel(UI.COL_PANEL2)
	var v := UI.vbox(10)
	p.add_child(v)

	# Volume
	var vol := UI.hbox(8)
	vol.add_child(UI.label("Master volume", 14))
	var s := HSlider.new()
	s.min_value = 0.0
	s.max_value = 1.0
	s.step = 0.05
	s.value = Game.settings.get("master_volume", 1.0)
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.value_changed.connect(func(val):
		Game.settings["master_volume"] = val
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(0.0001, val))))
	vol.add_child(s)
	v.add_child(vol)

	v.add_child(_check("Reduce flashing effects", "reduce_flashing"))
	v.add_child(_check("Fast reveal (skip pack animations)", "fast_reveal"))
	root.add_child(p)

	# Save management
	var sp := UI.panel(UI.COL_PANEL2)
	var sv := UI.vbox(8)
	sp.add_child(sv)
	sv.add_child(UI.label("Save Data", 16, UI.COL_ACCENT))
	var info := "No save yet."
	if SaveManager.last_save_time > 0:
		info = "Last save: %s (%s)" % [Time.get_datetime_string_from_unix_time(SaveManager.last_save_time), SaveManager.last_save_reason]
	sv.add_child(UI.label(info, 12, UI.COL_MUTED))
	var sb := UI.hbox(8)
	sb.add_child(UI.button("Manual Save", func():
		SaveManager.save_game(Game, "manual")
		toast("Game saved.")
		refresh(), true))
	sb.add_child(UI.button("Delete Save", _delete_save))
	sv.add_child(sb)
	root.add_child(sp)

	# Info
	root.add_child(UI.label("Grader: %s  •  Build %s" % [Balance.GRADER_NAME, ProjectSettings.get_setting("application/config/version", "0.1.0")], 12, UI.COL_MUTED))
	root.add_child(UI.label("World seed: %d" % Game.world_seed, 12, UI.COL_MUTED))

func _check(text: String, key: String) -> CheckBox:
	var cb := CheckBox.new()
	cb.text = text
	cb.button_pressed = Game.settings.get(key, false)
	cb.toggled.connect(func(p): Game.settings[key] = p)
	return cb

func _delete_save() -> void:
	confirm("Delete your save permanently? This cannot be undone.", func():
		SaveManager.delete_save()
		toast("Save deleted.")
		main.show_menu())
