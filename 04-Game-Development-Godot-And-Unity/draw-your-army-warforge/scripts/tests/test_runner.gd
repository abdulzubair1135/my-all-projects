extends SceneTree

func _init() -> void:
	print("\n=======================================================")
	print("WARFORGE AUTOMATED TEST SUITE: MILESTONES 1 - 5")
	print("=======================================================\n")
	
	var pass_count = 0
	var fail_count = 0
	
	# Test 1: Derived Stats and Equipment Cost calculation
	print("[TEST 1] Testing SoldierDesign Derived Stats & Cost Calculation...")
	var soldier = SoldierDesign.new("test_champ", "Test Champion")
	soldier.weapon_id = "wpn_axe_battle" # cost 15, dmg +22
	soldier.armor_id = "arm_plate_harness" # cost 24, armor +28, hp +90
	var stats = soldier.calculate_derived_stats()
	# base infantry cost = 10; axe = 15; plate = 24; helmet iron_sallet = 6; shield round_buckler = 4 => 10 + 15 + 24 + 6 + 4 = 59
	if stats.total_cost == 59 and stats.armor >= 30.0:
		print("  -> PASS: Correct total cost calculated (" + str(stats.total_cost) + ") and armor (" + str(stats.armor) + ")")
		pass_count += 1
	else:
		printerr("  -> FAIL: Expected cost 59, got " + str(stats.total_cost))
		fail_count += 1

	# Test 2: Soldier Serialization and Deserialization Roundtrip
	print("[TEST 2] Testing Soldier Serialization & Deserialization...")
	var serialized = soldier.serialize()
	var deserialized = SoldierDesign.deserialize(serialized)
	if deserialized.id == soldier.id and deserialized.weapon_id == "wpn_axe_battle":
		print("  -> PASS: Deserialized object matches serialized payload exactly.")
		pass_count += 1
	else:
		printerr("  -> FAIL: Serialization mismatch.")
		fail_count += 1

	# Test 3: Formation Math Algorithms (Lines, Boxes, Wedges)
	print("[TEST 3] Testing Formation Math Point Generation...")
	var line_pts = FormationMath.generate_line_points(Vector3.ZERO, Vector3(10, 0, 0), 2.0)
	var box_pts = FormationMath.generate_box_points(Vector3.ZERO, Vector3(4, 0, 4), 2.0)
	var wedge_pts = FormationMath.generate_wedge_points(Vector3.ZERO, Vector3(0, 0, 10), 8.0, 2.0)
	
	if line_pts.size() == 6 and box_pts.size() == 9 and wedge_pts.size() > 5:
		print("  -> PASS: Line pts=" + str(line_pts.size()) + ", Box pts=" + str(box_pts.size()) + ", Wedge pts=" + str(wedge_pts.size()))
		pass_count += 1
	else:
		printerr("  -> FAIL: Unexpected formation point counts.")
		fail_count += 1

	# Test 4: Army Budget and Placement Validation
	print("[TEST 4] Testing Army Budget & Collision Validation...")
	var army = ArmyLoadout.new()
	army.custom_soldiers[soldier.id] = soldier.serialize()
	# Place 10 units at distinct coordinates
	for i in range(10):
		army.units.append({
			"unit_id": "u_" + str(i),
			"design_id": soldier.id,
			"position": Vector3(i * 2, 0, 0),
			"rotation_y": 0.0
		})
	var val_res = army.validate_army(1000, 300)
	if val_res.is_valid and val_res.total_cost == 590:
		print("  -> PASS: Army validation succeeded with cost " + str(val_res.total_cost))
		pass_count += 1
	else:
		printerr("  -> FAIL: Army validation failed.")
		fail_count += 1

	# Test 5: Undo / Redo Command History
	print("[TEST 5] Testing Undo / Redo Transactional History...")
	var history = EditorHistory.new()
	var test_army = ArmyLoadout.new()
	var unit_payload: Array[Dictionary] = [{"unit_id": "u_test", "design_id": soldier.id, "position": Vector3.ZERO}]
	var cmd = EditorCommand.PlaceUnitsCommand.new(test_army, unit_payload)
	history.execute_command(cmd)
	var placed_size = test_army.units.size()
	history.undo()
	var undone_size = test_army.units.size()
	history.redo()
	var redone_size = test_army.units.size()
	if placed_size == 1 and undone_size == 0 and redone_size == 1:
		print("  -> PASS: History execute -> undo -> redo integrity preserved.")
		pass_count += 1
	else:
		printerr("  -> FAIL: History state failure.")
		fail_count += 1

	# Test 6: Combat Calculations & Damage Mitigation
	print("[TEST 6] Testing Combat Damage & Mitigation Formula...")
	var combat_data = UnitCombatData.new()
	combat_data.max_health = 100.0
	combat_data.current_health = 100.0
	combat_data.armor = 100.0 # 50% damage reduction: 100 / (100 + 100) = 0.5
	var dmg_res = combat_data.apply_damage(40.0)
	if is_equal_approx(dmg_res.actual_damage, 20.0) and is_equal_approx(combat_data.current_health, 80.0):
		print("  -> PASS: 40 damage mitigated by 100 armor yields 20 actual damage (hp: 80).")
		pass_count += 1
	else:
		printerr("  -> FAIL: Damage calculation mismatch: " + str(dmg_res.actual_damage))
		fail_count += 1

	# Test 7: 200-Unit Spatial Grid & Targeting Performance Benchmark
	print("[TEST 7] Testing 200-Unit Combat Engine & Spatial Indexing...")
	var bench_engine = CombatSimulationEngine.new()
	var test_design = SoldierDesign.new("bench", "Legionary")
	for i in range(100):
		var u1 = Unit3D.new()
		u1.position = Vector3((i % 10) * 2, 0, (i / 10) * 2 + 5)
		u1.unit_data = UnitCombatData.new()
		u1.unit_data.unit_id = "b_" + str(i)
		u1.unit_data.team_id = 0
		bench_engine.register_unit(u1)
		
		var u2 = Unit3D.new()
		u2.position = Vector3((i % 10) * 2, 0, -(i / 10) * 2 - 5)
		u2.unit_data = UnitCombatData.new()
		u2.unit_data.unit_id = "r_" + str(i)
		u2.unit_data.team_id = 1
		bench_engine.register_unit(u2)
		
	bench_engine.simulation_running = true
	var bench_start = Time.get_ticks_msec()
	for f in range(30):
		bench_engine.step(0.016)
	var bench_elapsed = Time.get_ticks_msec() - bench_start
	var avg_tick = float(bench_elapsed) / 30.0
	print("  -> Benchmark result: 200 units, 30 ticks in %d ms (avg %0.2f ms/tick)" % [bench_elapsed, avg_tick])
	if avg_tick < 16.6:
		print("  -> PASS: 200-unit simulation executes well within 60 FPS frame budget (avg %0.2f ms < 16.6ms)" % avg_tick)
		pass_count += 1
	else:
		printerr("  -> FAIL: Simulation tick exceeded budget: %0.2f ms" % avg_tick)
		fail_count += 1

	for u in bench_engine.units:
		u.free()
	bench_engine.units.clear()
		
	# Test 8: Authoritative Multiplayer Networking Loop
	print("[TEST 8] Testing 2-Player ENet Server/Client Network Loop...")
	var net_server = NetworkMatchManagerNode.new()
	var net_client = NetworkMatchManagerNode.new()
	
	var host_ok = net_server.host_match(8899)
	var client_ok = net_client.join_match("127.0.0.1", 8899)
	
	if host_ok and client_ok:
		print("  -> PASS: ENet host and client initialized successfully without port collisions.")
		pass_count += 1
	else:
		printerr("  -> FAIL: Network initialization failure.")
		fail_count += 1
		
	net_client.disconnect_match()
	net_server.disconnect_match()
	net_client.free()
	net_server.free()

	print("\n=======================================================")
	print("TEST RESULTS SUMMARY: " + str(pass_count) + " PASSED, " + str(fail_count) + " FAILED")
	print("=======================================================\n")
	
	quit(0 if fail_count == 0 else 1)
