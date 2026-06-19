class_name ScreenBase
extends MarginContainer
## Base for every in-game screen. Subclasses override build() to construct their
## UI once, and refresh() to update dynamic content. Main wires `main` so screens
## can request navigation and shared dialogs.
##
## Extends MarginContainer (not a plain Control) so a screen's single root child
## is stretched to fill the content area — otherwise a trailing ScrollContainer
## collapses to its minimum height and its contents become invisible.

var main: Node = null
var _built := false

func setup(main_ref: Node) -> void:
	main = main_ref
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	size_flags_vertical = Control.SIZE_EXPAND_FILL
	if not _built:
		build()
		_built = true
	refresh()

# Override in subclasses.
func build() -> void:
	pass

func refresh() -> void:
	pass

# Convenience pass-throughs to Main.
func goto(screen: String) -> void:
	if main and main.has_method("goto"):
		main.goto(screen)

func toast(text: String) -> void:
	if main and main.has_method("toast"):
		main.toast(text)

func confirm(text: String, on_yes: Callable) -> void:
	if main and main.has_method("confirm"):
		main.confirm(text, on_yes)

func clear_children(node: Node) -> void:
	for c in node.get_children():
		c.queue_free()
