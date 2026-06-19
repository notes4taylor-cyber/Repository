extends ScreenBase
## Profile / Reputation: collector title, reputation categories, achievements.

var _body: VBoxContainer

func build() -> void:
	var sc := UI.scroll()
	add_child(sc)
	_body = UI.vbox(12)
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_body)

func refresh() -> void:
	if _body == null:
		return
	clear_children(_body)
	_body.add_child(UI.label("Collector Profile", 24, UI.COL_GOLD))
	_body.add_child(UI.label(Reputation.title(), 20, UI.COL_ACCENT))

	# Stats
	var stats := UI.panel(UI.COL_PANEL2)
	var sv := UI.vbox(4)
	stats.add_child(sv)
	sv.add_child(UI.label("Total Prestige: %s P" % UI.money(PrestigeCalc.total_prestige()), 14))
	sv.add_child(UI.label("Unique cards: %d   •   Total cards: %d" % [Game.unique_card_count(), Game.collection.size()], 14))
	sv.add_child(UI.label("Badges earned: %d   •   Achievements: %d / %d" % [Badges.total_badges_earned(), Achievements.count_unlocked(), Achievements.DEFS.size()], 14))
	sv.add_child(UI.label("Day: %d" % Game.day, 14))
	_body.add_child(stats)

	# Reputation breakdown
	_body.add_child(UI.label("Reputation", 18, UI.COL_ACCENT))
	var maxv := 1.0
	for c in Reputation.CATEGORIES:
		maxv = maxf(maxv, Reputation.points.get(c, 0.0))
	for c in Reputation.CATEGORIES:
		var val: float = Reputation.points.get(c, 0.0)
		var row := UI.vbox(2)
		var h := UI.hbox(8)
		h.add_child(UI.label(c, 13, UI.COL_TEXT))
		h.add_child(UI.spacer())
		h.add_child(UI.label("%s (%s)" % [Reputation.tier_for(val), UI.money(val)], 12, UI.COL_MUTED))
		row.add_child(h)
		var bar := ProgressBar.new()
		bar.min_value = 0
		bar.max_value = maxv
		bar.value = val
		bar.show_percentage = false
		bar.custom_minimum_size = Vector2(0, 8)
		row.add_child(bar)
		_body.add_child(row)

	# Achievements
	_body.add_child(UI.label("Achievements", 18, UI.COL_ACCENT))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	for d in Achievements.DEFS:
		var unlocked: bool = Achievements.is_unlocked(d["id"])
		var p := UI.panel(UI.COL_PANEL2 if unlocked else UI.COL_PANEL)
		var v := UI.vbox(2)
		p.add_child(v)
		v.add_child(UI.label(("✓ " if unlocked else "• ") + d["name"], 14, UI.COL_GOOD if unlocked else UI.COL_MUTED))
		v.add_child(UI.label(d["desc"], 11, UI.COL_MUTED))
		grid.add_child(p)
	_body.add_child(grid)
