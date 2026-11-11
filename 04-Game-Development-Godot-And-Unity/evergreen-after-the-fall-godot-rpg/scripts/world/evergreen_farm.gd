extends Node2D

# Evergreen: After the Fall - Evergreen Farm Region
# Core homestead hub: player residence, crop fields, water well, storage, bed rest, and companion presence

@onready var player: CharacterBody2D = $Player
@onready var companion: Node2D = $Companion
@onready var companion_sprite: Sprite2D = $Companion/Sprite2D
@onready var farm_manager: FarmManager = $FarmManager
@onready var time_modulate: CanvasModulate = $DayNightModulate
@onready var crops_container: Node2D = $CropsContainer

# Preset companion spots
const ARCHI_COMPANION_POS: Vector2 = Vector2(300, 260) # Garden plot
const DANISH_COMPANION_POS: Vector2 = Vector2(210, 160) # Farmhouse porch

const CROP_PLOT_SCENE = preload("res://scenes/farming/CropPlot.tscn")
const ANIMAL_SCENE = preload("res://scenes/animals/FarmAnimal.tscn")
const NPC_SCENE = preload("res://scenes/npcs/NPC.tscn")

func _ready() -> void:
	GameState.is_in_safe_zone = true
	EventBus.protagonist_switched.connect(_on_protagonist_switched)
	EventBus.time_updated.connect(_on_time_updated)
	
	_spawn_farm_plots()
	_spawn_animals()
	_spawn_npcs()
	_update_companion()
	_update_lighting(GameState.current_hour, GameState.current_minute)
	
	# Set player camera limits for Evergreen Farm (0 to 960 width, 0 to 640 height)
	if player and player.camera:
		player.camera.limit_left = 0
		player.camera.limit_top = 0
		player.camera.limit_right = 960
		player.camera.limit_bottom = 640
	
	WorldManager.apply_player_spawn(player)
	
	# Check for autosave on startup if not already loaded
	EventBus.notification_requested.emit("Evergreen Farm - Morning. Safe Zone.", 3.0)

func _spawn_farm_plots() -> void:
	# Spawn a 6x3 grid of interactive crop plots in the garden area
	# From tile x=9 to 14 (pixel 288 to 448), tile y=10 to 12 (pixel 320 to 384)
	for gy in range(3):
		for gx in range(6):
			var plot_node: CropPlot = CROP_PLOT_SCENE.instantiate()
			var px = (9 + gx) * 32
			var py = (10 + gy) * 32
			plot_node.position = Vector2(px, py)
			plot_node.plot_id = "plot_%d_%d" % [gx, gy]
			plot_node.is_tilled = true
			plot_node.is_watered = false
			
			# Pre-plant a small demo crop in the first plot for immediate feedback
			if gx == 0 and gy == 0:
				plot_node.crop_id = "crop_turnip"
				plot_node.current_stage = 1 # Growing turnip
				plot_node.is_watered = true
			
			crops_container.add_child(plot_node)
			farm_manager.register_plot(plot_node)

func _spawn_animals() -> void:
	var animals_container = Node2D.new()
	animals_container.name = "AnimalsContainer"
	animals_container.y_sort_enabled = true
	add_child(animals_container)
	
	# Spawn Chicken "Clucky"
	var chick: FarmAnimal = ANIMAL_SCENE.instantiate()
	chick.position = Vector2(260, 220)
	chick.animal_type = "chicken"
	chick.animal_name = "Clucky"
	animals_container.add_child(chick)
	
	# Spawn Cow "Bessie"
	var cow: FarmAnimal = ANIMAL_SCENE.instantiate()
	cow.position = Vector2(340, 230)
	cow.animal_type = "cow"
	cow.animal_name = "Bessie"
	animals_container.add_child(cow)

func _spawn_npcs() -> void:
	var npcs_container = Node2D.new()
	npcs_container.name = "NPCsContainer"
	npcs_container.y_sort_enabled = true
	add_child(npcs_container)
	
	# Spawn Thomas (Master Farmer & Mentor)
	var thomas: NPCBase = NPC_SCENE.instantiate()
	thomas.position = Vector2(260, 290)
	thomas.npc_id = "npc_thomas"
	npcs_container.add_child(thomas)

func _on_time_updated(hour: int, minute: int, _day: int, _season: String) -> void:
	_update_lighting(hour, minute)

func _update_lighting(hour: int, minute: int) -> void:
	if not time_modulate:
		return
	
	var total_minutes = hour * 60 + minute
	var target_color = Color.WHITE
	
	if total_minutes < 300: # 00:00 - 05:00 Night
		target_color = Color(0.28, 0.32, 0.48)
	elif total_minutes < 420: # 05:00 - 07:00 Dawn
		var t = float(total_minutes - 300) / 120.0
		target_color = Color(0.28, 0.32, 0.48).lerp(Color(0.95, 0.85, 0.72), t)
	elif total_minutes < 1020: # 07:00 - 17:00 Full Daylight
		target_color = Color(1.0, 1.0, 1.0)
	elif total_minutes < 1200: # 17:00 - 20:00 Dusk
		var t = float(total_minutes - 1020) / 180.0
		target_color = Color(1.0, 1.0, 1.0).lerp(Color(0.88, 0.62, 0.52), t)
	else: # 20:00 - 24:00 Night
		var t = float(total_minutes - 1200) / 240.0
		target_color = Color(0.88, 0.62, 0.52).lerp(Color(0.28, 0.32, 0.48), t)
	
	time_modulate.color = target_color

func trigger_sleep() -> void:
	# Restore stats for both protagonists
	for p_key in GameState.character_data.keys():
		var stats = GameState.character_data[p_key]
		stats["health"] = stats["max_health"]
		stats["stamina"] = stats["max_stamina"]
	
	var cur_stats = GameState.get_current_stats()
	EventBus.health_changed.emit(cur_stats["health"], cur_stats["max_health"])
	EventBus.stamina_changed.emit(cur_stats["stamina"], cur_stats["max_stamina"])
	
	# Advance clock to 06:00 AM next day
	GameState.current_hour = 6
	GameState.current_minute = 0
	GameState.current_day += 1
	
	# Signal day started -> triggers farm_manager.advance_all_crops()
	EventBus.day_started.emit(GameState.current_day)
	EventBus.time_updated.emit(6, 0, GameState.current_day, GameState.current_season)
	
	# Autosave current world state
	SaveService.save_game(1, farm_manager, player.global_position)
	EventBus.notification_requested.emit("Rested until morning (Day %d, 06:00 AM). Crops have grown!" % GameState.current_day, 3.5)

func _on_protagonist_switched(_new_protagonist: String) -> void:
	_update_companion()

func _update_companion() -> void:
	if not companion or not companion_sprite:
		return
	
	if GameState.current_protagonist == GameState.PROTAGONIST_ARCHI:
		# Playing as Archi => Companion is Danish
		companion.position = DANISH_COMPANION_POS
		companion_sprite.texture = load("res://assets/characters/danish/danish_spritesheet.png")
		companion_sprite.frame = 0 # Danish idle down
		companion.get_node("Interactable").display_name = "Danish"
	else:
		# Playing as Danish => Companion is Archi
		companion.position = ARCHI_COMPANION_POS
		companion_sprite.texture = load("res://assets/characters/archi/archi_spritesheet.png")
		companion_sprite.frame = 0 # Archi idle down
		companion.get_node("Interactable").display_name = "Archi"
