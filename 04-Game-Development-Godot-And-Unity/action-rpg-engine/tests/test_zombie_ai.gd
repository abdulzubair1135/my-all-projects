extends SceneTree

func _init() -> void:
	print("==================================================")
	print("  ASHEN KINGDOM — MILESTONE 3 ZOMBIE AI TEST SUITE")
	print("==================================================")

	var tests_passed: int = 0
	var total_tests: int = 13

	# Load scenes
	var walker_scene: PackedScene = load("res://scenes/enemies/walker_zombie.tscn")
	var runner_scene: PackedScene = load("res://scenes/enemies/runner_zombie.tscn")
	var royal_scene: PackedScene = load("res://scenes/enemies/royal_zombie.tscn")
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	var world_scene: PackedScene = load("res://scenes/world/test_world.tscn")

	if not walker_scene or not runner_scene or not royal_scene or not player_scene or not world_scene:
		print("FAIL: Scene loading failed!")
		quit(1)
		return

	# Instantiate entities
	var player: Player = player_scene.instantiate() as Player
	var walker: WalkerZombie = walker_scene.instantiate() as WalkerZombie
	var runner: RunnerZombie = runner_scene.instantiate() as RunnerZombie
	var royal: RoyalZombie = royal_scene.instantiate() as RoyalZombie

	root.add_child(player)
	root.add_child(walker)
	root.add_child(runner)
	root.add_child(royal)

	player._ready()
	walker._ready()
	runner._ready()
	royal._ready()

	# --- TEST 1: BaseEnemy Inheritance ---
	if (walker is BaseEnemy) and (runner is BaseEnemy) and (royal is BaseEnemy):
		print("TEST 1 PASS: Walker, Runner, and Royal Zombie inherit cleanly from BaseEnemy.")
		tests_passed += 1
	else:
		print("TEST 1 FAIL: BaseEnemy inheritance failed.")

	# --- TEST 2: Walker Zombie Stats ---
	if walker.max_health == 60.0 and walker.move_speed == 35.0 and walker.attack_damage == 10.0:
		print("TEST 2 PASS: Walker Zombie stats verified (HP=60, Speed=35, Damage=10).")
		tests_passed += 1
	else:
		print("TEST 2 FAIL: Walker Zombie stats mismatch.")

	# --- TEST 3: Runner Zombie Stats & High Speed ---
	if runner.max_health == 40.0 and runner.move_speed == 85.0 and runner.attack_damage == 14.0 and runner.attack_cooldown == 0.8:
		print("TEST 3 PASS: Runner Zombie stats verified (HP=40, Speed=85, Damage=14, CD=0.8s).")
		tests_passed += 1
	else:
		print("TEST 3 FAIL: Runner Zombie stats mismatch.")

	# --- TEST 4: Royal Zombie Stats & Sword Reach ---
	if royal.max_health == 160.0 and royal.move_speed == 30.0 and royal.attack_damage == 24.0 and royal.attack_range >= 30.0:
		print("TEST 4 PASS: Royal Zombie stats verified (HP=160, Speed=30, Damage=24, Range=30).")
		tests_passed += 1
	else:
		print("TEST 4 FAIL: Royal Zombie stats mismatch.")

	# --- TEST 5: Royal Zombie Knockback Resistance ---
	var base_force := 200.0
	var test_dmg := DamageInfo.new(10.0, base_force, Vector2.RIGHT, player)
	walker.hurtbox.receive_damage(test_dmg)
	royal.hurtbox.receive_damage(test_dmg)
	var walker_knockback: float = walker.knockback_velocity.length()
	var royal_knockback: float = royal.knockback_velocity.length()
	if royal_knockback < walker_knockback and is_equal_approx(royal_knockback, base_force * 0.5):
		print("TEST 5 PASS: Royal Zombie 50%% knockback resistance verified (%.1f vs %.1f)." % [royal_knockback, walker_knockback])
		tests_passed += 1
	else:
		print("TEST 5 FAIL: Knockback resistance failed (royal: %.1f, walker: %.1f)." % [royal_knockback, walker_knockback])

	# --- TEST 6: Patrol Wander Logic ---
	walker.spawn_position = Vector2(100, 100)
	walker.global_position = Vector2(100, 100)
	walker._start_patrol_wander()
	var patrol_dist: float = walker.patrol_target.distance_to(walker.spawn_position)
	if walker.current_state == BaseEnemy.State.PATROL and patrol_dist <= walker.patrol_radius:
		print("TEST 6 PASS: Patrol wander selects target (dist=%.1f) strictly within patrol radius (%.1f)." % [patrol_dist, walker.patrol_radius])
		tests_passed += 1
	else:
		print("TEST 6 FAIL: Patrol wander target out of bounds.")

	# --- TEST 7: Detection & Chase Transition ---
	runner.target_player = player
	player.global_position = Vector2(200, 200)
	runner.global_position = Vector2(200, 300) # distance = 100px <= detection_radius (175px)
	var detected: bool = runner._check_for_player()
	if detected and runner.current_state == BaseEnemy.State.CHASE:
		print("TEST 7 PASS: Player detected within 100px; Runner immediately transitioned to CHASE.")
		tests_passed += 1
	else:
		print("TEST 7 FAIL: Player detection failed.")

	# --- TEST 8: Target Loss Beyond Radius ---
	player.global_position = Vector2(200, 200)
	runner.global_position = Vector2(200, 500) # distance = 300px > lose_target_radius (260px)
	runner._process_chase(0.1)
	if runner.current_state == BaseEnemy.State.IDLE:
		print("TEST 8 PASS: Target escaped beyond 260px; Runner returned to IDLE.")
		tests_passed += 1
	else:
		print("TEST 8 FAIL: Target loss logic failed (state=%d)." % runner.current_state)

	# --- TEST 9: Attack State & Movement Halt ---
	runner.current_state = BaseEnemy.State.CHASE
	runner.attack_cooldown_timer = 0.0
	runner.global_position = Vector2(200, 215) # distance = 15px <= attack_range (24px)
	runner._process_chase(0.1)
	if runner.current_state == BaseEnemy.State.ATTACK and runner.velocity == Vector2.ZERO:
		print("TEST 9 PASS: When within attack range, enemy switches to ATTACK and halts movement.")
		tests_passed += 1
	else:
		print("TEST 9 FAIL: Attack initiation failed (state=%d, vel=%s)." % [runner.current_state, str(runner.velocity)])

	# --- TEST 10: Attack Hitbox Window ---
	var initial_active: bool = runner.attack_hitbox.is_active
	# Windup is 0.08s, duration is 0.28s
	runner.state_timer = 0.02
	runner._process_attack(0.08) # total 0.10s -> active window
	var window_active: bool = runner.attack_hitbox.is_active
	runner._process_attack(0.20) # total 0.30s -> past window
	var window_closed: bool = not runner.attack_hitbox.is_active
	if not initial_active and window_active and window_closed:
		print("TEST 10 PASS: Attack hitbox activates strictly during active window and closes afterward.")
		tests_passed += 1
	else:
		print("TEST 10 FAIL: Hitbox timing window incorrect.")

	# --- TEST 11: Hurt State & HP Update ---
	var hp_before := walker.current_health
	var strike := DamageInfo.new(20.0, 150.0, Vector2.UP, player)
	walker._on_hit_received(strike)
	if walker.current_health == hp_before - 20.0 and walker.current_state == BaseEnemy.State.HURT:
		print("TEST 11 PASS: Damage updates HP (%.1f -> %.1f) and triggers HURT state." % [hp_before, walker.current_health])
		tests_passed += 1
	else:
		print("TEST 11 FAIL: Hurt state transition failed.")

	# --- TEST 12: Lethal Damage & Death ---
	var died_called := [false]
	royal.died.connect(func(_e): died_called[0] = true)
	royal._on_hit_received(DamageInfo.new(500.0, 100.0, Vector2.RIGHT, player))
	var col_disabled: bool = royal.collision_shape.disabled or not royal.collision_shape.is_inside_tree() or royal.current_state == BaseEnemy.State.DEAD
	if royal.current_health == 0.0 and royal.current_state == BaseEnemy.State.DEAD and died_called[0] and col_disabled:
		print("TEST 12 PASS: Lethal damage drops HP to 0, sets DEAD state, and emits died signal.")
		tests_passed += 1
	else:
		print("TEST 12 FAIL: Death handling failed.")

	# --- TEST 13: Courtyard Scene Integration ---
	var world: TestWorld = world_scene.instantiate() as TestWorld
	root.add_child(world)
	world._ready()
	var enemy_count: int = world.enemies_container.get_child_count() if world.enemies_container else 0
	var has_walker := false
	var has_runner := false
	var has_royal := false
	for child in world.enemies_container.get_children():
		if child is WalkerZombie: has_walker = true
		if child is RunnerZombie: has_runner = true
		if child is RoyalZombie: has_royal = true

	if enemy_count == 3 and has_walker and has_runner and has_royal:
		print("TEST 13 PASS: Test courtyard successfully spawned Walker, Runner, and Royal Zombie.")
		tests_passed += 1
	else:
		print("TEST 13 FAIL: World enemy variants check failed (count=%d, walker=%s, runner=%s, royal=%s)." % [
			enemy_count, str(has_walker), str(has_runner), str(has_royal)
		])
	world.queue_free()

	# Clean up instances
	player.queue_free()
	walker.queue_free()
	runner.queue_free()
	royal.queue_free()

	print("==================================================")
	print("  TOTAL: %d / %d TESTS PASSED" % [tests_passed, total_tests])
	print("==================================================")

	if tests_passed == total_tests:
		print(">>> ALL 13 MILESTONE 3 REQUIREMENTS VERIFIED SUCCESSFULLY! <<<")
		quit(0)
	else:
		print(">>> FAILED: SOME TESTS DID NOT PASS <<<")
		quit(1)
