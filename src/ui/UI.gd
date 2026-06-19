class_name UI
extends RefCounted
## Small UI construction helpers so screens stay terse and consistent.
## Everything is built in code (no fragile .tscn wiring).

const COL_BG := Color("#15161f")
const COL_PANEL := Color("#1f2130")
const COL_PANEL2 := Color("#272a3d")
const COL_TEXT := Color("#e7e9ff")
const COL_MUTED := Color("#9aa0b5")
const COL_ACCENT := Color("#8a7bff")
const COL_GOOD := Color("#5bd16a")
const COL_BAD := Color("#ff7a7a")
const COL_GOLD := Color("#ffd24a")

static func label(text: String, size: int = 16, color: Color = COL_TEXT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l

static func wrap_label(text: String, size: int = 14, color: Color = COL_MUTED) -> Label:
	var l := label(text, size, color)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return l

static func button(text: String, callable: Callable, accent: bool = false) -> Button:
	var b := Button.new()
	b.text = text
	b.add_theme_font_size_override("font_size", 15)
	b.custom_minimum_size = Vector2(0, 34)
	if accent:
		b.add_theme_color_override("font_color", Color.WHITE)
		var sb := _flat(COL_ACCENT, COL_ACCENT.lightened(0.1), 8)
		b.add_theme_stylebox_override("normal", sb)
		b.add_theme_stylebox_override("hover", _flat(COL_ACCENT.lightened(0.12), COL_ACCENT, 8))
		b.add_theme_stylebox_override("pressed", _flat(COL_ACCENT.darkened(0.15), COL_ACCENT, 8))
	if callable.is_valid():
		b.pressed.connect(callable)
	return b

static func panel(bg: Color = COL_PANEL, pad: int = 10) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := _flat(bg, bg.lightened(0.08), 8)
	sb.content_margin_left = pad
	sb.content_margin_right = pad
	sb.content_margin_top = pad
	sb.content_margin_bottom = pad
	p.add_theme_stylebox_override("panel", sb)
	return p

static func _flat(bg: Color, border: Color, radius: int) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(1)
	sb.set_corner_radius_all(radius)
	return sb

static func vbox(sep: int = 6) -> VBoxContainer:
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", sep)
	return v

static func hbox(sep: int = 6) -> HBoxContainer:
	var h := HBoxContainer.new()
	h.add_theme_constant_override("separation", sep)
	return h

static func scroll() -> ScrollContainer:
	var s := ScrollContainer.new()
	s.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	s.size_flags_vertical = Control.SIZE_EXPAND_FILL
	s.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	return s

static func spacer() -> Control:
	var c := Control.new()
	c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	c.size_flags_vertical = Control.SIZE_EXPAND_FILL
	return c

static func money(v: float) -> String:
	return _commas(int(round(v)))

static func _commas(n: int) -> String:
	var s := str(abs(n))
	var out := ""
	var c := 0
	for i in range(s.length() - 1, -1, -1):
		out = s[i] + out
		c += 1
		if c % 3 == 0 and i > 0:
			out = "," + out
	return ("-" if n < 0 else "") + out

# ---------------------------------------------------------------------------
# Card tile (placeholder frame). Compact, color-coded by rarity & variant.
# ---------------------------------------------------------------------------
static func card_tile(inst: CardInstance, show_value: bool = true) -> PanelContainer:
	var def := ContentDB.get_card(inst.card_id)
	var er := Enums.effective_rarity(def.rarity, inst.variant)
	var frame := Enums.rarity_color(er)
	var p := PanelContainer.new()
	var sb := _flat(COL_PANEL2, frame, 10)
	sb.set_border_width_all(3)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	p.add_theme_stylebox_override("panel", sb)
	p.custom_minimum_size = Vector2(168, 150)

	var v := vbox(3)
	var head := hbox(4)
	head.add_child(label("#%03d" % def.number, 12, COL_MUTED))
	head.add_child(spacer())
	head.add_child(label(Enums.rarity_name(er), 12, frame))
	v.add_child(head)

	var name_l := label(def.name, 15, COL_TEXT)
	name_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	v.add_child(name_l)

	v.add_child(label("%s • %s" % [def.faction, ContentDB.get_set(def.set_id).name], 11, COL_MUTED))

	var vlbl := label(Enums.variant_name(inst.variant), 13, Enums.variant_color(inst.variant))
	v.add_child(vlbl)

	var cond := "Raw %s" % Enums.condition_name(inst.condition)
	if inst.graded:
		cond = "%s GRADE %d" % [Balance.GRADER_NAME.substr(0, 3).to_upper(), inst.grade]
	v.add_child(label(cond, 11, COL_GOLD if inst.graded else COL_MUTED))

	if inst.serial_label() != "":
		v.add_child(label("Serial " + inst.serial_label(), 12, COL_GOLD))

	if show_value:
		v.add_child(label("Value: %s PL" % money(PrestigeCalc.card_value(inst)), 13, COL_GOOD))

	p.add_child(v)
	return p
