extends SceneTree

func _init() -> void:
	print("--- Starting Ashen Kingdom Automated Verification Tests ---")
	var success := true

	# 1. Test Player scene loading
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	if not player_scene:
		print("FAIL: Could not load player.tscn")
		quit(1)
		return
	print("PASS: Player scene loaded.")

	var player: Player = player_scene.instantiate() as Player
	root.add_child(player)
	player.animated_sprite = player.get_node("AnimatedSprite2D")
	player._ready()

	# 2. Test initial properties
	if player.current_health != 100.0 or player.current_stamina != 100.0:
		print("FAIL: Initial health/stamina not 100.0")
		success = false
	else:
		print("PASS: Player initial stats verified (HP=100, Stamina=100).")

	# 3. Test 8-direction facing calculation
	player._update_facing(Vector2(0, 1))
	if player.current_facing != Player.Facing.DOWN:
		print("FAIL: Down facing calculation incorrect")
		success = false
	else:
		print("PASS: Facing DOWN correctly resolved.")

	player._update_facing(Vector2(0, -1))
	if player.current_facing != Player.Facing.UP:
		print("FAIL: Up facing calculation incorrect")
		success = false
	else:
		print("PASS: Facing UP correctly resolved.")

	player._update_facing(Vector2(1, 0))
	if player.current_facing != Player.Facing.RIGHT:
		print("FAIL: Right facing calculation incorrect")
		success = false
	else:
		print("PASS: Facing RIGHT correctly resolved.")

	player._update_facing(Vector2(-1, 0))
	if player.current_facing != Player.Facing.LEFT:
		print("FAIL: Left facing calculation incorrect")
		success = false
	else:
		print("PASS: Facing LEFT correctly resolved.")

	# Diagonal (down-right with dominant horizontal or vertical)
	player._update_facing(Vector2(1, 0.5).normalized())
	if player.current_facing != Player.Facing.RIGHT:
		print("FAIL: Diagonal facing incorrect")
		success = false
	else:
		print("PASS: Diagonal facing correctly mapped.")

	# 4. Test Animation & Directional logic
	player.current_state = Player.State.WALK
	player.current_facing = Player.Facing.LEFT
	player._update_animation()
	if player.animated_sprite.flip_h:
		print("FAIL: Left facing walk should NOT flip sprite (uses dedicated walk_left anim)")
		success = false
	else:
		print("PASS: Dedicated directional animation (walk_left) verified.")

	player.current_facing = Player.Facing.RIGHT
	player._update_animation()
	if player.animated_sprite.flip_h:
		print("FAIL: Right facing walk should NOT flip sprite horizontally")
		success = false
	else:
		print("PASS: Sprite flip_h false verified for RIGHT movement.")

	# 5. Test Stamina consumption during sprint
	player.is_sprinting = true
	var initial_stamina := player.current_stamina
	player._handle_stamina(0.5)
	if player.current_stamina >= initial_stamina:
		print("FAIL: Stamina should decrease while sprinting")
		success = false
	else:
		print("PASS: Stamina drain on sprint verified (%.1f -> %.1f)." % [initial_stamina, player.current_stamina])

	# 6. Test Damage and Death
	var died_signal_fired := [false]
	player.died.connect(func(): died_signal_fired[0] = true)
	player.take_damage(50.0)
	if player.current_health != 50.0:
		print("FAIL: Health should be 50.0 after 50 damage")
		success = false
	else:
		print("PASS: Damage handling verified (100 -> 50).")

	player.take_damage(60.0)
	if player.current_health != 0.0 or player.current_state != Player.State.DEAD or not died_signal_fired[0]:
		print("FAIL: Death handling failed (hp=%.1f, state=%d, died=%s)" % [player.current_health, player.current_state, str(died_signal_fired[0])])
		success = false
	else:
		print("PASS: Lethal damage and died signal verified.")

	# 7. Test World Scene Loading & Assembly
	var world_scene: PackedScene = load("res://scenes/world/test_world.tscn")
	if not world_scene:
		print("FAIL: Could not load test_world.tscn")
		success = false
	else:
		var world: TestWorld = world_scene.instantiate() as TestWorld
		world.ground_container = world.get_node("Ground")
		world.obstacles_container = world.get_node("Obstacles")
		world.lights_container = world.get_node("Lights")
		world.player = world.get_node("Player")
		world.hud = world.get_node("HUD")
		root.add_child(world)
		world._ready()

		if world.obstacles_container.get_child_count() == 0:
			print("FAIL: World obstacles not generated")
			success = false
		else:
			print("PASS: World instantiated with %d obstacles/colliders and %d brazier lights." % [
				world.obstacles_container.get_child_count(),
				world.brazier_lights.size()
			])
		world.queue_free()

	player.queue_free()

	if success:
		print("=== ALL TESTS PASSED SUCCESSFULLY ===")
		quit(0)
	else:
		print("=== SOME TESTS FAILED ===")
		quit(1)
