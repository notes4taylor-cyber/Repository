extends Control
## Main (root controller)
## Owns the resource header, navigation bar, screen switching, toasts and the
## shared confirmation dialog. Screens are built in code and cached.

const SCREENS := {
	"dashboard": "res://src/ui/screens/DashboardScreen.gd",
	"shop": "res://src/ui/screens/ShopScreen.gd",
	"open": "res://src/ui/screens/OpenScreen.gd",
	"collection": "res://src/ui/screens/CollectionScreen.gd",
	"sets": "res://src/ui/screens/SetsScreen.gd",
	"grading": "res://src/ui/screens/GradingScreen.gd",
	"trades": "res://src/ui/screens/TradesScreen.gd",
	"display": "res://src/ui/screens/DisplayScreen.gd",
	"profile": "res://src/ui/screens/ProfileScreen.gd",
	"settings": "res://src/ui/screens/SettingsScreen.gd",
	"debug": "res://src/ui/screens/DebugPanel.gd",
}

const NAV := [
	["dashboard", "Dashboard"], ["shop", "Shop"], ["open", "Open Packs"],
	["collection", "Collection"], ["sets", "Sets & Badges"], ["grading", "Grading"],
	["trades", "Trades"], ["display", "Display Room"], ["profile", "Profile"],
	["settings", "Settings"],
]

var debug_enabled := true
var in_game := false
var current_name := ""

var _header: PanelContainer
var _header_box: HBoxContainer
var _nav: HBoxContainer
var _content: PanelContainer
var _toast: Label
var _toast_timer: Timer
var _confirm: ConfirmationDialog
var _confirm_cb: Callable

var _screens := {}        # name -> ScreenBase
var _menu_screen: ScreenBase

func _ready() -> void:
	_build_chrome()
	Game.changed.connect(_refresh_header)
	Game.notify.connect(toast)
	SaveManager.saved.connect(func(reason): _flash_saved(reason))
	show_menu()

func _build_chrome() -> void:
	var bg := ColorRect.new()
	bg.color = UI.COL_BG
	bg.anchor_right = 1.0
	bg.anchor_bottom = 1.0
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)

	var margin := MarginContainer.new()
	margin.anchor_right = 1.0
	margin.anchor_bottom = 1.0
	margin.add_theme_constant_override("margin_left", 12)
	margin.add_theme_constant_override("margin_right", 12)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	add_child(margin)

	var root := UI.vbox(8)
	margin.add_child(root)

	# Header (resource bar)
	_header = UI.panel(UI.COL_PANEL, 8)
	_header_box = UI.hbox(16)
	_header.add_child(_header_box)
	root.add_child(_header)

	# Nav bar
	var nav_scroll := ScrollContainer.new()
	nav_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	nav_scroll.custom_minimum_size = Vector2(0, 42)
	_nav = UI.hbox(4)
	nav_scroll.add_child(_nav)
	root.add_child(nav_scroll)
	_build_nav()

	# Content
	_content = UI.panel(UI.COL_PANEL, 12)
	_content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root.add_child(_content)

	# Toast
	_toast = UI.label("", 15, Color.WHITE)
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_toast.anchor_left = 0.0
	_toast.anchor_right = 1.0
	_toast.anchor_top = 0.9
	_toast.anchor_bottom = 0.97
	_toast.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_toast.add_theme_color_override("font_color", UI.COL_GOLD)
	_toast.visible = false
	add_child(_toast)
	_toast_timer = Timer.new()
	_toast_timer.one_shot = true
	_toast_timer.timeout.connect(func(): _toast.visible = false)
	add_child(_toast_timer)

	# Confirm dialog
	_confirm = ConfirmationDialog.new()
	_confirm.title = "Confirm"
	_confirm.confirmed.connect(_on_confirmed)
	add_child(_confirm)

func _build_nav() -> void:
	for entry in NAV:
		_nav.add_child(UI.button(entry[1], goto.bind(entry[0])))
	if debug_enabled:
		var db := UI.button("Debug", goto.bind("debug"))
		db.add_theme_color_override("font_color", UI.COL_BAD)
		_nav.add_child(db)
	_nav.add_child(UI.button("Main Menu", show_menu))

# ===========================================================================
# Navigation
# ===========================================================================
func show_menu() -> void:
	in_game = false
	_header.visible = false
	_nav.get_parent().visible = false
	_clear_content()
	if _menu_screen == null:
		_menu_screen = load("res://src/ui/screens/MainMenuScreen.gd").new()
	_content.add_child(_menu_screen)
	_menu_screen.setup(self)
	current_name = "menu"

func enter_game() -> void:
	in_game = true
	_header.visible = true
	_nav.get_parent().visible = true
	_refresh_header()
	goto("dashboard")

func goto(screen: String) -> void:
	if not SCREENS.has(screen):
		return
	_clear_content()
	if not _screens.has(screen):
		_screens[screen] = load(SCREENS[screen]).new()
	var s: ScreenBase = _screens[screen]
	_content.add_child(s)
	s.setup(self)
	current_name = screen

func _clear_content() -> void:
	for c in _content.get_children():
		_content.remove_child(c)

# ===========================================================================
# Header
# ===========================================================================
func _refresh_header() -> void:
	if not in_game:
		return
	for c in _header_box.get_children():
		c.queue_free()
	var pc := PrestigeCalc.collection_prestige()
	var p := pc + Game.pl
	_add_stat("Total P", UI.money(p), UI.COL_GOLD)
	_add_stat("PC", UI.money(pc), UI.COL_ACCENT)
	_add_stat("PL", UI.money(Game.pl), UI.COL_GOOD)
	_add_stat("Day", str(Game.day), UI.COL_TEXT)
	_add_stat("Cards", str(Game.collection.size()), UI.COL_MUTED)
	_header_box.add_child(UI.spacer())
	_header_box.add_child(UI.label(Reputation.title(), 13, UI.COL_MUTED))
	_header_box.add_child(UI.button("Save", _manual_save))

func _add_stat(name: String, value: String, color: Color) -> void:
	var v := UI.vbox(0)
	v.add_child(UI.label(name, 11, UI.COL_MUTED))
	v.add_child(UI.label(value, 20, color))
	_header_box.add_child(v)

func _manual_save() -> void:
	SaveManager.save_game(Game, "manual")

func _flash_saved(reason: String) -> void:
	if in_game:
		toast("Saved (%s)" % reason)

# ===========================================================================
# Toast + confirm
# ===========================================================================
func toast(text: String) -> void:
	_toast.text = text
	_toast.visible = true
	_toast_timer.start(2.2)

func confirm(text: String, on_yes: Callable) -> void:
	_confirm_cb = on_yes
	_confirm.dialog_text = text
	_confirm.popup_centered()

func _on_confirmed() -> void:
	if _confirm_cb.is_valid():
		_confirm_cb.call()

# ===========================================================================
# Debug hotkey
# ===========================================================================
func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_F1:
		debug_enabled = not debug_enabled
		toast("Debug %s" % ("enabled" if debug_enabled else "disabled"))
