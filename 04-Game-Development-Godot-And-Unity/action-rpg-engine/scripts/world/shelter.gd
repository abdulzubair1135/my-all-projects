class_name Shelter
extends Node2D

@onready var player: Player = $Player
@onready var hud: HUD = $HUD
@onready var ground_container: Node2D = $Ground
@onready var obstacles_container: Node2D = $Obstacles
@onready var death_screen: DeathScreen = $DeathScreen
@onready var hearth_light: PointLight2D = $Obstacles/Fireplace/PointLight2D
@onready var notification_label: Label = $HUD/NotificationLabel

@onready var bed_interactable: Interactable = $Interactables/BedInteractable
@onready var hearth_interactable: Interactable = $Interactables/HearthInteractable
@onready var chest_interactable: Interactable = $Interactables/ChestInteractable
@onready var bench_interactable: Interactable = $Interactables/BenchInteractable
@onready var exit_door_interactable: Interactable = $Interactables/ExitDoorInteractable
@onready var shore_door_interactable: Interactable = $Interactables/ShoreDoorInteractable

const TILE_SIZE: int = 32
const ROOM_WIDTH: int = 16
const ROOM_HEIGHT: int = 12

var tiles_texture: Texture2D = preload("res://assets/tiles/test_tiles.png")
var light_texture: Texture2D = preload("res://assets/environment/light_radial.png")

var flicker_timer: float = 0.0

func _ready() -> void:
	y_sort_enabled = true
	obstacles_container.y_sort_enabled = true

	# Set safe checkpoint in GameState
	var state = _get_game_state()
	if state:
		state.current_scene = "res://scenes/world/home/shelter.tscn"
		state.set_current_spawn("spawn_home")

	_build_shelter_room()
	_connect_interactions()
	_connect_hud_and_death()

	# If there was a pending spawn request, apply it
	if state:
		var target_spawn: String = state.pending_spawn_id if state.pending_spawn_id != "" else "spawn_home"
		var sp := SpawnManager.find_spawn_point(self, target_spawn)
		if sp:
			SpawnManager.position_player_at_spawn(player, sp)
		if not state.pending_player_restore.is_empty():
			SpawnManager.apply_saved_state(player, state.pending_player_restore)
			state.pending_player_restore.clear()
		state.pending_spawn_id = ""

func _process(delta: float) -> void:
	flicker_timer += delta * 6.0
	if hearth_light:
		hearth_light.energy = 1.1 + sin(flicker_timer * 2.0) * 0.08 + cos(flicker_timer * 3.5) * 0.05

func _build_shelter_room() -> void:
	# Lay wooden/stone floor
	for y in range(ROOM_HEIGHT):
		for x in range(ROOM_WIDTH):
			var sprite := Sprite2D.new()
			sprite.texture = tiles_texture
			sprite.centered = false
			sprite.position = Vector2(x * TILE_SIZE, y * TILE_SIZE)
			sprite.region_enabled = true

			var is_wall: bool = (x == 0 or x == ROOM_WIDTH - 1 or y == 0 or y == ROOM_HEIGHT - 1)
			var is_door: bool = (y == ROOM_HEIGHT - 1 and (x == 7 or x == 8))

			if is_wall and not is_door:
				sprite.region_rect = Rect2(0, 32, 32, 32) # Wall
				_create_wall_collider(sprite.position)
			else:
				# Interior wooden/stone floor
				sprite.region_rect = Rect2(32, 0, 32, 32)

			ground_container.add_child(sprite)

func _create_wall_collider(pos: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = pos + Vector2(TILE_SIZE / 2.0, TILE_SIZE / 2.0)
	body.collision_layer = 1
	body.collision_mask = 0

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(TILE_SIZE, TILE_SIZE)
	col.shape = shape
	body.add_child(col)

	obstacles_container.add_child(body)

func _connect_interactions() -> void:
	if bed_interactable and not bed_interactable.interacted.is_connected(_on_bed_rest):
		bed_interactable.interacted.connect(_on_bed_rest)
	if hearth_interactable and not hearth_interactable.interacted.is_connected(_on_hearth_warm):
		hearth_interactable.interacted.connect(_on_hearth_warm)
	if chest_interactable and not chest_interactable.interacted.is_connected(_on_chest_open):
		chest_interactable.interacted.connect(_on_chest_open)
	if bench_interactable and not bench_interactable.interacted.is_connected(_on_bench_use):
		bench_interactable.interacted.connect(_on_bench_use)
	if exit_door_interactable and not exit_door_interactable.interacted.is_connected(_on_exit_to_courtyard):
		exit_door_interactable.interacted.connect(_on_exit_to_courtyard)
	if shore_door_interactable and not shore_door_interactable.interacted.is_connected(_on_exit_to_shore):
		shore_door_interactable.interacted.connect(_on_exit_to_shore)

func _connect_hud_and_death() -> void:
	if player and hud:
		hud.register_player(player)
	if player and death_screen:
		if not player.died.is_connected(death_screen.show_death_screen):
			player.died.connect(death_screen.show_death_screen)

func _on_bed_rest(p: Player) -> void:
	p.current_health = p.max_health
	p.current_stamina = p.max_stamina
	p.health_changed.emit(p.current_health, p.max_health)
	p.stamina_changed.emit(p.current_stamina, p.max_stamina)

	var state = _get_game_state()
	if state:
		state.advance_day()

	var sm = _get_save_manager()
	if sm:
		sm.autosave(p)

	_show_notification("RESTED & SAVED — DAY ADVANCED")

func _get_game_state() -> Node:
	if is_inside_tree():
		var node = get_node_or_null("/root/GameState")
		if node:
			return node
	if get_parent():
		return get_parent().get_node_or_null("GameState")
	return null

func _get_save_manager() -> Node:
	if is_inside_tree():
		var node = get_node_or_null("/root/SaveManager")
		if node:
			return node
	if get_parent():
		return get_parent().get_node_or_null("SaveManager")
	return null

func _on_hearth_warm(_p: Player) -> void:
	_show_notification("The dying embers grant fleeting warmth.")

func _on_chest_open(_p: Player) -> void:
	_show_notification("Ruined Chest — Storage coming in future milestone.")

func _on_bench_use(_p: Player) -> void:
	_show_notification("Decayed Workbench — Crafting coming in future milestone.")

func _on_exit_to_courtyard(_p: Player) -> void:
	var st = get_node_or_null("/root/SceneTransition")
	if st and st.has_method("change_scene"):
		st.change_scene("res://scenes/world/test_world.tscn", "spawn_courtyard")
	else:
		get_tree().change_scene_to_file("res://scenes/world/test_world.tscn")

func _on_exit_to_shore(_p: Player) -> void:
	var st = get_node_or_null("/root/SceneTransition")
	if st and st.has_method("change_scene"):
		st.change_scene("res://scenes/world/shore/the_shore.tscn", "spawn_shore_forest")
	else:
		get_tree().change_scene_to_file("res://scenes/world/shore/the_shore.tscn")

func _show_notification(text: String) -> void:
	if notification_label:
		notification_label.text = text
		notification_label.visible = true
		notification_label.modulate.a = 1.0
		var tween := create_tween()
		tween.tween_interval(1.8)
		tween.tween_property(notification_label, "modulate:a", 0.0, 0.4)
		tween.tween_callback(func(): notification_label.visible = false)
