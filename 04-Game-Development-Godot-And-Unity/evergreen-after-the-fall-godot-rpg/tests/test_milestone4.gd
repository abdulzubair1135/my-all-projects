extends Node

# Evergreen: After the Fall - Milestone 4 Automated Test Suite
# Validates Animals (Chicken, Cow), Product Collection, Feeding, Affection, NPC Daily Schedules & Gifts, and Crafting Service

var farm_scene: Node2D = null
var player: CharacterBody2D = null

func _ready() -> void:
	print("==================================================")
	print("  EVERGREEN: AFTER THE FALL - MILESTONE 4 TEST   ")
	print("==================================================")
	
	var farm_packed = load("res://scenes/world/EvergreenFarm.tscn")
	assert(farm_packed != null, "EvergreenFarm.tscn must load")
	farm_scene = farm_packed.instantiate()
	add_child(farm_scene)
	
	player = farm_scene.get_node("Player")
	assert(player != null, "Player must exist")
	
	_test_farm_animals()

func _test_farm_animals() -> void:
	print("\n--- TEST 1: Farm Animals (Chicken & Cow) ---")
	
	var animals = get_tree().get_nodes_in_group("animals")
	assert(animals.size() >= 2, "Must spawn at least 2 farm animals (Chicken and Cow)")
	
	var chicken: FarmAnimal = null
	var cow: FarmAnimal = null
	for a in animals:
		if a.animal_type == "chicken":
			chicken = a
		elif a.animal_type == "cow":
			cow = a
	
	assert(chicken != null and cow != null, "Chicken and Cow nodes must exist")
	print("Found Chicken: %s (Affection: %d), Cow: %s (Affection: %d)" % [chicken.animal_name, chicken.affection, cow.animal_name, cow.affection])
	
	# 1. Collect Egg from chicken
	var eggs_before = InventoryService.get_item_count("produce_egg")
	assert(chicken.has_product == true, "Chicken starts with fresh egg ready")
	chicken.interact(player)
	assert(chicken.has_product == false, "Product collected")
	var eggs_after = InventoryService.get_item_count("produce_egg")
	assert(eggs_after == eggs_before + 1, "Egg added to player inventory")
	print("[PASS] Egg collection verified.")
	
	# 2. Feed chicken
	var seeds_before = InventoryService.get_item_count("seed_turnip")
	var affection_before = chicken.affection
	chicken.interact(player) # Feeds with turnip seed
	assert(chicken.is_fed == true, "Chicken must be marked fed")
	assert(chicken.affection > affection_before, "Feeding must increase affection")
	assert(InventoryService.get_item_count("seed_turnip") == seeds_before - 1, "1 seed consumed for feed")
	print("[PASS] Animal feeding and affection gain verified.")
	
	# 3. Advance Day -> produces new egg
	chicken.advance_day()
	assert(chicken.has_product == true, "Fed chicken produces egg next morning")
	assert(chicken.is_fed == false, "Fed status resets for new day")
	print("[PASS] Daily animal production cycle verified.")
	
	# 4. Collect Milk from cow
	var milk_before = InventoryService.get_item_count("produce_milk")
	cow.interact(player)
	assert(cow.has_product == false, "Milk collected")
	assert(InventoryService.get_item_count("produce_milk") == milk_before + 1, "Milk added to inventory")
	print("[PASS] Cow milk collection verified.")
	
	_test_npc_schedule_and_social()

func _test_npc_schedule_and_social() -> void:
	print("\n--- TEST 2: Named NPC Schedule & Social System ---")
	
	var npcs = get_tree().get_nodes_in_group("npcs")
	assert(npcs.size() >= 1, "Must have at least 1 NPC in farm hub")
	
	var thomas: NPCBase = npcs[0]
	assert(thomas != null and thomas.npc_name == "Thomas", "Thomas mentor NPC must exist")
	
	# 1. Schedule position check at 08:00 AM (morning crops check)
	thomas._evaluate_schedule(8)
	assert(thomas.position == Vector2(260, 290), "At 08:00 AM Thomas must be at garden plots (260, 290)")
	
	# 2. Schedule position check at 14:00 (afternoon workshop)
	thomas._evaluate_schedule(14)
	assert(thomas.position == Vector2(210, 160), "At 14:00 Thomas must be at workshop bench (210, 160)")
	print("[PASS] NPC daily schedule transitions verified.")
	
	# 3. Gift Giving (Thomas loves Turnip)
	InventoryService.add_item("produce_turnip", 2)
	InventoryService.select_slot(0)
	# Put turnip in active slot
	InventoryService.slots[0] = {"item_id": "produce_turnip", "count": 2}
	
	var trust_before = thomas.friendship
	thomas.interact(player)
	assert(thomas.friendship == trust_before + 15, "Loved gift (+15 friendship) awarded")
	print("[PASS] NPC gift preferences and friendship progression verified.")
	
	_test_crafting_system()

func _test_crafting_system() -> void:
	print("\n--- TEST 3: Crafting & Construction System ---")
	
	# Supply crafting materials: 20 Wood, 10 Stone
	InventoryService.add_item("mat_wood", 20)
	InventoryService.add_item("mat_stone", 10)
	
	# 1. Crafting as Archi (Standard recipe cost: 5 wood)
	GameState.current_protagonist = GameState.PROTAGONIST_ARCHI
	assert(CraftingService.can_craft("recipe_barricade") == true, "Must have enough wood to craft barricade")
	var wood_before = InventoryService.get_item_count("mat_wood")
	var barricades_before = InventoryService.get_item_count("crafted_barricade")
	
	var crafted = CraftingService.craft("recipe_barricade")
	assert(crafted == true, "Barricade craft must succeed")
	assert(InventoryService.get_item_count("crafted_barricade") == barricades_before + 1, "Barricade added to inventory")
	assert(InventoryService.get_item_count("mat_wood") == wood_before - 5, "Standard cost: 5 wood consumed")
	print("[PASS] Standard crafting verified.")
	
	# 2. Crafting as Danish: Field Engineer Perk (-1 wood discount on defense recipes)
	GameState.current_protagonist = GameState.PROTAGONIST_DANISH
	wood_before = InventoryService.get_item_count("mat_wood")
	barricades_before = InventoryService.get_item_count("crafted_barricade")
	
	crafted = CraftingService.craft("recipe_barricade")
	assert(crafted == true, "Danish barricade craft must succeed")
	assert(InventoryService.get_item_count("crafted_barricade") == barricades_before + 1, "Second barricade added")
	# Danish consumes only 4 wood (5 - 1 discount)!
	assert(InventoryService.get_item_count("mat_wood") == wood_before - 4, "Danish Field Engineer discount: only 4 wood consumed!")
	print("[PASS] Danish's Field Engineer crafting perk discount verified.")
	
	# 3. Crafting Medical Bandage (uses 1 egg + 1 wood)
	InventoryService.add_item("produce_egg", 1)
	assert(CraftingService.can_craft("recipe_bandage") == true, "Can craft sterile bandage")
	CraftingService.craft("recipe_bandage")
	assert(InventoryService.get_item_count("med_bandage") >= 1, "Sterile bandage crafted")
	print("[PASS] Medical crafting verified.")
	
	print("\n==================================================")
	print("  ALL MILESTONE 4 VERIFICATIONS PASSED (100%)    ")
	print("==================================================")
	get_tree().quit(0)
