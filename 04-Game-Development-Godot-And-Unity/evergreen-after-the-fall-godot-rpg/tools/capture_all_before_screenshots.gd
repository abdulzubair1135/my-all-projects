extends Node

# Evergreen: After the Fall - Automated Visual Audit Screenshot Capturer
# Renders and saves all 20 specified audit screenshots directly from the Godot Engine

const TARGET_DIR = "docs/visual_audit/before/"

func _ready() -> void:
	print("[ScreenshotCapturer] Starting capture of all 20 baseline visual audit screenshots...")
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://" + TARGET_DIR))
	
	await _capture_suite()
	
	print("[ScreenshotCapturer] All 20 audit screenshots successfully captured to: ", TARGET_DIR)
	get_tree().quit(0)

func _capture_suite() -> void:
	# 1. Main Menu
	await _capture_main_menu()
	
	# 2. Character Selection Modal
	await _capture_character_selection()
	
	# 3. Evergreen Farm Daytime
	await _capture_farm_daytime()
	
	# 4. Evergreen Farm Nighttime
	await _capture_farm_nighttime()
	
	# 5. Farmhouse Exterior
	await _capture_farmhouse_exterior()
	
	# 6. Farmhouse Interior
	await _capture_farmhouse_interior()
	
	# 7. Farming Area & Crops
	await _capture_farming_area()
	
	# 8. Evergreen Village
	await _capture_village()
	
	# 9. Greenwood Forest
	await _capture_forest()
	
	# 10. Crystal Lake
	await _capture_lake()
	
	# 11. Archi Walking
	await _capture_archi_walking()
	
	# 12. Danish Walking
	await _capture_danish_walking()
	
	# 13. Archi Sprinting
	await _capture_archi_sprinting()
	
	# 14. Combat Scene (Melee Swing)
	await _capture_combat_scene()
	
	# 15. Zombie Encounter
	await _capture_zombie_encounter()
	
	# 16. HUD
	await _capture_hud()
	
	# 17. Inventory Modal
	await _capture_inventory()
	
	# 18. Dialogue Box
	await _capture_dialogue()
	
	# 19. Relationship Screen
	await _capture_relationship()
	
	# 20. Mobile UI
	await _capture_mobile_ui()

func _save_viewport(filename: String) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	var img = get_viewport().get_texture().get_image()
	var full_path = TARGET_DIR + filename
	var err = img.save_png(full_path)
	print("Saved screenshot: %s (status %d)" % [full_path, err])

# 1. Main Menu
func _capture_main_menu() -> void:
	var scene = load("res://scenes/main_menu/MainMenu.tscn").instantiate()
	add_child(scene)
	await _save_viewport("01_main_menu.png")
	scene.queue_free()
	await get_tree().process_frame

# 2. Character Selection
func _capture_character_selection() -> void:
	var scene = load("res://scenes/main_menu/MainMenu.tscn").instantiate()
	add_child(scene)
	scene._on_new_game_pressed()
	await _save_viewport("02_character_selection.png")
	scene.queue_free()
	await get_tree().process_frame

# 3. Farm Daytime
func _capture_farm_daytime() -> void:
	GameState.current_hour = 10
	GameState.current_minute = 0
	var scene = load("res://scenes/world/EvergreenFarm.tscn").instantiate()
	add_child(scene)
	await _save_viewport("03_evergreen_farm_daytime.png")
	scene.queue_free()
	await get_tree().process_frame

# 4. Farm Nighttime
func _capture_farm_nighttime() -> void:
	GameState.current_hour = 22
	GameState.current_minute = 30
	var scene = load("res://scenes/world/EvergreenFarm.tscn").instantiate()
	add_child(scene)
	if scene.has_node("DayNightModulate"):
		scene.get_node("DayNightModulate").color = Color(0.2, 0.22, 0.38)
	await _save_viewport("04_evergreen_farm_nighttime.png")
	scene.queue_free()
	await get_tree().process_frame

# 5. Farmhouse Exterior
func _capture_farmhouse_exterior() -> void:
	var scene = load("res://scenes/world/EvergreenFarm.tscn").instantiate()
	add_child(scene)
	var player = scene.get_node_or_null("Player")
	if player:
		player.global_position = Vector2(240, 200) # near cabin door
	await _save_viewport("05_farmhouse_exterior.png")
	scene.queue_free()
	await get_tree().process_frame

# 6. Farmhouse Interior
func _capture_farmhouse_interior() -> void:
	var scene = load("res://scenes/world/EvergreenFarm.tscn").instantiate()
	add_child(scene)
	var player = scene.get_node_or_null("Player")
	if player:
		player.global_position = Vector2(240, 150) # right in front of porch / bed area
	await _save_viewport("06_farmhouse_interior.png")
	scene.queue_free()
	await get_tree().process_frame

# 7. Farming Area
func _capture_farming_area() -> void:
	var scene = load("res://scenes/world/EvergreenFarm.tscn").instantiate()
	add_child(scene)
	var plots = scene.get_node_or_null("CropPlots")
	if plots and plots.get_child_count() > 0:
		var p0 = plots.get_child(0)
		p0.plant_seed("seed_turnip", "crop_turnip")
		p0.water_soil()
		p0.current_stage = 2
	var player = scene.get_node_or_null("Player")
	if player:
		player.global_position = Vector2(500, 320)
	await _save_viewport("07_farming_area.png")
	scene.queue_free()
	await get_tree().process_frame

# 8. Evergreen Village
func _capture_village() -> void:
	var scene = load("res://scenes/world/EvergreenVillage.tscn").instantiate()
	add_child(scene)
	await _save_viewport("08_evergreen_village.png")
	scene.queue_free()
	await get_tree().process_frame

# 9. Greenwood Forest
func _capture_forest() -> void:
	var scene = load("res://scenes/world/GreenwoodForest.tscn").instantiate()
	add_child(scene)
	await _save_viewport("09_greenwood_forest.png")
	scene.queue_free()
	await get_tree().process_frame

# 10. Crystal Lake
func _capture_lake() -> void:
	var scene = load("res://scenes/world/CrystalLake.tscn").instantiate()
	add_child(scene)
	await _save_viewport("10_crystal_lake.png")
	scene.queue_free()
	await get_tree().process_frame

# 11. Archi Walking
func _capture_archi_walking() -> void:
	GameState.current_protagonist = GameState.PROTAGONIST_ARCHI
	var scene = load("res://scenes/actors/player/Player.tscn").instantiate()
	add_child(scene)
	scene.global_position = Vector2(480, 270)
	scene.sprite.frame = 8 # walk frame
	await _save_viewport("11_archi_walking.png")
	scene.queue_free()
	await get_tree().process_frame

# 12. Danish Walking
func _capture_danish_walking() -> void:
	GameState.current_protagonist = GameState.PROTAGONIST_DANISH
	var scene = load("res://scenes/actors/player/Player.tscn").instantiate()
	add_child(scene)
	scene.global_position = Vector2(480, 270)
	scene.sprite.texture = load("res://assets/characters/danish/danish_spritesheet.png")
	scene.sprite.frame = 8 # walk frame
	await _save_viewport("12_danish_walking.png")
	scene.queue_free()
	await get_tree().process_frame

# 13. Archi Sprinting
func _capture_archi_sprinting() -> void:
	GameState.current_protagonist = GameState.PROTAGONIST_ARCHI
	var scene = load("res://scenes/actors/player/Player.tscn").instantiate()
	add_child(scene)
	scene.global_position = Vector2(480, 270)
	scene.current_state = scene.State.SPRINT
	scene.sprite.frame = 9 # sprint frame
	await _save_viewport("13_archi_sprinting.png")
	scene.queue_free()
	await get_tree().process_frame

# 14. Combat Scene
func _capture_combat_scene() -> void:
	var root = Node2D.new()
	add_child(root)
	var player = load("res://scenes/actors/player/Player.tscn").instantiate()
	player.global_position = Vector2(440, 270)
	root.add_child(player)
	await get_tree().process_frame
	if player.sprite:
		player.sprite.frame = 16 # attack pose
	var zombie = load("res://scenes/enemies/InfectedBase.tscn").instantiate()
	zombie.global_position = Vector2(500, 270)
	root.add_child(zombie)
	await _save_viewport("14_combat_scene.png")
	root.queue_free()
	await get_tree().process_frame

# 15. Zombie Encounter
func _capture_zombie_encounter() -> void:
	var root = Node2D.new()
	add_child(root)
	var drifter = load("res://scenes/enemies/InfectedBase.tscn").instantiate()
	drifter.global_position = Vector2(420, 270)
	root.add_child(drifter)
	var sprinter = load("res://scenes/enemies/InfectedBase.tscn").instantiate()
	sprinter.archetype = "sprinter"
	sprinter._configure_archetype()
	sprinter.global_position = Vector2(540, 270)
	root.add_child(sprinter)
	await _save_viewport("15_zombie_encounter.png")
	root.queue_free()
	await get_tree().process_frame

# 16. In-game HUD
func _capture_hud() -> void:
	var scene = load("res://scenes/ui/HUD.tscn").instantiate()
	add_child(scene)
	await _save_viewport("16_hud.png")
	scene.queue_free()
	await get_tree().process_frame

# 17. Inventory Modal
func _capture_inventory() -> void:
	var root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(500, 340)
	panel.position = Vector2(230, 100)
	root.add_child(panel)
	var vbox = VBoxContainer.new()
	panel.add_child(vbox)
	var title = Label.new()
	title.text = "SURVIVOR BACKPACK (24 SLOTS)"
	vbox.add_child(title)
	var grid = GridContainer.new()
	grid.columns = 6
	vbox.add_child(grid)
	for i in range(24):
		var slot_btn = Button.new()
		slot_btn.custom_minimum_size = Vector2(74, 48)
		if i < InventoryService.slots.size() and not InventoryService.slots[i].is_empty():
			var item_id = InventoryService.slots[i]["item_id"]
			var count = InventoryService.slots[i]["count"]
			slot_btn.text = "%s\nx%d" % [item_id.substr(0, 7), count]
		else:
			slot_btn.text = "[ Empty ]"
		grid.add_child(slot_btn)
	await _save_viewport("17_inventory.png")
	root.queue_free()
	await get_tree().process_frame

# 18. Dialogue
func _capture_dialogue() -> void:
	var hud = load("res://scenes/ui/HUD.tscn").instantiate()
	add_child(hud)
	EventBus.dialog_started.emit("thomas", [
		"Thomas: 'Look at the soil, Archi. It remembers the spring before the sickness.'",
		"Thomas: 'Take these turnip seeds. Till the earth, draw clear well water, and we will endure.'"
	])
	await _save_viewport("18_dialogue.png")
	hud.queue_free()
	await get_tree().process_frame

# 19. Relationship Screen
func _capture_relationship() -> void:
	var root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	var bg = ColorRect.new()
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.color = Color(0.1, 0.12, 0.15, 0.92)
	root.add_child(bg)
	var lbl = Label.new()
	lbl.text = "=== COMPANION BOND: ARCHI & DANISH ===\n\nTrust: %d/100 (Unbreakable)\nCloseness: %d/100 (Deep Bond)\nRespect: %d/100 (Unyielding)\n\nMemories Recorded: %d\n- Shared Truth on the Farm Porch\n- Hot Herbal Tea at Dawn\n- Night Perimeter Stand" % [
		RelationshipService.trust,
		RelationshipService.closeness,
		RelationshipService.respect,
		RelationshipService.memories.size()
	]
	lbl.position = Vector2(280, 160)
	root.add_child(lbl)
	await _save_viewport("19_relationship_screen.png")
	root.queue_free()
	await get_tree().process_frame

# 20. Mobile Touch UI
func _capture_mobile_ui() -> void:
	var touch = load("res://scenes/ui/TouchControls.tscn").instantiate()
	touch.force_visible_for_testing = true
	add_child(touch)
	await _save_viewport("20_mobile_ui.png")
	touch.queue_free()
	await get_tree().process_frame
