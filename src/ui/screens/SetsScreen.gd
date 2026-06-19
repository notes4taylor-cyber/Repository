extends ScreenBase
## Sets & Badges: completion progress and earned badge tiers per set.

var _body: VBoxContainer

func build() -> void:
	var sc := UI.scroll()
	add_child(sc)
	_body = UI.vbox(10)
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_body)

func refresh() -> void:
	if _body == null:
		return
	clear_children(_body)
	_body.add_child(UI.label("Season 1 — Sets & Badges", 24, UI.COL_GOLD))
	_body.add_child(UI.label("Total badges earned: %d" % Badges.total_badges_earned(), 14, UI.COL_MUTED))

	for set_id in ContentDB.set_order:
		_body.add_child(_set_panel(set_id))

func _set_panel(set_id: String) -> PanelContainer:
	var set_def := ContentDB.get_set(set_id)
	var rep := Badges.set_report(set_id)
	var p := UI.panel(UI.COL_PANEL2)
	var v := UI.vbox(6)
	p.add_child(v)

	var head := UI.hbox(8)
	head.add_child(UI.label(set_def.name, 18, UI.COL_TEXT))
	head.add_child(UI.label("(%d cards • %s)" % [set_def.size(), set_def.theme], 12, UI.COL_MUTED))
	head.add_child(UI.spacer())
	head.add_child(UI.button("View in Binder", goto.bind("collection")))
	v.add_child(head)

	v.add_child(_progress_line("Base checklist", rep["base_pct"], rep["base_owned"], rep["total"]))
	v.add_child(_progress_line("Holo-or-better", rep["holo_pct"], rep["holo_owned"], rep["total"]))
	v.add_child(_progress_line("High-grade (9+)", rep["mythic_pct"], rep["mythic_owned"], rep["total"]))

	# Badge tier chips
	var chips := UI.hbox(6)
	for tier in Badges.TIER_ORDER:
		var earned: bool = rep["tiers"][tier]
		var chip := UI.panel(Badges.tier_color(tier) if earned else UI.COL_PANEL, 6)
		var lbl := UI.label(tier.capitalize(), 12, Color.BLACK if earned else UI.COL_MUTED)
		chip.add_child(lbl)
		chips.add_child(chip)
	v.add_child(chips)
	return p

func _progress_line(label: String, pct: float, owned: int, total: int) -> VBoxContainer:
	var v := UI.vbox(2)
	var h := UI.hbox(8)
	h.add_child(UI.label(label, 13, UI.COL_MUTED))
	h.add_child(UI.spacer())
	h.add_child(UI.label("%d%% (%d/%d)" % [int(pct * 100), owned, total], 13, UI.COL_TEXT))
	v.add_child(h)
	var bar := ProgressBar.new()
	bar.min_value = 0.0
	bar.max_value = 1.0
	bar.value = pct
	bar.show_percentage = false
	bar.custom_minimum_size = Vector2(0, 10)
	v.add_child(bar)
	return v
