extends Node
## Headless UI smoke test: boots the real Main scene, starts a game, navigates
## every screen, opens a pack (reveal flow), and opens the collection details
## dialog. Any UI build/refresh runtime error prints as a SCRIPT ERROR and the
## final marker confirms a clean traversal.
## Run: godot --headless res://tools/UISmoke.tscn

func _ready() -> void:
	print("=== UI smoke test ===")
	var main: Control = load("res://src/ui/Main.tscn").instantiate()
	add_child(main)            # triggers Main._ready -> chrome + main menu
	await get_tree().process_frame

	Game.new_game(777)
	main.enter_game()
	await get_tree().process_frame

	# Give the player something to look at on every screen.
	Game.debug_add_pl(20000.0)
	var pid: String = "%s_pack" % ContentDB.set_order[0]
	Game.buy_product(pid)

	# Open a pack while on the open screen so the reveal flow builds.
	main.goto("open")
	await get_tree().process_frame
	Game.open_unit(pid)
	await get_tree().process_frame
	print("  [OK] open/reveal screen built (%d cards)" % Game.collection.size())

	Game.debug_force_pull("serialized")
	Game.debug_complete_set(ContentDB.set_order[0])
	Trades.refresh()

	for screen in ["dashboard", "shop", "open", "collection", "sets", "grading",
			"trades", "display", "profile", "settings", "debug"]:
		main.goto(screen)
		await get_tree().process_frame
		print("  [OK] screen built: " + screen)

	# Exercise the collection details dialog (instance-level actions UI).
	main.goto("collection")
	await get_tree().process_frame
	var coll = main._screens["collection"]
	if not Game.collection.is_empty():
		coll._open_details(Game.collection[0].card_id)
		await get_tree().process_frame
		print("  [OK] collection details dialog built")

	# Toast + header refresh paths.
	main.toast("smoke")
	main._refresh_header()
	await get_tree().process_frame

	print("=== UI smoke OK ===")
	get_tree().quit(0)
