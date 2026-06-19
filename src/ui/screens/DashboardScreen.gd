extends ScreenBase
## Dashboard: at-a-glance overview + quick actions.

var _body: VBoxContainer

func build() -> void:
	var sc := UI.scroll()
	add_child(sc)
	_body = UI.vbox(12)
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_body)

func _enter_tree() -> void:
	if not Game.changed.is_connected(refresh):
		Game.changed.connect(refresh)

func _exit_tree() -> void:
	if Game.changed.is_connected(refresh):
		Game.changed.disconnect(refresh)

func refresh() -> void:
	if _body == null:
		return
	clear_children(_body)

	_body.add_child(UI.label("Dashboard", 26, UI.COL_GOLD))

	# Prestige summary row
	var row := UI.hbox(12)
	var pc := PrestigeCalc.collection_prestige()
	row.add_child(_stat_card("Total Prestige", UI.money(pc + Game.pl) + " P", UI.COL_GOLD))
	row.add_child(_stat_card("Collection (PC)", UI.money(pc), UI.COL_ACCENT))
	row.add_child(_stat_card("Liquid (PL)", UI.money(Game.pl), UI.COL_GOOD))
	row.add_child(_stat_card("Unique / Total", "%d / %d" % [Game.unique_card_count(), Game.collection.size()], UI.COL_TEXT))
	_body.add_child(row)

	# Market trend + milestone
	var info := UI.panel(UI.COL_PANEL2)
	var iv := UI.vbox(6)
	info.add_child(iv)
	iv.add_child(UI.label("Active Market Trends", 16, UI.COL_ACCENT))
	iv.add_child(UI.wrap_label(Market.trend_summary(), 14))
	iv.add_child(UI.label("Next milestone: " + Game.next_milestone_text(), 13, UI.COL_MUTED))
	_body.add_child(info)

	# Best card
	var best := Game.best_card_instance()
	if best != null:
		var bc := UI.panel(UI.COL_PANEL2)
		var bh := UI.hbox(12)
		bc.add_child(bh)
		var bv := UI.vbox(4)
		bv.add_child(UI.label("Best Card", 16, UI.COL_ACCENT))
		bv.add_child(UI.label("Top value: %s PL" % UI.money(PrestigeCalc.card_value(best)), 13, UI.COL_GOOD))
		bh.add_child(bv)
		bh.add_child(UI.spacer())
		bh.add_child(UI.card_tile(best))
		_body.add_child(bc)

	# Quick actions
	var actions := UI.hbox(8)
	actions.add_child(UI.button("Go to Shop", goto.bind("shop"), true))
	actions.add_child(UI.button("Open Packs", goto.bind("open")))
	actions.add_child(UI.button("Collection", goto.bind("collection")))
	actions.add_child(UI.button("Advance Day", func(): Game.advance_day()))
	_body.add_child(actions)

	# Recent pulls
	_body.add_child(UI.label("Recent Notable Pulls", 18, UI.COL_TEXT))
	if Game.recent_pulls.is_empty():
		_body.add_child(UI.label("Open some packs to see your highlights here.", 14, UI.COL_MUTED))
	else:
		var grid := GridContainer.new()
		grid.columns = 2
		grid.add_theme_constant_override("h_separation", 8)
		grid.add_theme_constant_override("v_separation", 8)
		for entry in Game.recent_pulls:
			grid.add_child(_pull_row(entry))
		_body.add_child(grid)

func _stat_card(title: String, value: String, color: Color) -> PanelContainer:
	var p := UI.panel(UI.COL_PANEL2)
	p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var v := UI.vbox(2)
	v.add_child(UI.label(title, 12, UI.COL_MUTED))
	v.add_child(UI.label(value, 22, color))
	p.add_child(v)
	return p

func _pull_row(entry: Dictionary) -> PanelContainer:
	var p := UI.panel(UI.COL_PANEL if not entry.get("grail", false) else UI.COL_PANEL2)
	var h := UI.hbox(8)
	p.add_child(h)
	var v := UI.vbox(2)
	var col: Color = UI.COL_GOLD if entry.get("grail", false) else UI.COL_TEXT
	v.add_child(UI.label(entry.get("label", "?"), 15, col))
	v.add_child(UI.label(entry.get("sub", ""), 12, UI.COL_MUTED))
	h.add_child(v)
	h.add_child(UI.spacer())
	var tag := "NEW" if entry.get("new", false) else "DUP"
	h.add_child(UI.label(tag, 12, UI.COL_GOOD if entry.get("new", false) else UI.COL_MUTED))
	h.add_child(UI.label("%s PL" % UI.money(entry.get("value", 0.0)), 14, UI.COL_GOOD))
	return p
