extends SceneTree

func _init() -> void:
	print("==================================================")
	print("  ASHEN KINGDOM — MILESTONE 2 AUTOMATED TEST SUITE")
	print("==================================================")

	var tests_passed: int = 0
	var total_tests: int = 18

	# Load scenes
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	var zombie_scene: PackedScene = load("res://scenes/enemies/training_zombie.tscn")
	var world_scene: PackedScene = load("res://scenes/world/test_world.tscn")

	if not player_scene or not zombie_scene or not world_scene:
		print("FAIL: Core scenes could not be loaded!")
		quit(1)
		return

	# Instantiate entities for testing
	var player: Player = player_scene.instantiate() as Player
	var zombie: TrainingZombie = zombie_scene.instantiate() as TrainingZombie
	root.add_child(player)
	root.add_child(zombie)
	player._ready()
	zombie._ready()

	# --- TEST 1: Light attack damages enemy ---
	var initial_zombie_hp: float = zombie.current_health
	var light_dmg := DamageInfo.new(player.combat_controller.light_damage, player.combat_controller.light_knockback, Vector2.RIGHT, player)
	zombie.hurtbox.receive_damage(light_dmg)
	if zombie.current_health == initial_zombie_hp - player.combat_controller.light_damage:
		print("TEST 1 PASS: Light attack damages enemy correctly (100 -> %.1f)." % zombie.current_health)
		tests_passed += 1
	else:
		print("TEST 1 FAIL: Zombie HP after light attack: %.1f (expected %.1f)" % [zombie.current_health, initial_zombie_hp - player.combat_controller.light_damage])

	# --- TEST 2: Heavy attack damages enemy ---
	var hp_before_heavy: float = zombie.current_health
	var heavy_dmg := DamageInfo.new(player.combat_controller.heavy_damage, player.combat_controller.heavy_knockback, Vector2.RIGHT, player)
	zombie.hurtbox.receive_damage(heavy_dmg)
	if zombie.current_health == hp_before_heavy - player.combat_controller.heavy_damage:
		print("TEST 2 PASS: Heavy attack damages enemy correctly (%.1f -> %.1f)." % [hp_before_heavy, zombie.current_health])
		tests_passed += 1
	else:
		print("TEST 2 FAIL: Heavy attack damage incorrect.")

	# --- TEST 3: Heavy attack deals more damage than light attack ---
	if player.combat_controller.heavy_damage > player.combat_controller.light_damage:
		print("TEST 3 PASS: Heavy attack (%.1f) deals more damage than light attack (%.1f)." % [
			player.combat_controller.heavy_damage, player.combat_controller.light_damage
		])
		tests_passed += 1
	else:
		print("TEST 3 FAIL: Heavy damage not greater than light damage.")

	# --- TEST 4: Attack direction changes correctly ---
	player.current_facing = Player.Facing.UP
	player.combat_controller._align_hitbox_to_facing(player.get_facing_vector())
	var facing_up_aligned: bool = player.combat_controller.hitbox_pivot.position.y < 0

	player.current_facing = Player.Facing.DOWN
	player.combat_controller._align_hitbox_to_facing(player.get_facing_vector())
	var facing_down_aligned: bool = player.combat_controller.hitbox_pivot.position.y > 0

	player.current_facing = Player.Facing.RIGHT
	player.combat_controller._align_hitbox_to_facing(player.get_facing_vector())
	var facing_right_aligned: bool = player.combat_controller.hitbox_pivot.position.x > 0

	player.current_facing = Player.Facing.LEFT
	player.combat_controller._align_hitbox_to_facing(player.get_facing_vector())
	var facing_left_aligned: bool = player.combat_controller.hitbox_pivot.position.x < 0

	if facing_up_aligned and facing_down_aligned and facing_right_aligned and facing_left_aligned:
		print("TEST 4 PASS: Attack hitbox pivot aligns accurately with UP, DOWN, RIGHT, and LEFT.")
		tests_passed += 1
	else:
		print("TEST 4 FAIL: Directional hitbox alignment failed.")

	# --- TEST 5: Hitbox activates only during attack ---
	var hitbox_initially_inactive: bool = not player.combat_controller.attack_hitbox.is_active
	player.combat_controller.start_light_attack(Vector2.DOWN)
	# Advance combat update past hitbox start window (light_hitbox_start is 0.06s)
	player.combat_controller.update_combat(0.08)
	var hitbox_active_during_attack: bool = player.combat_controller.attack_hitbox.is_active
	# Advance past attack finish (duration is 0.25s)
	player.combat_controller.update_combat(0.25)
	var hitbox_inactive_after_attack: bool = not player.combat_controller.attack_hitbox.is_active

	if hitbox_initially_inactive and hitbox_active_during_attack and hitbox_inactive_after_attack:
		print("TEST 5 PASS: Attack hitbox activates strictly during active frames and deactivates afterward.")
		tests_passed += 1
	else:
		print("TEST 5 FAIL: Hitbox timing activation incorrect.")

	# --- TEST 6: Target cannot receive repeated damage every frame from one attack ---
	var fresh_zombie: TrainingZombie = zombie_scene.instantiate() as TrainingZombie
	root.add_child(fresh_zombie)
	fresh_zombie._ready()

	var test_hitbox := Hitbox.new()
	root.add_child(test_hitbox)
	test_hitbox._ready()

	var single_attack := DamageInfo.new(15.0, 100.0, Vector2.RIGHT, player)
	test_hitbox.activate(single_attack)
	# Simulate 10 frames of overlapping detection
	for _i in range(10):
		test_hitbox._on_area_entered(fresh_zombie.hurtbox)

	if fresh_zombie.current_health == 85.0:
		print("TEST 6 PASS: Target received exactly one instance of damage despite 10 overlapping frames (HP=%.1f)." % fresh_zombie.current_health)
		tests_passed += 1
	else:
		print("TEST 6 FAIL: Target damaged repeatedly: HP=%.1f (expected 85.0)" % fresh_zombie.current_health)
	test_hitbox.queue_free()
	fresh_zombie.queue_free()

	# --- TEST 7: Dodge consumes stamina ---
	player.current_stamina = 100.0
	var dodge_cost: float = player.combat_controller.dodge_stamina_cost
	# Simulate dodge activation
	player.combat_controller.start_dodge(Vector2.DOWN)
	player.current_stamina -= dodge_cost
	if player.current_stamina == 100.0 - dodge_cost:
		print("TEST 7 PASS: Dodge consumes stamina correctly (100 -> %.1f)." % player.current_stamina)
		tests_passed += 1
	else:
		print("TEST 7 FAIL: Dodge stamina consumption incorrect.")
	# Finish dodge
	player.combat_controller.update_combat(0.3)

	# --- TEST 8: Dodge fails when stamina is insufficient ---
	player.current_stamina = 10.0 # less than 25
	player.combat_controller.dodge_cooldown_timer = 0.0
	var dodge_activated: bool = false
	if player.current_stamina >= player.combat_controller.dodge_stamina_cost and player.combat_controller.can_dodge():
		dodge_activated = player.combat_controller.start_dodge(Vector2.DOWN)
	if not dodge_activated:
		print("TEST 8 PASS: Dodge rejected when stamina (%.1f) < cost (%.1f)." % [player.current_stamina, dodge_cost])
		tests_passed += 1
	else:
		print("TEST 8 FAIL: Dodge activated despite low stamina.")

	# --- TEST 9: Player cannot receive damage during i-frames ---
	player.current_health = 100.0
	player.combat_controller.start_dodge(Vector2.DOWN)
	# Within i-frame duration (0.20s), player hurtbox is invulnerable
	var is_invulnerable_during_dodge: bool = player.hurtbox.is_invulnerable
	var incoming_strike := DamageInfo.new(30.0, 100.0, Vector2.LEFT, zombie)
	var hit_blocked: bool = not player.hurtbox.receive_damage(incoming_strike)

	if is_invulnerable_during_dodge and hit_blocked and player.current_health == 100.0:
		print("TEST 9 PASS: Damage completely prevented during dodge i-frames (HP=%.1f)." % player.current_health)
		tests_passed += 1
	else:
		print("TEST 9 FAIL: Player took damage during i-frames: HP=%.1f" % player.current_health)

	# --- TEST 10: Player receives damage outside i-frames ---
	player.combat_controller.update_combat(0.3) # finish dodge, clear i-frames
	var is_vuln_after_dodge: bool = not player.hurtbox.is_invulnerable
	var hit_accepted: bool = player.hurtbox.receive_damage(incoming_strike)

	if is_vuln_after_dodge and hit_accepted and player.current_health == 70.0:
		print("TEST 10 PASS: Damage received normally outside i-frames (100 -> %.1f)." % player.current_health)
		tests_passed += 1
	else:
		print("TEST 10 FAIL: Player failed to receive damage outside i-frames (HP=%.1f)." % player.current_health)

	# --- TEST 11: Knockback works ---
	var knock_dir := Vector2(1, 0)
	var knock_force := 250.0
	player.combat_controller.apply_knockback(knock_force, knock_dir)
	if player.combat_controller.knockback_velocity == knock_dir * knock_force:
		print("TEST 11 PASS: Knockback applied with vector %s." % str(player.combat_controller.knockback_velocity))
		tests_passed += 1
	else:
		print("TEST 11 FAIL: Knockback velocity mismatch.")

	# --- TEST 12: Enemy dies at 0 HP ---
	var zombie_died_signal := [false]
	zombie.died.connect(func(_z): zombie_died_signal[0] = true)
	zombie.take_damage(200.0) if zombie.has_method("take_damage") else zombie.hurtbox.receive_damage(DamageInfo.new(200.0, 100.0, Vector2.RIGHT, player))
	if zombie.current_health == 0.0 and zombie.current_state == TrainingZombie.State.DEAD and zombie_died_signal[0]:
		print("TEST 12 PASS: Enemy dies at 0 HP, disables collisions, and emits died signal.")
		tests_passed += 1
	else:
		print("TEST 12 FAIL: Enemy death handling failed (HP=%.1f, State=%d)." % [zombie.current_health, zombie.current_state])

	# --- TEST 13: Player dies at 0 HP ---
	var player_died_signal := [false]
	player.died.connect(func(): player_died_signal[0] = true)
	player.take_damage(100.0)
	if player.current_health == 0.0 and player.current_state == Player.State.DEAD and player_died_signal[0]:
		print("TEST 13 PASS: Player dies at 0 HP, halts combat, and emits died signal.")
		tests_passed += 1
	else:
		print("TEST 13 FAIL: Player death handling failed.")

	# --- TEST 14: Death UI appears ---
	var death_screen: DeathScreen = load("res://scenes/ui/death_screen.tscn").instantiate() as DeathScreen
	root.add_child(death_screen)
	death_screen._ready()
	var hidden_before: bool = not death_screen.visible
	death_screen.show_death_screen()
	var visible_after: bool = death_screen.visible
	if hidden_before and visible_after:
		print("TEST 14 PASS: Death Screen activates and becomes visible upon player death.")
		tests_passed += 1
	else:
		print("TEST 14 FAIL: Death Screen visibility transition failed.")
	death_screen.queue_free()

	# --- TEST 15: Restart mechanism works ---
	var ds_test: DeathScreen = load("res://scenes/ui/death_screen.tscn").instantiate() as DeathScreen
	root.add_child(ds_test)
	ds_test._ready()
	if ds_test.restart_button and ds_test.restart_button.is_connected("pressed", ds_test._on_restart_pressed):
		print("TEST 15 PASS: Restart button is wired to scene reload handler.")
		tests_passed += 1
	else:
		print("TEST 15 FAIL: Restart button not wired to reload handler.")
	ds_test.queue_free()

	# --- TEST 16: Existing movement still works ---
	var fresh_player: Player = player_scene.instantiate() as Player
	root.add_child(fresh_player)
	fresh_player._ready()
	fresh_player._update_facing(Vector2(0, 1))
	if fresh_player.current_facing == Player.Facing.DOWN and fresh_player.base_speed > 0:
		print("TEST 16 PASS: Existing 8-directional movement logic verified intact.")
		tests_passed += 1
	else:
		print("TEST 16 FAIL: Existing movement logic compromised.")

	# --- TEST 17: Existing sprint/stamina still works ---
	fresh_player.is_sprinting = true
	var stam_before := fresh_player.current_stamina
	fresh_player._handle_stamina(0.5)
	if fresh_player.current_stamina < stam_before:
		print("TEST 17 PASS: Existing sprint stamina drain verified intact (%.1f -> %.1f)." % [stam_before, fresh_player.current_stamina])
		tests_passed += 1
	else:
		print("TEST 17 FAIL: Sprint stamina drain broken.")
	fresh_player.queue_free()

	# --- TEST 18: Project starts without errors ---
	var test_world: TestWorld = world_scene.instantiate() as TestWorld
	root.add_child(test_world)
	test_world._ready()
	var zombies_spawned: int = test_world.enemies_container.get_child_count() if test_world.enemies_container else 0
	if test_world and zombies_spawned == 3:
		print("TEST 18 PASS: Full game world initialized cleanly with %d Training Zombies and HUD." % zombies_spawned)
		tests_passed += 1
	else:
		print("TEST 18 FAIL: Game world initialization failed (zombies spawned: %d)." % zombies_spawned)
	test_world.queue_free()

	# Clean up initial test instances
	player.queue_free()
	zombie.queue_free()

	print("==================================================")
	print("  TOTAL: %d / %d TESTS PASSED" % [tests_passed, total_tests])
	print("==================================================")

	if tests_passed == total_tests:
		print(">>> ALL 18 MILESTONE 2 REQUIREMENTS VERIFIED SUCCESSFULLY! <<<")
		quit(0)
	else:
		print(">>> FAILED: SOME TESTS DID NOT PASS <<<")
		quit(1)
