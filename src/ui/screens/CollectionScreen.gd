extends ScreenBase
## Collection Binder: filter / sort / search, grouped by card, with a per-card
## details dialog for instance-level actions (sell / grade / display) so the
## correct copy is always the one acted on.

const ROW_CAP := 400

var _search: LineEdit
var _set_opt: OptionButton
var _rarity_opt: OptionButton
var _variant_opt: OptionButton
var _owned_opt: OptionButton
var _graded_opt: OptionButton
var _sort_opt: OptionButton
var _completion: Label
var _list: VBoxContainer
var _dialog: AcceptDialog
var _dialog_box: VBoxContainer
var _dialog_card_id := ""

func build() -> void:
	var root := UI.vbox(8)
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(root)

	root.add_child(UI.label("Collection Binder", 24, UI.COL_GOLD))

	# Row 1: search + sell duplicates
	var r1 := UI.hbox(8)
	_search = LineEdit.new()
	_search.placeholder_text = "Search by name..."
	_search.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_search.text_changed.connect(func(_t): refresh())
	r1.add_child(_search)
	r1.add_child(UI.button("Sell All Duplicates", _sell_dupes))
	root.add_child(r1)

	# Row 2: filters
	var r2 := UI.hbox(8)
	_set_opt = _make_opt(["All Sets"], r2, "Set")
	for sid in ContentDB.set_order:
		_set_opt.add_item(ContentDB.get_set(sid).name)
	_rarity_opt = _make_opt(["All Rarities", "Common", "Uncommon", "Rare", "Legendary"], r2, "Rarity")
	_variant_opt = _make_opt(["All Variants"], r2, "Variant")
	for vn in Enums.VARIANT_NAMES:
		_variant_opt.add_item(vn)
	_owned_opt = _make_opt(["Owned", "Unowned", "All"], r2, "Owned")
	_graded_opt = _make_opt(["Any Grade", "Graded", "Ungraded"], r2, "Graded")
	root.add_child(r2)

	# Row 3: sort + completion
	var r3 := UI.hbox(8)
	_sort_opt = _make_opt(["Value", "Rarity", "Set Number", "Quantity", "Condition", "Grade", "Newest"], r3, "Sort")
	r3.add_child(UI.spacer())
	_completion = UI.label("", 14, UI.COL_ACCENT)
	r3.add_child(_completion)
	root.add_child(r3)

	var sc := UI.scroll()
	root.add_child(sc)
	_list = UI.vbox(6)
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_list)

	_dialog = AcceptDialog.new()
	_dialog.title = "Card Details"
	_dialog.min_size = Vector2(520, 420)
	var dsc := UI.scroll()
	dsc.custom_minimum_size = Vector2(500, 380)
	_dialog_box = UI.vbox(6)
	_dialog_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dsc.add_child(_dialog_box)
	_dialog.add_child(dsc)
	add_child(_dialog)

func _make_opt(items: Array, parent: Control, _label: String) -> OptionButton:
	var o := OptionButton.new()
	for it in items:
		o.add_item(it)
	o.item_selected.connect(func(_i): refresh())
	parent.add_child(o)
	return o

# ===========================================================================
func refresh() -> void:
	if _list == null:
		return
	clear_children(_list)

	# Build owned index.
	var owned := {}   # card_id -> Array[CardInstance]
	for inst in Game.collection:
		if not owned.has(inst.card_id):
			owned[inst.card_id] = []
		owned[inst.card_id].append(inst)

	# Decide which card_ids to consider (by set).
	var set_sel := _set_opt.selected   # 0 = all, else index+? (item 0 is "All")
	var card_ids: Array = []
	if set_sel <= 0:
		for sid in ContentDB.set_order:
			card_ids.append_array(ContentDB.get_set(sid).card_ids)
	else:
		card_ids = ContentDB.get_set(ContentDB.set_order[set_sel - 1]).card_ids.duplicate()

	# Completion label (only when one set selected).
	if set_sel > 0:
		var rep := Badges.set_report(ContentDB.set_order[set_sel - 1])
		_completion.text = "Set completion: %d%% (%d/%d)" % [int(rep["base_pct"] * 100), rep["base_owned"], rep["total"]]
	else:
		_completion.text = "%d unique / %d total cards" % [Game.unique_card_count(), Game.collection.size()]

	# Filter + build display records.
	var records: Array = []
	for cid in card_ids:
		var def := ContentDB.get_card(cid)
		var insts: Array = owned.get(cid, [])
		if not _passes(def, insts):
			continue
		records.append(_record(def, insts))

	_sort_records(records)

	var shown := 0
	for rec in records:
		if shown >= ROW_CAP:
			_list.add_child(UI.label("... %d more hidden. Use filters to narrow results." % (records.size() - shown), 13, UI.COL_MUTED))
			break
		_list.add_child(_row(rec))
		shown += 1
	if records.is_empty():
		_list.add_child(UI.label("No cards match these filters.", 14, UI.COL_MUTED))

func _record(def: CardDefinition, insts: Array) -> Dictionary:
	var best_v := 0.0
	var best_variant := -1
	var best_grade := 0
	var best_cond := 0
	var newest := 0
	for inst in insts:
		var v := PrestigeCalc.card_value(inst)
		if v > best_v:
			best_v = v
			best_variant = inst.variant
		best_grade = maxi(best_grade, inst.grade)
		best_cond = maxi(best_cond, inst.condition)
		newest = maxi(newest, inst.acquired_seq)
	return {
		"def": def, "insts": insts, "qty": insts.size(),
		"best_v": best_v, "best_variant": best_variant,
		"best_grade": best_grade, "best_cond": best_cond, "newest": newest,
	}

func _passes(def: CardDefinition, insts: Array) -> bool:
	var owned := insts.size() > 0
	# owned filter: 0 = Owned, 1 = Unowned, 2 = All
	var of := _owned_opt.selected
	if of == 0 and not owned:
		return false
	if of == 1 and owned:
		return false
	# search
	var q := _search.text.strip_edges().to_lower()
	if q != "" and not def.name.to_lower().contains(q):
		return false
	# rarity (base rarity)
	if _rarity_opt.selected > 0:
		var want_rarity := _rarity_opt.selected - 1   # Common..Legendary == 0..3
		if def.rarity != want_rarity:
			return false
	# variant (requires an owned instance of that variant)
	if _variant_opt.selected > 0:
		var want_variant := _variant_opt.selected - 1
		var has := false
		for inst in insts:
			if inst.variant == want_variant:
				has = true
				break
		if not has:
			return false
	# graded
	if _graded_opt.selected == 1:   # Graded
		var any := false
		for inst in insts:
			if inst.graded:
				any = true
		if not any:
			return false
	elif _graded_opt.selected == 2:  # Ungraded
		var anyu := false
		for inst in insts:
			if not inst.graded:
				anyu = true
		if not anyu:
			return false
	return true

func _sort_records(records: Array) -> void:
	var mode := _sort_opt.selected
	var cmp := func(a, b):
		match mode:
			1: return a["def"].rarity > b["def"].rarity
			2: return a["def"].number < b["def"].number
			3: return a["qty"] > b["qty"]
			4: return a["best_cond"] > b["best_cond"]
			5: return a["best_grade"] > b["best_grade"]
			6: return a["newest"] > b["newest"]
			_: return a["best_v"] > b["best_v"]
	records.sort_custom(cmp)

func _row(rec: Dictionary) -> PanelContainer:
	var def: CardDefinition = rec["def"]
	var owned: bool = rec["qty"] > 0
	var p := UI.panel(UI.COL_PANEL2 if owned else UI.COL_PANEL)
	var h := UI.hbox(10)
	p.add_child(h)

	var num := UI.label("#%03d" % def.number, 13, UI.COL_MUTED)
	num.custom_minimum_size = Vector2(48, 0)
	h.add_child(num)

	var v := UI.vbox(2)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var nm := UI.label(def.name, 15, UI.COL_TEXT if owned else UI.COL_MUTED)
	v.add_child(nm)
	v.add_child(UI.label("%s • %s • %s" % [ContentDB.get_set(def.set_id).name, def.faction, Enums.rarity_name(def.rarity)], 11, UI.COL_MUTED))
	h.add_child(v)

	if owned:
		h.add_child(UI.label("x%d" % rec["qty"], 14, UI.COL_TEXT))
		h.add_child(UI.label("best: %s" % Enums.variant_name(rec["best_variant"]), 12, Enums.variant_color(rec["best_variant"])))
		h.add_child(UI.label("%s PL" % UI.money(rec["best_v"]), 14, UI.COL_GOOD))
		h.add_child(UI.button("Details", _open_details.bind(def.id)))
	else:
		h.add_child(UI.label("Not owned", 13, UI.COL_BAD))
	return p

# ===========================================================================
# Details dialog: per-instance actions
# ===========================================================================
func _open_details(card_id: String) -> void:
	_dialog_card_id = card_id
	_populate_dialog()
	_dialog.title = ContentDB.get_card(card_id).name
	_dialog.popup_centered()

func _populate_dialog() -> void:
	clear_children(_dialog_box)
	var def := ContentDB.get_card(_dialog_card_id)
	var insts: Array = []
	for inst in Game.collection:
		if inst.card_id == _dialog_card_id:
			insts.append(inst)
	if insts.is_empty():
		_dialog_box.add_child(UI.label("No copies owned.", 14, UI.COL_MUTED))
		return
	_dialog_box.add_child(UI.label("%d cop%s • set %s" % [insts.size(), "y" if insts.size() == 1 else "ies", ContentDB.get_set(def.set_id).name], 13, UI.COL_MUTED))
	var best_uid := Game.best_copy_uid(_dialog_card_id)
	for inst in insts:
		_dialog_box.add_child(_instance_row(inst, inst.uid == best_uid))

func _instance_row(inst: CardInstance, is_best: bool) -> PanelContainer:
	var p := UI.panel(UI.COL_PANEL)
	var v := UI.vbox(4)
	p.add_child(v)

	var line := UI.hbox(8)
	var tag := "BEST COPY" if is_best else "duplicate"
	line.add_child(UI.label(Enums.variant_name(inst.variant), 14, Enums.variant_color(inst.variant)))
	line.add_child(UI.label(tag, 11, UI.COL_GOLD if is_best else UI.COL_MUTED))
	line.add_child(UI.spacer())
	line.add_child(UI.label("%s PL" % UI.money(PrestigeCalc.card_value(inst)), 14, UI.COL_GOOD))
	v.add_child(line)

	var cond := "Raw: %s" % Enums.condition_name(inst.condition)
	if inst.graded:
		cond = "%s Grade %d/10" % [Balance.GRADER_NAME, inst.grade]
	var meta := cond
	if inst.serial_label() != "":
		meta += "  •  Serial " + inst.serial_label()
	if Game.is_displayed(inst.uid):
		meta += "  •  ON DISPLAY"
	v.add_child(UI.label(meta, 12, UI.COL_MUTED))

	var actions := UI.hbox(6)
	actions.add_child(UI.button("Sell", _sell.bind(inst.uid)))
	if not inst.graded:
		actions.add_child(UI.button("Grade (%d PL)" % int(Grading.fee()), _grade.bind(inst.uid)))
	actions.add_child(UI.button("Remove Display" if Game.is_displayed(inst.uid) else "Display", _display.bind(inst.uid)))
	v.add_child(actions)
	return p

func _sell(uid: int) -> void:
	var inst := Game.get_instance(uid)
	if inst == null:
		return
	var value := PrestigeCalc.sell_value(inst)
	var do_sell := func():
		var res := Game.sell_instance(uid)
		toast(res["reason"])
		_populate_dialog()
		refresh()
	if value >= Balance.HIGH_VALUE_THRESHOLD:
		confirm("Sell this card for %s PL? This cannot be undone." % UI.money(value), do_sell)
	else:
		do_sell.call()

func _grade(uid: int) -> void:
	var res := Game.grade_instance(uid)
	toast(res["reason"])
	_populate_dialog()
	refresh()

func _display(uid: int) -> void:
	var res := Game.toggle_display(uid)
	toast(res["reason"])
	_populate_dialog()
	refresh()

func _sell_dupes() -> void:
	var dupes := Game.duplicate_instance_uids()
	if dupes.is_empty():
		toast("No duplicates to sell.")
		return
	var total := 0.0
	for uid in dupes:
		var inst := Game.get_instance(uid)
		if inst:
			total += PrestigeCalc.sell_value(inst)
	confirm("Sell %d duplicate cards for about %s PL? Best copy of each card is kept." % [dupes.size(), UI.money(total)], func():
		var res := Game.sell_all_duplicates()
		toast("Sold %d duplicates for %s PL." % [res["count"], UI.money(res["total"])])
		refresh())
