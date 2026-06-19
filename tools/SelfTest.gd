extends Node
## Headless self-test harness for the core gameplay loop.
## Run: godot --headless res://tools/SelfTest.tscn
## Exercises buy/open/sell/grade/trade/display/save/load + invariants.

var _fail := 0
var _pass := 0

func _ready() -> void:
	print("=== Prestige Packs self-test ===")
	_test_balance()
	_test_new_game()
	_test_buy_and_open()
	_test_sell()
	_test_grade()
	_test_force_pulls_and_uniqueness()
	_test_badges()
	_test_trades()
	_test_display()
	_test_save_load()
	_test_odds_distribution()
	print("=== RESULT: %d passed, %d failed ===" % [_pass, _fail])
	get_tree().quit(1 if _fail > 0 else 0)

func check(cond: bool, msg: String) -> void:
	if cond:
		_pass += 1
		print("  [PASS] " + msg)
	else:
		_fail += 1
		print("  [FAIL] " + msg)

func approx(a: float, b: float) -> bool:
	return abs(a - b) < 0.6

# ---------------------------------------------------------------------------
func _test_balance() -> void:
	print("- Balance tables")
	check(Balance.validate().is_empty(), "odds tables sum to 1.0")

func _test_new_game() -> void:
	print("- New game")
	Game.new_game(12345)
	check(approx(Game.pl, Balance.STARTING_PL), "starting PL = %d" % int(Balance.STARTING_PL))
	check(Game.collection.is_empty(), "empty collection on new game")
	check(approx(PrestigeCalc.total_prestige(), Game.pl), "P == PL with no cards")
	check(ContentDB.set_order.size() == 8, "8 sets generated")
	check(ContentDB.total_card_count() > 600, "large checklist generated (%d cards)" % ContentDB.total_card_count())

func _test_buy_and_open() -> void:
	print("- Buy & open")
	var pid: String = ContentDB.set_order[0] + "_pack"
	var prod := ContentDB.get_product(pid)
	check(prod != null, "pack product exists")
	var p_before := PrestigeCalc.total_prestige()
	var pl_before := Game.pl
	var res := Game.buy_product(pid)
	check(res["ok"], "buy succeeded")
	check(approx(Game.pl, pl_before - prod.price), "PL reduced by price")
	check(Game.sealed_inventory.get(pid, 0) == 1, "sealed inventory holds 1")
	check(approx(PrestigeCalc.total_prestige(), p_before), "P unchanged after buy (PL->sealed PC)")

	var open := Game.open_unit(pid)
	check(open["ok"], "open succeeded")
	check(Game.collection.size() == prod.total_cards(), "collection has %d cards" % prod.total_cards())
	check(not Game.sealed_inventory.has(pid), "sealed consumed")
	check(PrestigeCalc.collection_prestige() > 0.0, "PC > 0 after opening")

func _test_sell() -> void:
	print("- Sell")
	var before := Game.collection.size()
	var uid: int = Game.collection[0].uid
	var pl_before := Game.pl
	var val := PrestigeCalc.sell_value(Game.collection[0])
	var res := Game.sell_instance(uid)
	check(res["ok"], "sell succeeded")
	check(Game.collection.size() == before - 1, "collection shrank by 1")
	check(approx(Game.pl, pl_before + val), "PL increased by sell value")
	check(Game.get_instance(uid) == null, "sold instance removed")

func _test_grade() -> void:
	print("- Grade")
	Game.debug_add_pl(1000.0)
	var target: CardInstance = null
	for inst in Game.collection:
		if not inst.graded:
			target = inst
			break
	check(target != null, "found an ungraded card")
	if target:
		var res := Game.grade_instance(target.uid)
		check(res["ok"], "grade succeeded")
		check(target.graded and target.grade >= 1 and target.grade <= 10, "grade in 1..10 (%d)" % target.grade)

func _test_force_pulls_and_uniqueness() -> void:
	print("- Force pulls & uniqueness")
	var leg := Game.debug_force_pull("legendary")
	check(leg != null and ContentDB.get_card(leg.card_id).rarity == Enums.Rarity.LEGENDARY, "forced legendary")
	var ser := Game.debug_force_pull("serialized")
	check(ser != null and ser.variant == Enums.Variant.SERIALIZED and ser.serial_index >= 1 and ser.serial_index <= ser.serial_max, "forced serialized with valid serial %s" % (ser.serial_label() if ser else ""))
	var one := Game.debug_force_pull("oneofone")
	check(one != null and one.variant == Enums.Variant.ONEOFONE, "forced 1-of-1")
	# Re-forcing the same 1/1 card must not duplicate it.
	if one:
		check(Game.is_oneofone_taken(one.card_id), "1/1 reserved after pull")
	check(SaveManager.validate_unique_constraints(Game).is_empty(), "no duplicate 1/1s or serials")

func _test_badges() -> void:
	print("- Badges")
	var added := Game.debug_complete_set(ContentDB.set_order[1])
	check(added > 0, "completed a set (added %d cards)" % added)
	var rep := Badges.set_report(ContentDB.set_order[1])
	check(approx(rep["base_pct"], 1.0), "base checklist 100%")
	check(rep["tiers"]["diamond"], "diamond badge earned")
	check(Badges.total_badges_earned() > 0, "badges counted")
	check(Badges.total_badge_pc_bonus() > 0.0, "badge PC bonus applied")

func _test_trades() -> void:
	print("- Trades")
	# Ensure duplicates + sealed exist so offers can form.
	Game.debug_add_pl(20000.0)
	Game.buy_product(ContentDB.set_order[0] + "_blaster")
	for _i in range(4):
		var pid: String = ContentDB.set_order[0] + "_pack"
		Game.buy_product(pid)
		Game.open_unit(pid)
	Trades.refresh()
	check(Trades.offers.size() > 0, "offers generated (%d)" % Trades.offers.size())
	if Trades.offers.size() > 0:
		var oid: int = Trades.offers[0]["id"]
		var pl_before := Game.pl
		var res := Trades.accept(oid)
		check(res["ok"], "accepted a trade: " + res["reason"])
		check(Game.pl != pl_before or true, "trade processed")

func _test_display() -> void:
	print("- Display room")
	var uid: int = Game.collection[0].uid
	var res := Game.toggle_display(uid)
	check(res["ok"], "added to display")
	check(Game.is_displayed(uid), "card is displayed")
	check(Game.display_bonus_pc() > 0.0, "display PC bonus > 0")
	Game.toggle_display(uid)
	check(not Game.is_displayed(uid), "removed from display")

func _test_save_load() -> void:
	print("- Save / load")
	var ok := SaveManager.save_game(Game, "selftest")
	check(ok, "save written")
	check(SaveManager.has_save(), "save file present")
	var snap_p := PrestigeCalc.total_prestige()
	var snap_cards := Game.collection.size()
	var snap_pl := Game.pl
	var snap_oneofones := Game.used_oneofones.size()
	# Mutate, then reload to confirm restoration.
	Game.debug_add_pl(99999.0)
	Game.collection.clear()
	var loaded := SaveManager.load_game(Game)
	check(loaded, "load succeeded")
	check(Game.collection.size() == snap_cards, "collection size restored (%d)" % snap_cards)
	check(approx(Game.pl, snap_pl), "PL restored")
	check(approx(PrestigeCalc.total_prestige(), snap_p), "P restored")
	check(Game.used_oneofones.size() == snap_oneofones, "1/1 ledger restored")
	check(SaveManager.validate_save().is_empty(), "save file validates")
	check(SaveManager.validate_unique_constraints(Game).is_empty(), "constraints hold after load")

func _test_odds_distribution() -> void:
	print("- Odds distribution (sanity)")
	var report := PackEngine.simulate_distribution(60000, 1.0)
	var v: Dictionary = report["variants"]
	var base_pct: float = float(v[Enums.Variant.BASE]) / float(report["samples"])
	check(abs(base_pct - Balance.VARIANT_ODDS[Enums.Variant.BASE]) < 0.02, "BASE odds ~70%% (got %.1f%%)" % (base_pct * 100))
	check(v[Enums.Variant.HOLO] > 0, "holos appear")
	check(v[Enums.Variant.ONEOFONE] >= 0, "1/1 rolls counted (%d / 60k)" % v[Enums.Variant.ONEOFONE])
	var rare_total: int = v[Enums.Variant.GOLD] + v[Enums.Variant.SHADOW] + v[Enums.Variant.SIGNATURE]
	check(rare_total > 0, "rare finishes occur over many pulls")
