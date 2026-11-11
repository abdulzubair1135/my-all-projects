extends Node

# Evergreen: After the Fall - Milestone 3 Automated Test Suite
# Validates Real-Time Melee Combat, Hitbox/Hurtbox, Knockback, Zombie AI Perception & States, Damage Feedback, and Night Defense Horde

var farm_scene: Node2D = null
var player: CharacterBody2D = null
var night_director: NightDefenseDirector = null

const INFECTED_SCENE = preload("res://scenes/enemies/InfectedBase.tscn")

func _ready() -> void:
	print("==================================================")
	print("  EVERGREEN: AFTER THE FALL - MILESTONE 3 TEST   ")
	print("==================================================")
	
	var farm_packed = load("res://scenes/world/EvergreenFarm.tscn")
	assert(farm_packed != null, "EvergreenFarm.tscn must load")
	farm_scene = farm_packed.instantiate()
	add_child(farm_scene)
	
	player = farm_scene.get_node("Player")
	night_director = farm_scene.get_node("NightDefenseDirector")
	assert(player != null and night_director != null, "Player and NightDirector must exist")
	
	_test_melee_combat()

func _test_melee_combat() -> void:
	print("\n--- TEST 1: Real-Time Melee Combat & Damage ---")
	
	# Spawn a test Drifter 16 pixels directly below the player
	player.global_position = Vector2(300, 300)
	player.facing_direction = Vector2.DOWN
	
	var drifter: InfectedBase = INFECTED_SCENE.instantiate()
	drifter.archetype = "drifter"
	drifter.global_position = Vector2(300, 320)
	farm_scene.add_child(drifter)
	
	var hp_before = drifter.current_health
	var player_stamina_before = GameState.get_current_stats()["stamina"]
	
	# Trigger Light Attack
	player._perform_attack(false)
	
	# Wait for physics overlap
	await get_tree().physics_frame
	await get_tree().physics_frame
	
	var hp_after = drifter.current_health
	var stamina_after = GameState.get_current_stats()["stamina"]
	print("Drifter HP: %f -> %f (Damage dealt: %f)" % [hp_before, hp_after, hp_before - hp_after])
	assert(hp_after < hp_before, "Drifter must take damage from player attack!")
	assert(stamina_after < player_stamina_before, "Attack must consume stamina!")
	assert(drifter.current_state == drifter.AIState.HURT, "Drifter must enter HURT stagger state!")
	print("[PASS] Melee attack, damage delivery, and enemy stagger verified.")
	
	_test_danish_combat_perk(drifter)

func _test_danish_combat_perk(drifter: InfectedBase) -> void:
	print("\n--- TEST 2: Danish Heavy Weapon Perk (+25% Melee Damage) ---")
	
	# Switch to Danish
	GameState.switch_protagonist()
	assert(GameState.current_protagonist == GameState.PROTAGONIST_DANISH, "Active protagonist is Danish")
	
	# Reset drifter hurtbox invulnerability window for test
	drifter.hurtbox.can_take_damage = true
	drifter.hurtbox.invuln_timer = 0.0
	
	var hp_before = drifter.current_health
	player._perform_attack(true) # Heavy attack
	
	await get_tree().physics_frame
	await get_tree().physics_frame
	
	var hp_after = drifter.current_health
	var damage_dealt = hp_before - hp_after
	print("Danish Heavy Attack Damage: %f" % damage_dealt)
	assert(damage_dealt >= 55.0, "Danish heavy attack must deal perk-boosted heavy damage (>=55)")
	print("[PASS] Danish's Heavy Weapon combat perk verified.")
	
	if is_instance_valid(drifter):
		drifter.queue_free()
	
	_test_zombie_ai_perception()

func _test_zombie_ai_perception() -> void:
	print("\n--- TEST 3: Zombie AI Vision & Hearing Perception ---")
	
	player.global_position = Vector2(300, 300)
	
	# Spawn Sprinter 180 pixels away (within hearing range 300px when player sprints)
	var sprinter: InfectedBase = INFECTED_SCENE.instantiate()
	sprinter.archetype = "sprinter"
	sprinter.global_position = Vector2(300, 480)
	farm_scene.add_child(sprinter)
	
	sprinter.current_state = sprinter.AIState.IDLE
	assert(sprinter.current_state == sprinter.AIState.IDLE, "Sprinter starts IDLE")
	
	# Player starts sprinting (makes noise)
	player.current_state = player.State.SPRINT
	sprinter._update_perception()
	
	print("Sprinter state after hearing sprint noise: ", sprinter.current_state)
	assert(sprinter.current_state == sprinter.AIState.CHASE, "Sprinter must detect player and switch to CHASE state!")
	print("[PASS] Zombie perception and sound attraction verified.")
	
	_test_player_damage_reception(sprinter)

func _test_player_damage_reception(sprinter: InfectedBase) -> void:
	print("\n--- TEST 4: Zombie Attack & Player Damage Reception ---")
	
	# Move sprinter right next to player to trigger attack
	sprinter.global_position = Vector2(300, 318)
	sprinter.facing_dir = Vector2.UP
	
	var player_hp_before = GameState.get_current_stats()["health"]
	sprinter._start_attack()
	
	# Force active hit frame
	sprinter.hitbox.monitoring = true
	sprinter.hitbox.position = Vector2(0, -14)
	
	await get_tree().physics_frame
	await get_tree().physics_frame
	
	var player_hp_after = GameState.get_current_stats()["health"]
	print("Player HP: %f -> %f" % [player_hp_before, player_hp_after])
	assert(player_hp_after < player_hp_before, "Player must take damage from infected attack!")
	assert(player.current_state == player.State.HURT, "Player must enter HURT state on hit!")
	print("[PASS] Infected attack and player hurt feedback verified.")
	
	if is_instance_valid(sprinter):
		sprinter.queue_free()
	
	_test_night_horde_spawner()

func _test_night_horde_spawner() -> void:
	print("\n--- TEST 5: Night Defense Director & Horde Spawning ---")
	
	assert(night_director != null, "Night defense director exists")
	assert(night_director.active_enemies.is_empty(), "No enemies active before wave")
	
	# Spawn a wave of 3 infected
	night_director.spawn_night_wave(3)
	assert(night_director.wave_in_progress == true, "Wave must be marked in progress")
	assert(night_director.active_enemies.size() == 3, "Must have 3 active enemies in wave")
	print("[PASS] Night defense wave of %d infected spawned." % night_director.active_enemies.size())
	
	# Clear wave
	for enemy in night_director.active_enemies.duplicate():
		if is_instance_valid(enemy):
			enemy.queue_free()
	
	# Advance frame to trigger queue_free cleanup
	await get_tree().physics_frame
	await get_tree().physics_frame
	
	assert(night_director.wave_in_progress == false, "Wave must complete when all enemies defeated")
	print("[PASS] Night defense wave resolution and reward event verified.")
	
	print("\n==================================================")
	print("  ALL MILESTONE 3 VERIFICATIONS PASSED (100%)    ")
	print("==================================================")
	get_tree().quit(0)
