extends ScreenBase
## NPC Trades: review offers from collectors with distinct tastes.

var _body: VBoxContainer

func build() -> void:
	var root := UI.vbox(8)
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(root)
	var head := UI.hbox(8)
	head.add_child(UI.label("NPC Trades", 24, UI.COL_GOLD))
	head.add_child(UI.spacer())
	head.add_child(UI.button("Find New Offers", func():
		Trades.refresh()
		refresh()))
	root.add_child(head)
	root.add_child(UI.wrap_label("Collectors want items from your inventory and offer PL, sealed product, or cards in return. Compare the values before you accept.", 13))
	var sc := UI.scroll()
	root.add_child(sc)
	_body = UI.vbox(8)
	_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_body)

func refresh() -> void:
	if _body == null:
		return
	if Trades.offers.is_empty():
		Trades.refresh()
	clear_children(_body)
	if Trades.offers.is_empty():
		_body.add_child(UI.label("No offers right now. Acquire more cards/sealed product, then check back.", 14, UI.COL_MUTED))
		return
	for offer in Trades.offers:
		_body.add_child(_offer_panel(offer))

func _offer_panel(offer: Dictionary) -> PanelContainer:
	var p := UI.panel(UI.COL_PANEL2)
	var v := UI.vbox(6)
	p.add_child(v)

	var head := UI.hbox(8)
	head.add_child(UI.label(offer["npc_name"], 16, UI.COL_ACCENT))
	head.add_child(UI.label("(%s)" % offer["npc_type"], 12, UI.COL_MUTED))
	v.add_child(head)
	v.add_child(UI.label(offer["npc_desc"], 12, UI.COL_MUTED))

	var cols := UI.hbox(16)
	var want_v := UI.vbox(2)
	want_v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	want_v.add_child(UI.label("They want:", 13, UI.COL_BAD))
	want_v.add_child(UI.wrap_label(offer["want_label"], 13, UI.COL_TEXT))
	want_v.add_child(UI.label("~%s PL" % UI.money(offer["want_value"]), 12, UI.COL_MUTED))
	cols.add_child(want_v)

	var give_v := UI.vbox(2)
	give_v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	give_v.add_child(UI.label("They give:", 13, UI.COL_GOOD))
	give_v.add_child(UI.wrap_label(offer["give_label"], 13, UI.COL_TEXT))
	give_v.add_child(UI.label("~%s PL" % UI.money(offer["give_value"]), 12, UI.COL_MUTED))
	cols.add_child(give_v)
	v.add_child(cols)

	var net: float = offer["give_value"] - offer["want_value"]
	var net_col: Color = UI.COL_GOOD if net >= 0 else UI.COL_BAD
	v.add_child(UI.label("Net for you: %s%s PL" % ["+" if net >= 0 else "", UI.money(net)], 14, net_col))

	var actions := UI.hbox(8)
	actions.add_child(UI.button("Accept", _accept.bind(offer["id"]), true))
	actions.add_child(UI.button("Decline", _decline.bind(offer["id"])))
	v.add_child(actions)
	return p

func _accept(offer_id: int) -> void:
	var offer := Trades.get_offer(offer_id)
	if offer.is_empty():
		refresh()
		return
	var high: bool = maxf(offer["want_value"], offer["give_value"]) >= Balance.HIGH_VALUE_THRESHOLD
	var do_accept := func():
		var res := Trades.accept(offer_id)
		toast(res["reason"])
		refresh()
	if high:
		confirm("Confirm this trade? It involves high-value items.", do_accept)
	else:
		do_accept.call()

func _decline(offer_id: int) -> void:
	Trades.decline(offer_id)
	refresh()
