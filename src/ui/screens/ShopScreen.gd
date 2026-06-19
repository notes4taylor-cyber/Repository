extends ScreenBase
## Shop: buy sealed Season 1 product. Buy to keep sealed, or buy & open now.

var _list: VBoxContainer
var _set_filter: OptionButton

func build() -> void:
	var root := UI.vbox(10)
	root.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(root)

	var header := UI.hbox(10)
	header.add_child(UI.label("Shop", 26, UI.COL_GOLD))
	header.add_child(UI.spacer())
	header.add_child(UI.label("Filter set:", 14, UI.COL_MUTED))
	_set_filter = OptionButton.new()
	_set_filter.add_item("All Sets", -1)
	for i in range(ContentDB.set_order.size()):
		_set_filter.add_item(ContentDB.get_set(ContentDB.set_order[i]).name, i)
	_set_filter.item_selected.connect(func(_i): refresh())
	header.add_child(_set_filter)
	root.add_child(header)

	root.add_child(UI.wrap_label("Buy sealed product to lock PL into PC, then open it for cards (or hold it as a sealed investment).", 13))

	var sc := UI.scroll()
	root.add_child(sc)
	_list = UI.vbox(8)
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_list)

func refresh() -> void:
	if _list == null:
		return
	clear_children(_list)
	var sel := _set_filter.get_selected_id()
	for i in range(ContentDB.set_order.size()):
		if sel != -1 and sel != i:
			continue
		var set_id: String = ContentDB.set_order[i]
		_list.add_child(UI.label(ContentDB.get_set(set_id).name, 18, UI.COL_ACCENT))
		for prod in ContentDB.products_for_set(set_id):
			_list.add_child(_product_row(prod))

func _product_row(prod: ProductDefinition) -> PanelContainer:
	var p := UI.panel(UI.COL_PANEL2)
	var h := UI.hbox(12)
	p.add_child(h)

	var v := UI.vbox(2)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	v.add_child(UI.label(prod.name, 16))
	v.add_child(UI.label("%d packs x %d cards (%d total) • luck x%.2f" % [prod.packs, prod.cards_per_pack, prod.total_cards(), prod.luck], 12, UI.COL_MUTED))
	h.add_child(v)

	var price := UI.label("%s PL" % UI.money(prod.price), 18, UI.COL_GOOD)
	h.add_child(price)

	var buy := UI.button("Buy", _buy.bind(prod.id))
	var buy_open := UI.button("Buy & Open", _buy_open.bind(prod.id), true)
	var afford := Game.pl >= prod.price
	buy.disabled = not afford
	buy_open.disabled = not afford
	h.add_child(buy)
	h.add_child(buy_open)
	return p

func _buy(product_id: String) -> void:
	var res := Game.buy_product(product_id)
	toast(res["reason"])
	refresh()

func _buy_open(product_id: String) -> void:
	var res := Game.buy_product(product_id)
	if not res["ok"]:
		toast(res["reason"])
		return
	# Navigate to the open screen first so it can catch the reveal signal.
	goto("open")
	Game.open_unit(product_id)
