extends ScreenBase
## Display Room: showcase favorite cards, sealed shelf, featured card and a
## favorite set badge. Displayed items grant a small PC bonus.

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
	_body.add_child(UI.label("Display Room", 24, UI.COL_GOLD))

	var slots_used := Game.display_card_uids.size()
	var slots_max := Game.display_slots_unlocked()
	_body.add_child(UI.label("Display slots: %d / %d   •   Display PC bonus: %s" % [slots_used, slots_max, UI.money(Game.display_bonus_pc())], 13, UI.COL_MUTED))
	_body.add_child(UI.label("Add cards from the Collection screen (open a card's Details, then 'Display').", 12, UI.COL_MUTED))

	# Featured
	var featured := Game.get_instance(Game.featured_uid) if Game.featured_uid >= 0 else null
	_body.add_child(UI.label("Featured Card", 18, UI.COL_ACCENT))
	if featured != null:
		_body.add_child(UI.card_tile(featured))
	else:
		_body.add_child(UI.label("None featured yet.", 13, UI.COL_MUTED))

	# Displayed cards
	_body.add_child(UI.label("On Display", 18, UI.COL_ACCENT))
	if Game.display_card_uids.is_empty():
		_body.add_child(UI.label("Nothing on display.", 13, UI.COL_MUTED))
	else:
		var grid := GridContainer.new()
		grid.columns = 4
		grid.add_theme_constant_override("h_separation", 8)
		grid.add_theme_constant_override("v_separation", 8)
		for uid in Game.display_card_uids:
			var inst := Game.get_instance(uid)
			if inst == null:
				continue
			var cell := UI.vbox(2)
			cell.add_child(UI.card_tile(inst))
			var btns := UI.hbox(4)
			btns.add_child(UI.button("Feature", func(): Game.set_featured(uid); refresh()))
			btns.add_child(UI.button("Remove", func(): Game.toggle_display(uid); refresh()))
			cell.add_child(btns)
			grid.add_child(cell)
		_body.add_child(grid)

	# Top 5 cards
	_body.add_child(UI.label("Top 5 Cards", 18, UI.COL_ACCENT))
	var sorted := Game.collection.duplicate()
	sorted.sort_custom(func(a, b): return PrestigeCalc.card_value(a) > PrestigeCalc.card_value(b))
	if sorted.is_empty():
		_body.add_child(UI.label("No cards yet.", 13, UI.COL_MUTED))
	else:
		var grid2 := GridContainer.new()
		grid2.columns = 5
		grid2.add_theme_constant_override("h_separation", 8)
		for i in range(mini(5, sorted.size())):
			grid2.add_child(UI.card_tile(sorted[i]))
		_body.add_child(grid2)

	# Sealed shelf
	_body.add_child(UI.label("Sealed Shelf", 18, UI.COL_ACCENT))
	if Game.sealed_inventory.is_empty():
		_body.add_child(UI.label("No sealed product owned.", 13, UI.COL_MUTED))
	else:
		var shelf := UI.vbox(4)
		for pid in Game.sealed_inventory.keys():
			var prod := ContentDB.get_product(pid)
			var cb := CheckBox.new()
			cb.text = "%s x%d (display on shelf)" % [prod.name, Game.sealed_inventory[pid]]
			cb.button_pressed = Game.display_sealed.has(pid)
			cb.toggled.connect(_toggle_sealed.bind(pid))
			shelf.add_child(cb)
		_body.add_child(shelf)

	# Favorite set badge
	_body.add_child(UI.label("Favorite Set Badge", 18, UI.COL_ACCENT))
	var opt := OptionButton.new()
	opt.add_item("None")
	for i in range(ContentDB.set_order.size()):
		opt.add_item(ContentDB.get_set(ContentDB.set_order[i]).name)
	# select current
	if Game.display_badge_set != "":
		var idx := ContentDB.set_order.find(Game.display_badge_set)
		if idx >= 0:
			opt.select(idx + 1)
	opt.item_selected.connect(func(i):
		Game.display_badge_set = "" if i == 0 else ContentDB.set_order[i - 1]
		Game.on_state_changed()
		refresh())
	_body.add_child(opt)
	if Game.display_badge_set != "":
		var tier := Badges.highest_tier(Game.display_badge_set)
		_body.add_child(UI.label("Highest badge: %s" % (tier.capitalize() if tier != "" else "none yet"), 13, Badges.tier_color(tier) if tier != "" else UI.COL_MUTED))

	# Rarest pull + stats
	if not sorted.is_empty():
		var rarest: CardInstance = sorted[0]
		var rdef := ContentDB.get_card(rarest.card_id)
		_body.add_child(UI.label("Rarest Pull: %s — %s %s" % [rdef.name, Enums.variant_name(rarest.variant), Enums.rarity_name(Enums.effective_rarity(rdef.rarity, rarest.variant))], 14, UI.COL_GOLD))
	_body.add_child(UI.label("Collection: %d unique / %d total • %s Total Prestige" % [Game.unique_card_count(), Game.collection.size(), UI.money(PrestigeCalc.total_prestige())], 13, UI.COL_MUTED))

func _toggle_sealed(pressed: bool, pid: String) -> void:
	if pressed:
		if not Game.display_sealed.has(pid):
			Game.display_sealed.append(pid)
	else:
		Game.display_sealed.erase(pid)
	Game.on_state_changed()
