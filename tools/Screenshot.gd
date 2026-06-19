extends Node
## Offscreen screenshot tool: boots the real Main scene under a virtual display
## and saves PNGs of several screens so the game can be "seen" running headlessly.
## Run: xvfb-run -s "-screen 0 1400x900x24" godot res://tools/Screenshot.tscn

const OUT := "/home/user/Repository/shots/"
var main: Control

func _ready() -> void:
	DirAccess.make_dir_recursive_absolute(OUT)
	main = load("res://src/ui/Main.tscn").instantiate()
	add_child(main)
	await _settle()
	await _shot("01_main_menu")

	Game.new_game(424242)
	main.enter_game()
	Game.debug_add_pl(25000.0)
	await _settle()
	await _shot("02_dashboard")

	main.goto("shop")
	await _settle()
	await _shot("03_shop")

	# Open a collector box on the open screen to show a rich reveal.
	var pid: String = "%s_collector_box" % ContentDB.set_order[1]
	Game.buy_product(pid)
	main.goto("open")
	await _settle()
	Game.open_unit(pid)
	await _settle()
	await _shot("04_pack_opening")

	# Populate more, force some grails, then show collection + sets.
	Game.debug_force_pull("oneofone")
	Game.debug_force_pull("serialized")
	Game.debug_force_pull("legendary")
	Game.debug_complete_set(ContentDB.set_order[0])
	main.goto("collection")
	await _settle()
	await _shot("05_collection")

	main.goto("sets")
	await _settle()
	await _shot("06_sets_badges")

	Trades.refresh()
	main.goto("trades")
	await _settle()
	await _shot("07_trades")

	print("SCREENSHOTS DONE")
	get_tree().quit(0)

func _settle() -> void:
	for _i in range(4):
		await get_tree().process_frame
	await RenderingServer.frame_post_draw

func _shot(name: String) -> void:
	var img := get_viewport().get_texture().get_image()
	var path := OUT + name + ".png"
	var err := img.save_png(path)
	print("  saved %s (%s)" % [path, "ok" if err == OK else "ERR %d" % err])
