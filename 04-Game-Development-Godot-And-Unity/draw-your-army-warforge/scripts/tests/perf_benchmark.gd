extends SceneTree

func _init() -> void:
	print("[BENCHMARK] Initializing 200 autonomous combatants in simulation engine...")
	var engine = CombatSimulationEngine.new()
	var design_a = SoldierDesign.new("bench_a", "Blue Legion")
	var design_b = SoldierDesign.new("bench_b", "Red Legion")
	
	# Spawn 100 Blue vs 100 Red units without scene tree attachment
	for i in range(100):
		var u_a = Unit3D.new()
		u_a.position = Vector3((i % 10) * 2 - 10, 0, (i / 10) * 2 + 10)
		u_a.setup_from_design(design_a, 0, "blue_" + str(i))
		engine.register_unit(u_a)
		
		var u_b = Unit3D.new()
		u_b.position = Vector3((i % 10) * 2 - 10, 0, -(i / 10) * 2 - 10)
		u_b.setup_from_design(design_b, 1, "red_" + str(i))
		engine.register_unit(u_b)
		
	engine.simulation_running = true
	var start_ticks = Time.get_ticks_msec()
	var simulated_frames = 120
	var delta = 1.0 / 60.0
	
	print("[BENCHMARK] Executing %d simulation steps..." % simulated_frames)
	for f in range(simulated_frames):
		# Manual step of simulation engine logic
		engine.step(delta)
		# Step unit logic without CharacterBody3D physics engine server dependency
		for u in engine.units:
			if u.unit_data.is_alive and is_instance_valid(u.target_unit):
				var diff = u.target_unit.position - u.position
				diff.y = 0.0
				var dist = diff.length()
				if dist <= u.unit_data.attack_range:
					if u.attack_cooldown_timer <= 0.0:
						u.attack_cooldown_timer = u.unit_data.attack_interval
						var res = u.target_unit.unit_data.apply_damage(u.unit_data.damage)
						if res.killed:
							u.target_unit = null
				else:
					u.position += diff.normalized() * (u.unit_data.move_speed * delta)
			if u.attack_cooldown_timer > 0.0:
				u.attack_cooldown_timer -= delta
		
	var duration_msec = Time.get_ticks_msec() - start_ticks
	var avg_step_msec = float(duration_msec) / float(simulated_frames)
	
	print("[BENCHMARK RESULTS]")
	print("  -> Total Units: %d" % engine.units.size())
	print("  -> Execution Time for 120 ticks: %d ms" % duration_msec)
	print("  -> Average Tick Time: %0.2f ms (Budget: 16.6ms for 60fps)" % avg_step_msec)
	
	if avg_step_msec < 16.6:
		print("  -> BENCHMARK PERFORMANCE: EXCELLENT (Target < 16.6ms met)")
	else:
		print("  -> BENCHMARK PERFORMANCE: NEEDS OPTIMIZATION")
		
	# Clean up units
	for u in engine.units:
		u.free()
	engine.clear()
	
	print("[BENCHMARK] Test finished successfully.")
	quit(0)
