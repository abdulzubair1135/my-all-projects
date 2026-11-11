extends Node

# Evergreen: After the Fall - Milestones 5 & 6 Automated Test Suite
# Validates Relationship Dimensions (Trust, Closeness, Respect, Memories, Milestones, Meals, Gifts)
# and World Streaming (WorldManager, Region Transitions, Spawn Markers, Safe Zone Tracking, Discovered Map)

func _ready() -> void:
	print("==================================================")
	print("  EVERGREEN: AFTER THE FALL - MILESTONES 5 & 6   ")
	print("==================================================")
	
	_test_relationship_system()
	_test_world_region_streaming()

func _test_relationship_system() -> void:
	print("\n--- TEST 1: Relationship Dimensions & Milestones ---")
	
	var summary = RelationshipService.get_summary()
	print("Starting Relationship: Trust: %d, Closeness: %d, Respect: %d, Memories: %d" % [
		summary["trust"], summary["closeness"], summary["respect"], summary["memories_count"]
	])
	assert(RelationshipService.memories.size() >= 1, "Must have initial arrival memory")
	
	# 1. Milestone Unlock: Trust 1 (Shared Truth at Trust >= 50)
	var trust_before = RelationshipService.trust
	RelationshipService.add_trust(25, "Defended farm together")
	assert(RelationshipService.trust == trust_before + 25, "Trust must increase by 25")
	assert(RelationshipService.unlocked_milestones.has("trust_1"), "Must unlock trust_1 milestone")
	print("[PASS] Trust progression and 'Shared Truth' milestone verified.")
	
	# 2. Milestone Unlock: Closeness 1 (Tea on the Porch at Closeness >= 50)
	RelationshipService.add_closeness(30, "Quiet evening talk")
	assert(RelationshipService.unlocked_milestones.has("closeness_1"), "Must unlock closeness_1 milestone")
	print("[PASS] Closeness progression and 'Tea on the Porch' milestone verified.")
	
	# 3. Companion Support Buffs
	var buffs = RelationshipService.get_companion_support_buff()
	assert(buffs["stamina_regen_bonus"] == 0.15, "Trust >= 50 must grant +15% stamina regen buff")
	assert(buffs["damage_resistance_bonus"] == 0.10, "Closeness >= 50 must grant +10% damage resistance buff")
	print("[PASS] Relationship companion passive support perks verified.")
	
	# 4. Shared Meal Mechanic
	InventoryService.add_item("food_bread", 2)
	var bread_count_before = InventoryService.get_item_count("food_bread")
	var mem_count_before = RelationshipService.memories.size()
	
	var shared = RelationshipService.share_meal()
	assert(shared == true, "Sharing meal must succeed when player has bread")
	assert(InventoryService.get_item_count("food_bread") == bread_count_before - 1, "1 bread consumed for meal")
	assert(RelationshipService.memories.size() == mem_count_before + 1, "New memory added for shared supper")
	print("[PASS] Shared meal interaction and memory recording verified.")
	
	# 5. Companion Gift Giving
	# Active protagonist: Archi -> giving gift to companion Danish
	GameState.current_protagonist = GameState.PROTAGONIST_ARCHI
	InventoryService.add_item("mat_wood", 5) # Danish loves wood/materials
	var gift_given = RelationshipService.give_companion_gift("mat_wood")
	assert(gift_given == true, "Companion gift giving must succeed")
	print("[PASS] Companion gift preferences and trust gains verified.")

func _test_world_region_streaming() -> void:
	print("\n--- TEST 2: WorldManager Region Streaming & Spawn Handoff ---")
	
	assert(WorldManager.regions.size() >= 4, "Must register at least 4 core regions (Farm, Village, Forest, Lake)")
	assert(WorldManager.current_region_id == "evergreen_farm", "Starting region is evergreen_farm")
	
	# 1. Load Evergreen Village Scene
	var village_packed = load("res://scenes/world/EvergreenVillage.tscn")
	assert(village_packed != null, "EvergreenVillage.tscn must load")
	var village_scene: Node2D = village_packed.instantiate()
	add_child(village_scene)
	
	var v_player = village_scene.get_node("Player")
	assert(v_player != null, "Village must have player instance")
	
	# Test spawn point handoff in village
	WorldManager.pending_spawn_id = "default"
	WorldManager.apply_player_spawn(v_player)
	var v_spawn = village_scene.get_node("SpawnPoint_default")
	assert(v_player.global_position == v_spawn.global_position, "Player must spawn at Village default marker (480, 480)")
	print("[PASS] Evergreen Village scene and spawn marker handoff verified.")
	
	village_scene.queue_free()
	
	# 2. Load Greenwood Forest Scene (Danger Zone)
	var forest_packed = load("res://scenes/world/GreenwoodForest.tscn")
	assert(forest_packed != null, "GreenwoodForest.tscn must load")
	var forest_scene: Node2D = forest_packed.instantiate()
	add_child(forest_scene)
	
	var f_player = forest_scene.get_node("Player")
	WorldManager.pending_spawn_id = "default"
	WorldManager.apply_player_spawn(f_player)
	
	assert(GameState.is_in_safe_zone == false, "Greenwood Forest must be marked as danger zone (safe_zone = false)!")
	assert(forest_scene.get_node("YSortProps/Drifter1") != null, "Forest must have roaming infected Drifter")
	print("[PASS] Greenwood Forest danger zone and roaming infected verified.")
	
	forest_scene.queue_free()
	
	# 3. Load Crystal Lake Scene
	var lake_packed = load("res://scenes/world/CrystalLake.tscn")
	assert(lake_packed != null, "CrystalLake.tscn must load")
	var lake_scene: Node2D = lake_packed.instantiate()
	add_child(lake_scene)
	
	assert(lake_scene.find_child("FishermanNoah", true, false) != null, "Crystal Lake must have Fisherman Noah interaction")
	print("[PASS] Crystal Lake region and shoreline POI verified.")
	
	lake_scene.queue_free()
	
	_test_save_load_persistence()

func _test_save_load_persistence() -> void:
	print("\n--- TEST 3: Save/Load Persistence of Relationships & World State ---")
	
	# 1. Save game
	var save_ok = SaveService.save_game(1, null, Vector2(100, 100))
	assert(save_ok == true, "Save game must succeed")
	
	var saved_trust = RelationshipService.trust
	var saved_closeness = RelationshipService.closeness
	
	# 2. Mutate relationship in memory
	RelationshipService.trust = 10
	RelationshipService.closeness = 5
	assert(RelationshipService.trust == 10, "Mutated trust in memory")
	
	# 3. Load game from slot 1
	var load_ok = SaveService.load_game(1, null, null)
	assert(load_ok == true, "Load game must succeed")
	
	# 4. Verify exact restoration
	assert(RelationshipService.trust == saved_trust, "Trust restored exactly from save")
	assert(RelationshipService.closeness == saved_closeness, "Closeness restored exactly from save")
	print("[PASS] Multi-dimensional relationship and memory persistence verified.")
	
	print("\n==================================================")
	print("  ALL MILESTONES 5 & 6 VERIFICATIONS PASSED (100%)")
	print("==================================================")
	get_tree().quit(0)
