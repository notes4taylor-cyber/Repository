extends ScreenBase
## Open Packs: pick owned sealed product to open, then reveal pulls one-by-one
## (or reveal all / skip). Listens to Game.pulls_ready so shop "Buy & Open" and
## in-screen opening share the same reveal flow.

const REVEAL_CAP := 60   # max tiles drawn; extras are summarized

var _container: VBoxContainer
var _pulls: Array = []
var _index: int = 0
var _grid: GridContainer
var _progress: Label
var _mode := "inventory"

func build() -> void:
	var sc := UI.scroll()
	add_child(sc)
	_container = UI.vbox(10)
	_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(_container)

func _enter_tree() -> void:
	if not Game.pulls_ready.is_connected(begin_reveal):
		Game.pulls_ready.connect(begin_reveal)

func _exit_tree() -> void:
	if Game.pulls_ready.is_connected(begin_reveal):
		Game.pulls_ready.disconnect(begin_reveal)

func refresh() -> void:
	if _container == null:
		return
	if _mode == "reveal":
		return
	_render_inventory()

# ===========================================================================
# Inventory of sealed product to open
# ===========================================================================
func _render_inventory() -> void:
	_mode = "inventory"
	clear_children(_container)
	_container.add_child(UI.label("Open Packs", 26, UI.COL_GOLD))

	if Game.sealed_inventory.is_empty():
		_container.add_child(UI.label("You have no sealed product. Visit the Shop to buy some.", 15, UI.COL_MUTED))
		_container.add_child(UI.button("Go to Shop", goto.bind("shop"), true))
		return

	_container.add_child(UI.label("Your sealed product:", 16, UI.COL_MUTED))
	for pid in Game.sealed_inventory.keys():
		var prod := ContentDB.get_product(pid)
		if prod == null:
			continue
		var qty: int = Game.sealed_inventory[pid]
		var p := UI.panel(UI.COL_PANEL2)
		var h := UI.hbox(12)
		p.add_child(h)
		var v := UI.vbox(2)
		v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		v.add_child(UI.label("%s  x%d" % [prod.name, qty], 16))
		v.add_child(UI.label("%d cards per unit • sealed value %s PC each" % [prod.total_cards(), UI.money(prod.price)], 12, UI.COL_MUTED))
		h.add_child(v)
		h.add_child(UI.button("Open 1", _open_one.bind(pid), true))
		_container.add_child(p)

func _open_one(product_id: String) -> void:
	var res := Game.open_unit(product_id)
	if not res["ok"]:
		toast(res["reason"])

# ===========================================================================
# Reveal flow (triggered by Game.pulls_ready)
# ===========================================================================
func begin_reveal(pulls: Array) -> void:
	_pulls = pulls
	_index = 0
	_mode = "reveal"
	clear_children(_container)

	var header := UI.hbox(10)
	_progress = UI.label("", 16, UI.COL_MUTED)
	header.add_child(_progress)
	header.add_child(UI.spacer())
	header.add_child(UI.button("Reveal Next", _reveal_next))
	header.add_child(UI.button("Reveal All", _reveal_all, true))
	header.add_child(UI.button("Skip to Summary", _show_summary))
	_container.add_child(header)

	_grid = GridContainer.new()
	_grid.columns = 4
	_grid.add_theme_constant_override("h_separation", 8)
	_grid.add_theme_constant_override("v_separation", 8)
	_container.add_child(_grid)

	_update_progress()
	if Game.settings.get("fast_reveal", false):
		_reveal_all()
	else:
		_reveal_next()

func _update_progress() -> void:
	if _progress != null:
		_progress.text = "Revealed %d / %d" % [mini(_index, _pulls.size()), _pulls.size()]

func _reveal_next() -> void:
	if _index >= _pulls.size():
		_show_summary()
		return
	if _grid.get_child_count() < REVEAL_CAP:
		_grid.add_child(_reveal_tile(_pulls[_index]))
	_index += 1
	_update_progress()
	if _index >= _pulls.size():
		_show_summary()

func _reveal_all() -> void:
	while _index < _pulls.size():
		if _grid.get_child_count() < REVEAL_CAP:
			_grid.add_child(_reveal_tile(_pulls[_index]))
		_index += 1
	_update_progress()
	_show_summary()

func _reveal_tile(inst: CardInstance) -> Control:
	var def := ContentDB.get_card(inst.card_id)
	var box := UI.vbox(2)
	box.add_child(UI.card_tile(inst))
	if Enums.is_grail(def.rarity, inst.variant):
		var tag := UI.label("★ GRAIL PULL ★", 13, UI.COL_GOLD)
		tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		box.add_child(tag)
	return box

func _show_summary() -> void:
	# Mark everything revealed.
	_index = _pulls.size()
	_update_progress()

	var total := 0.0
	var grails := 0
	var best: CardInstance = null
	var best_v := -1.0
	for inst in _pulls:
		var def := ContentDB.get_card(inst.card_id)
		var v := PrestigeCalc.card_value(inst)
		total += v
		if Enums.is_grail(def.rarity, inst.variant):
			grails += 1
		if v > best_v:
			best_v = v
			best = inst

	var sp := UI.panel(UI.COL_PANEL)
	var v := UI.vbox(6)
	sp.add_child(v)
	v.add_child(UI.label("Pack Summary", 20, UI.COL_GOLD))
	v.add_child(UI.label("Cards pulled: %d" % _pulls.size(), 15))
	v.add_child(UI.label("Total card value gained: %s PC" % UI.money(total), 15, UI.COL_GOOD))
	v.add_child(UI.label("Grail pulls: %d" % grails, 15, UI.COL_GOLD if grails > 0 else UI.COL_MUTED))
	if best != null:
		v.add_child(UI.label("Best pull: %s (%s PL)" % [ContentDB.get_card(best.card_id).name, UI.money(best_v)], 14, UI.COL_ACCENT))
	if _pulls.size() > REVEAL_CAP:
		v.add_child(UI.label("(%d cards added to your collection; first %d shown above.)" % [_pulls.size(), REVEAL_CAP], 12, UI.COL_MUTED))
	var actions := UI.hbox(8)
	actions.add_child(UI.button("Open More", func(): _render_inventory(), true))
	actions.add_child(UI.button("View Collection", goto.bind("collection")))
	v.add_child(actions)
	_container.add_child(sp)
