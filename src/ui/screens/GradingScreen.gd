extends ScreenBase
## Grading: submit raw cards to the fictional grader for a 1-10 grade.

const LIST_CAP := 150

var _body: VBoxContainer

func build() -> void:
	var root := UI.vbox(8)
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(root)
	root.add_child(UI.label("Grading — %s" % Balance.GRADER_NAME, 24, UI.COL_GOLD))
	root.add_child(UI.wrap_label("Submit a raw card for grading (%d PL). A higher grade raises its value; condition drives the odds. Grade 10 is rare." % int(Grading.fee()), 13))
	var sc := UI.scroll()
	root.add_child(sc)
	_body = UI.vbox(6)
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_body)

func refresh() -> void:
	if _body == null:
		return
	clear_children(_body)

	var ungraded: Array = []
	var graded_count := 0
	for inst in Game.collection:
		if inst.graded:
			graded_count += 1
		else:
			ungraded.append(inst)
	ungraded.sort_custom(func(a, b): return PrestigeCalc.card_value(a) > PrestigeCalc.card_value(b))

	_body.add_child(UI.label("Graded cards: %d   •   Raw cards: %d   •   Your PL: %s" % [graded_count, ungraded.size(), UI.money(Game.pl)], 13, UI.COL_MUTED))

	if ungraded.is_empty():
		_body.add_child(UI.label("No raw cards to grade. Open more packs!", 14, UI.COL_MUTED))
		return

	var shown := 0
	for inst in ungraded:
		if shown >= LIST_CAP:
			_body.add_child(UI.label("... and %d more raw cards." % (ungraded.size() - shown), 13, UI.COL_MUTED))
			break
		_body.add_child(_grade_row(inst))
		shown += 1

func _grade_row(inst: CardInstance) -> PanelContainer:
	var def := ContentDB.get_card(inst.card_id)
	var p := UI.panel(UI.COL_PANEL2)
	var h := UI.hbox(10)
	p.add_child(h)
	var v := UI.vbox(2)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_child(UI.label("%s (%s)" % [def.name, Enums.variant_name(inst.variant)], 15))
	v.add_child(UI.label("Condition: %s • raw value %s PL" % [Enums.condition_name(inst.condition), UI.money(PrestigeCalc.card_value(inst))], 12, UI.COL_MUTED))
	h.add_child(v)
	var btn := UI.button("Grade (%d PL)" % int(Grading.fee()), _grade.bind(inst.uid), true)
	btn.disabled = Game.pl < Grading.fee()
	h.add_child(btn)
	return p

func _grade(uid: int) -> void:
	var inst := Game.get_instance(uid)
	if inst == null:
		return
	var value := PrestigeCalc.card_value(inst)
	var do_grade := func():
		var res := Game.grade_instance(uid)
		toast(res["reason"])
		refresh()
	if value >= Balance.HIGH_VALUE_THRESHOLD:
		confirm("Grade this %s PL card? The grade may raise or lower its value." % UI.money(value), do_grade)
	else:
		do_grade.call()
