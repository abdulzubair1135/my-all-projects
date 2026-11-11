extends Node

# Evergreen: After the Fall - Milestone 2 Automated Test Suite
# Validates Inventory System, Tool Usage, Crop Lifecycle, Farm Simulation, Sleep & Day Advance, and Save/Load Persistence

var farm_scene: Node2D = null
var player: CharacterBody2D = null
var farm_manager: FarmManager = null

func _ready() -> void:
	print("==================================================")
	print("  EVERGREEN: AFTER THE FALL - MILESTONE 2 TEST   ")
	print("==================================================")
	
	_test_inventory_system()
	_load_farm_environment()

func _test_inventory_system() -> void:
	print("\n--- TEST 1: Inventory System & Stacking ---")
	
	# Verify starting loadout
	assert(InventoryService.slots.size() == InventoryService.MAX_PLAYER_SLOTS, "Must have 12 player slots")
	assert(InventoryService.has_item("tool_hoe"), "Must have hoe in starting inventory")
	assert(InventoryService.has_item("tool_can"), "Must have watering can in starting inventory")
	assert(InventoryService.has_item("seed_turnip", 10), "Must have at least 10 turnip seeds")
	print("[PASS] Starting loadout verified.")
	
	# Slot selection
	InventoryService.select_slot(0) # Hoe
	var active = InventoryService.get_active_item()
	assert(active["id"] == "tool_hoe", "Active item should be tool_hoe")
	assert(active["use_type"] == "till", "Hoe use_type must be till")
	
	InventoryService.select_slot(1) # Can
	active = InventoryService.get_active_item()
	assert(active["id"] == "tool_can", "Active item should be tool_can")
	
	# Item Addition & Stacking
	var seeds_before = InventoryService.get_item_count("seed_turnip")
	var added = InventoryService.add_item("seed_turnip", 5)
	assert(added == true, "Must successfully add seeds")
	var seeds_after = InventoryService.get_item_count("seed_turnip")
	assert(seeds_after == seeds_before + 5, "Seeds count must increase by 5")
	print("[PASS] Item stacking and slot selection verified.")

func _load_farm_environment() -> void:
	print("\n--- TEST 2: Farm Environment & Crop Plot Generation ---")
	var farm_packed = load("res://scenes/world/EvergreenFarm.tscn")
	assert(farm_packed != null, "EvergreenFarm.tscn must load")
	farm_scene = farm_packed.instantiate()
	add_child(farm_scene)
	
	player = farm_scene.get_node("Player")
	farm_manager = farm_scene.get_node("FarmManager")
	assert(player != null and farm_manager != null, "Player and FarmManager must exist")
	assert(farm_manager.plots.size() == 18, "Must generate 18 crop plots in garden (6x3 grid)")
	print("[PASS] FarmManager initialized with %d plots." % farm_manager.plots.size())
	
	_test_crop_interactions()

func _test_crop_interactions() -> void:
	print("\n--- TEST 3: Tool Usage & Farming Actions ---")
	
	var plot_demo: CropPlot = farm_manager.plots["plot_0_0"]
	assert(plot_demo != null, "Plot 0,0 must exist")
	assert(plot_demo.crop_id == "crop_turnip", "Plot 0,0 demo crop must be turnip")
	assert(plot_demo.current_stage == 1, "Plot 0,0 demo crop starts at stage 1 (growing)")
	assert(plot_demo.is_watered == true, "Plot 0,0 demo crop starts watered")
	
	# Test Planting in plot_1_0
	var plot_empty: CropPlot = farm_manager.plots["plot_1_0"]
	assert(plot_empty.crop_id == "", "Plot 1,0 starts empty")
	
	# Equip turnip seeds (Slot 2)
	InventoryService.select_slot(2)
	var seeds_count_before = InventoryService.get_item_count("seed_turnip")
	plot_empty.interact(player) # Plant!
	assert(plot_empty.crop_id == "crop_turnip", "Plot 1,0 must now have turnip planted")
	assert(plot_empty.current_stage == 0, "Newly planted crop must be stage 0")
	assert(InventoryService.get_item_count("seed_turnip") == seeds_count_before - 1, "1 seed must be deducted from inventory")
	print("[PASS] Seed planting verified.")
	
	# Equip Watering Can (Slot 1) and water plot_1_0
	InventoryService.select_slot(1)
	assert(plot_empty.is_watered == false, "Plot 1,0 is dry before watering")
	plot_empty.interact(player) # Water!
	assert(plot_empty.is_watered == true, "Plot 1,0 must now be watered")
	print("[PASS] Soil watering verified.")
	
	_test_sleep_and_day_advance(plot_demo, plot_empty)

func _test_sleep_and_day_advance(plot_demo: CropPlot, plot_new: CropPlot) -> void:
	print("\n--- TEST 4: Sleep & Day Advance Simulation ---")
	
	# Drain some stamina first
	GameState.consume_stamina(40.0)
	var stamina_drained = GameState.get_current_stats()["stamina"]
	assert(stamina_drained < 120.0, "Stamina should be drained")
	
	# Trigger sleep at farmhouse
	farm_scene.trigger_sleep()
	
	# Verify Day advance
	assert(GameState.current_day == 2, "Current day must be Day 2")
	assert(GameState.current_hour == 6, "Time must be 06:00 AM after sleep")
	assert(GameState.get_current_stats()["stamina"] == 120.0, "Stamina fully restored after sleep")
	
	# Verify Crop growth
	assert(plot_demo.current_stage == 2, "Plot 0,0 turnip must have grown to Stage 2 (Mature / Ready)")
	assert(plot_demo.is_watered == false, "Soil must dry out in the morning")
	assert(plot_new.current_stage == 1, "Plot 1,0 turnip must have grown to Stage 1")
	assert(plot_new.is_watered == false, "Soil must dry out in the morning")
	print("[PASS] Sleep cycle, day progression, and crop stage advancement verified.")
	
	_test_harvest(plot_demo)

func _test_harvest(plot_demo: CropPlot) -> void:
	print("\n--- TEST 5: Crop Harvesting & Character Perks ---")
	
	# Active protagonist is Archi => has 'Green Thumb' double yield
	assert(GameState.current_protagonist == GameState.PROTAGONIST_ARCHI, "Protagonist is Archi")
	var turnip_produce_before = InventoryService.get_item_count("produce_turnip")
	
	plot_demo.interact(player) # Harvest!
	assert(plot_demo.crop_id == "", "Plot must be empty after harvest")
	assert(plot_demo.current_stage == 0, "Plot stage reset after harvest")
	var turnip_produce_after = InventoryService.get_item_count("produce_turnip")
	
	# Archi yields 2 turnips thanks to Green Thumb!
	assert(turnip_produce_after == turnip_produce_before + 2, "Archi must harvest 2x turnips via Green Thumb perk")
	print("[PASS] Harvest mechanics and Archi's Green Thumb perk verified.")
	
	_test_save_and_load()

func _test_save_and_load() -> void:
	print("\n--- TEST 6: Save & Load Persistence ---")
	
	# 1. Save game to Slot 1
	var save_success = SaveService.save_game(1, farm_manager, player.global_position)
	assert(save_success == true, "Saving game to slot 1 must succeed")
	assert(SaveService.has_save(1) == true, "Save file must exist on disk")
	
	# 2. Modify state (change day, consume item, move player)
	GameState.current_day = 99
	GameState.farm_name = "Corrupted Name"
	player.global_position = Vector2(999, 999)
	InventoryService.remove_item("produce_turnip", 2)
	assert(InventoryService.get_item_count("produce_turnip") == 0, "Inventory modified")
	
	# 3. Load game from Slot 1
	var load_success = SaveService.load_game(1, farm_manager, player)
	assert(load_success == true, "Loading game from slot 1 must succeed")
	
	# 4. Verify exact state restoration
	assert(GameState.current_day == 2, "Day restored to 2")
	assert(GameState.farm_name == "Evergreen Farm", "Farm name restored")
	assert(InventoryService.get_item_count("produce_turnip") == 2, "Harvested turnips restored in inventory")
	print("[PASS] 100% save and load persistence verified.")
	
	print("\n==================================================")
	print("  ALL MILESTONE 2 VERIFICATIONS PASSED (100%)    ")
	print("==================================================")
	get_tree().quit(0)
