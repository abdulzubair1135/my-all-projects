class_name TestWorld
extends Node2D

@onready var player: Player = $Player
@onready var hud: HUD = $HUD
@onready var ground_container: Node2D = $Ground
@onready var obstacles_container: Node2D = $Obstacles
@onready var enemies_container: Node2D = $Enemies
@onready var lights_container: Node2D = $Lights
@onready var canvas_modulate: CanvasModulate = $CanvasModulate
@onready var death_screen: DeathScreen = $DeathScreen

const TILE_SIZE: int = 32
const MAP_WIDTH: int = 26
const MAP_HEIGHT: int = 18

var tiles_texture: Texture2D = preload("res://assets/tiles/test_tiles.png")
var light_texture: Texture2D = preload("res://assets/environment/light_radial.png")
var zombie_scene: PackedScene = preload("res://scenes/enemies/training_zombie.tscn")
var walker_scene: PackedScene = preload("res://scenes/enemies/walker_zombie.tscn")
var runner_scene: PackedScene = preload("res://scenes/enemies/runner_zombie.tscn")
var royal_scene: PackedScene = preload("res://scenes/enemies/royal_zombie.tscn")

# Tile regions within test_tiles.png (128x64, each tile is 32x32)
# Row 0: 0=corrupted earth, 1=stone floor, 2=path/cobble, 3=water
# Row 1: 0=stone wall, 1=ruined pillar, 2=barricade, 3=brazier
const REGION_EARTH: Rect2 = Rect2(0, 0, 32, 32)
const REGION_STONE_FLOOR: Rect2 = Rect2(32, 0, 32, 32)
const REGION_PATH: Rect2 = Rect2(64, 0, 32, 32)
const REGION_WALL: Rect2 = Rect2(0, 32, 32, 32)
const REGION_PILLAR: Rect2 = Rect2(32, 32, 32, 32)
const REGION_BARRICADE: Rect2 = Rect2(64, 32, 32, 32)
const REGION_BRAZIER: Rect2 = Rect2(96, 32, 32, 32)

var brazier_lights: Array[PointLight2D] = []
var flicker_timer: float = 0.0

@onready var notification_label: Label = $HUD/NotificationLabel

func _ready() -> void:
	# Enable Y-sorting on obstacles, enemies, and player
	y_sort_enabled = true
	obstacles_container.y_sort_enabled = true
	if enemies_container:
		enemies_container.y_sort_enabled = true

	_build_ruined_courtyard()
	_create_shelter_entrance()
	_spawn_zombies()
	_connect_hud_and_death()

	# Spawn handling
	var center_pos := Vector2((MAP_WIDTH * TILE_SIZE) / 2.0, (MAP_HEIGHT * TILE_SIZE) / 2.0)
	player.position = center_pos

	var state = get_node_or_null("/root/GameState") if is_inside_tree() else null
	if state:
		state.current_scene = "res://scenes/world/test_world.tscn"
		if state.pending_spawn_id != "":
			var sp := SpawnManager.find_spawn_point(self, state.pending_spawn_id)
			if sp:
				SpawnManager.position_player_at_spawn(player, sp)
			state.pending_spawn_id = ""
		if state.pending_player_restore.size() > 0:
			SpawnManager.apply_saved_state(player, state.pending_player_restore)
			state.pending_player_restore.clear()

func _create_shelter_entrance() -> void:
	# Ruined doorway arch at top center (x=13, y=0)
	var door_pos := Vector2(13 * TILE_SIZE, 1 * TILE_SIZE)
	var door_interactable := Interactable.new()
	door_interactable.position = door_pos
	door_interactable.prompt_text = "E — Enter Shelter"
	door_interactable.prompt_offset = Vector2(0, -18)

	var shape := CircleShape2D.new()
	shape.radius = 22.0
	var col := CollisionShape2D.new()
	col.shape = shape
	door_interactable.add_child(col)

	door_interactable.interacted.connect(func(_p):
		var st = get_node_or_null("/root/SceneTransition")
		if st and st.has_method("change_scene"):
			st.change_scene("res://scenes/world/home/shelter.tscn", "spawn_home_entrance")
		else:
			get_tree().change_scene_to_file("res://scenes/world/home/shelter.tscn")
	)
	add_child(door_interactable)

func _process(delta: float) -> void:
	# Subtle atmospheric torchlight flicker
	flicker_timer += delta * 7.0
	for i in range(brazier_lights.size()):
		var light: PointLight2D = brazier_lights[i]
		var noise_val: float = sin(flicker_timer + i * 1.8) * 0.06 + cos(flicker_timer * 2.3 + i) * 0.04
		light.energy = 0.95 + noise_val

func _connect_hud_and_death() -> void:
	if player and hud:
		hud.register_player(player)
	if player and death_screen:
		if not player.died.is_connected(death_screen.show_death_screen):
			player.died.connect(death_screen.show_death_screen)

func _spawn_zombies() -> void:
	if not enemies_container:
		return

	# 1. Plague Walker patrolling left courtyard
	if walker_scene:
		var walker := walker_scene.instantiate() as BaseEnemy
		walker.position = Vector2(260, 200)
		enemies_container.add_child(walker)

	# 2. Plague Runner prowling right courtyard
	if runner_scene:
		var runner := runner_scene.instantiate() as BaseEnemy
		runner.position = Vector2(560, 200)
		enemies_container.add_child(runner)

	# 3. Corrupted Royal Guard Zombie guarding southern altar
	if royal_scene:
		var royal := royal_scene.instantiate() as BaseEnemy
		royal.position = Vector2(416, 380)
		enemies_container.add_child(royal)

func _build_ruined_courtyard() -> void:
	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			var world_pos := Vector2(x * TILE_SIZE, y * TILE_SIZE)
			var is_boundary: bool = (x == 0 or x == MAP_WIDTH - 1 or y == 0 or y == MAP_HEIGHT - 1)

			# Ground floor tile
			var floor_sprite := Sprite2D.new()
			floor_sprite.texture = tiles_texture
			floor_sprite.centered = false
			floor_sprite.position = world_pos

			# Distribute stone courtyard floor with corrupted earth edges
			var dist_from_center: float = Vector2(x - MAP_WIDTH / 2.0, y - MAP_HEIGHT / 2.0).length()
			if dist_from_center < 7.5:
				floor_sprite.region_enabled = true
				floor_sprite.region_rect = REGION_STONE_FLOOR
			elif (x + y) % 3 == 0:
				floor_sprite.region_enabled = true
				floor_sprite.region_rect = REGION_PATH
			else:
				floor_sprite.region_enabled = true
				floor_sprite.region_rect = REGION_EARTH

			ground_container.add_child(floor_sprite)

			# Perimeter Walls
			if is_boundary:
				_create_wall_obstacle(world_pos)

	# Place Ruined Pillars inside the courtyard
	var pillar_coords := [
		Vector2i(6, 5), Vector2i(19, 5),
		Vector2i(6, 12), Vector2i(19, 12),
		Vector2i(10, 8), Vector2i(15, 8)
	]
	for coord: Vector2i in pillar_coords:
		_create_pillar_obstacle(Vector2(coord.x * TILE_SIZE, coord.y * TILE_SIZE))

	# Place Braziers with warm atmospheric lights
	var brazier_coords := [
		Vector2i(3, 3), Vector2i(22, 3),
		Vector2i(3, 14), Vector2i(22, 14),
		Vector2i(12, 4), Vector2i(13, 13)
	]
	for coord: Vector2i in brazier_coords:
		_create_brazier(Vector2(coord.x * TILE_SIZE, coord.y * TILE_SIZE))

func _create_wall_obstacle(pos: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = pos + Vector2(TILE_SIZE / 2.0, TILE_SIZE / 2.0)
	body.collision_layer = 1
	body.collision_mask = 0

	var sprite := Sprite2D.new()
	sprite.texture = tiles_texture
	sprite.region_enabled = true
	sprite.region_rect = REGION_WALL
	body.add_child(sprite)

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(TILE_SIZE, TILE_SIZE)
	col.shape = shape
	body.add_child(col)

	obstacles_container.add_child(body)

func _create_pillar_obstacle(pos: Vector2) -> void:
	var body := StaticBody2D.new()
	body.y_sort_enabled = true
	body.position = pos + Vector2(TILE_SIZE / 2.0, TILE_SIZE / 2.0)
	body.collision_layer = 1
	body.collision_mask = 0

	var sprite := Sprite2D.new()
	sprite.texture = tiles_texture
	sprite.region_enabled = true
	sprite.region_rect = REGION_PILLAR
	# Sprite centered at feet for proper Y-sorting
	sprite.position = Vector2(0, -4)
	body.add_child(sprite)

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(20, 14)
	col.position = Vector2(0, 4)
	col.shape = shape
	body.add_child(col)

	obstacles_container.add_child(body)

func _create_brazier(pos: Vector2) -> void:
	var body := StaticBody2D.new()
	body.y_sort_enabled = true
	body.position = pos + Vector2(TILE_SIZE / 2.0, TILE_SIZE / 2.0)
	body.collision_layer = 1
	body.collision_mask = 0

	var sprite := Sprite2D.new()
	sprite.texture = tiles_texture
	sprite.region_enabled = true
	sprite.region_rect = REGION_BRAZIER
	sprite.position = Vector2(0, -4)
	body.add_child(sprite)

	var col := CollisionShape2D.new()
	var shape := CircleShape2D.new()
	shape.radius = 8.0
	col.position = Vector2(0, 4)
	col.shape = shape
	body.add_child(col)

	# 2D Point Light
	var light := PointLight2D.new()
	light.texture = light_texture
	light.color = Color(1.0, 0.72, 0.38, 1.0)
	light.energy = 1.0
	light.texture_scale = 1.8
	light.position = Vector2(0, -8)
	body.add_child(light)
	brazier_lights.append(light)

	obstacles_container.add_child(body)
