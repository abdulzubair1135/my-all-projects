class_name TheShore
extends Node2D

@onready var player: Player = $Player
@onready var hud: HUD = $HUD
@onready var ground_container: Node2D = $Ground
@onready var obstacles_container: Node2D = $Obstacles
@onready var resources_container: Node2D = $Resources
@onready var wildlife_container: Node2D = $Wildlife
@onready var death_screen: DeathScreen = $DeathScreen
@onready var canvas_modulate: CanvasModulate = $CanvasModulate

@onready var world_time: Node = $WorldTime
@onready var season_manager: Node = $SeasonManager
@onready var weather_manager: Node = $WeatherManager
@onready var temperature_manager: Node = $TemperatureManager
@onready var world_lighting: Node = $WorldLighting

@onready var rain_particles: CPUParticles2D = $WeatherVFX/RainParticles
@onready var fog_overlay: ColorRect = $WeatherVFX/FogOverlay

@onready var intro_layer: CanvasLayer = $IntroLayer
@onready var intro_text_label: Label = $IntroLayer/ColorRect/Center/VBox/IntroLabel
@onready var intro_skip_label: Label = $IntroLayer/ColorRect/SkipPrompt

const TILE_SIZE: int = 32
const MAP_WIDTH: int = 48
const MAP_HEIGHT: int = 32

var tiles_texture: Texture2D = preload("res://assets/tiles/shore_tiles.png")
var objects_texture: Texture2D = preload("res://assets/environment/shore_objects.png")

var is_intro_playing: bool = false
var intro_step: int = 0
var intro_timer: float = 0.0
var intro_lines: Array[String] = [
	"Salt.",
	"Cold.",
	"Ash.",
	"Where... am I?",
	"The kingdom is gone."
]

func _ready() -> void:
	y_sort_enabled = true
	obstacles_container.y_sort_enabled = true
	wildlife_container.y_sort_enabled = true

	var state = _get_game_state()
	if state:
		state.current_scene = "res://scenes/world/shore/the_shore.tscn"
		if "shore" not in state.discovered_areas:
			state.discovered_areas.append("shore")

	_build_shore_terrain()
	_create_shipwreck_and_decorations()
	_create_resource_nodes()
	_create_wildlife()
	_create_shelter_entrance()
	_connect_hud_and_death()
	_connect_weather()

	# Handle spawn positioning
	if state and state.pending_spawn_id != "":
		var sp := SpawnManager.find_spawn_point(self, state.pending_spawn_id)
		if sp:
			SpawnManager.position_player_at_spawn(player, sp)
		state.pending_spawn_id = ""
	else:
		var sp := SpawnManager.find_spawn_point(self, "spawn_shore")
		if sp:
			SpawnManager.position_player_at_spawn(player, sp)

	if state and not state.pending_player_restore.is_empty():
		SpawnManager.apply_saved_state(player, state.pending_player_restore)
		state.pending_player_restore.clear()

	# Wake-up sequence on fresh start
	if state and state.game_day == 1 and state.play_time < 5.0:
		_start_intro_sequence()
	else:
		if intro_layer:
			intro_layer.visible = false

func _process(delta: float) -> void:
	if is_intro_playing:
		_process_intro_sequence(delta)

	# Update dynamic temperature
	if temperature_manager and world_time and season_manager and weather_manager:
		var s_idx := int(season_manager.current_season)
		var t: float = temperature_manager.update_temperature(s_idx, world_time.hour, weather_manager.current_weather)
		var state = _get_game_state()
		if state:
			state.temperature = t
			state.game_time = world_time.get_time_string()
			state.weather = weather_manager.current_weather
			state.season = s_idx
			state.season_day = season_manager.season_day
			state.year = season_manager.year

func _start_intro_sequence() -> void:
	is_intro_playing = true
	intro_step = 0
	intro_timer = 0.0
	if intro_layer:
		intro_layer.visible = true
	if intro_text_label:
		intro_text_label.text = intro_lines[0]
	if player:
		player.set_physics_process(false)

func _process_intro_sequence(delta: float) -> void:
	intro_timer += delta
	if intro_timer >= 1.6:
		intro_timer = 0.0
		intro_step += 1
		if intro_step < intro_lines.size():
			if intro_text_label:
				intro_text_label.text = intro_lines[intro_step]
		else:
			_end_intro_sequence()

func _end_intro_sequence() -> void:
	is_intro_playing = false
	if intro_layer:
		var tween := create_tween()
		tween.tween_property(intro_layer.get_node("ColorRect"), "modulate:a", 0.0, 0.8)
		tween.tween_callback(func(): intro_layer.visible = false)
	if player:
		player.set_physics_process(true)
	_show_notification("OBJECTIVE: Find Shelter Before Nightfall")

func _unhandled_input(event: InputEvent) -> void:
	if is_intro_playing and (event.is_action_pressed("interact") or event.is_action_pressed("dodge") or (event is InputEventKey and event.pressed)):
		_end_intro_sequence()
		get_viewport().set_input_as_handled()

func _build_shore_terrain() -> void:
	for y in range(MAP_HEIGHT):
		# Sinusoidal curved coastline: shore x ranges from 10 to 16
		var shore_x := 12 + int(sin(float(y) * 0.38) * 3.5)
		for x in range(MAP_WIDTH):
			var pos := Vector2(x * TILE_SIZE, y * TILE_SIZE)
			var sprite := Sprite2D.new()
			sprite.texture = tiles_texture
			sprite.centered = false
			sprite.position = pos
			sprite.region_enabled = true

			var is_boundary := (y == 0 or y == MAP_HEIGHT - 1 or x == 0)

			if x < shore_x - 3:
				# Deep ocean
				sprite.region_rect = Rect2(0, 0, 32, 32)
				_create_ocean_boundary(pos)
			elif x < shore_x:
				# Ocean surf
				sprite.region_rect = Rect2(32, 0, 32, 32)
			elif x < shore_x + 4:
				# Wet sand
				sprite.region_rect = Rect2(64, 0, 32, 32) if (x + y) % 2 == 0 else Rect2(96, 0, 32, 32)
			elif x < 34:
				# Dry sand / Dunes
				if (x + y) % 5 == 0:
					sprite.region_rect = Rect2(32, 32, 32, 32) # Sand with shells
				elif (x * 3 + y) % 7 == 0:
					sprite.region_rect = Rect2(64, 32, 32, 32) # Dune ridge
				else:
					sprite.region_rect = Rect2(0, 32, 32, 32)  # Dry sand base
			elif x < 38:
				# Coastal grass transition
				sprite.region_rect = Rect2(0, 64, 32, 32) if (x % 2 == 0) else Rect2(32, 64, 32, 32)
			else:
				# Coastal forest loam / pine needles
				sprite.region_rect = Rect2(64, 64, 32, 32) if (x % 2 == 0) else Rect2(96, 64, 32, 32)

			ground_container.add_child(sprite)

			if is_boundary:
				_create_cliff_obstacle(pos)

func _create_ocean_boundary(pos: Vector2) -> void:
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

func _create_cliff_obstacle(pos: Vector2) -> void:
	var body := StaticBody2D.new()
	body.position = pos + Vector2(TILE_SIZE / 2.0, TILE_SIZE / 2.0)
	body.collision_layer = 1
	body.collision_mask = 0

	var sprite := Sprite2D.new()
	sprite.texture = tiles_texture
	sprite.region_enabled = true
	sprite.region_rect = Rect2(0, 96, 32, 32)
	body.add_child(sprite)

	var col := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(TILE_SIZE, TILE_SIZE)
	col.shape = shape
	body.add_child(col)
	obstacles_container.add_child(body)

func _create_shipwreck_and_decorations() -> void:
	# 1. Shipwreck Main Hull
	var hull := StaticBody2D.new()
	hull.y_sort_enabled = true
	hull.position = Vector2(680, 460)
	hull.collision_layer = 1
	hull.collision_mask = 0

	var h_sprite := Sprite2D.new()
	h_sprite.texture = objects_texture
	h_sprite.region_enabled = true
	h_sprite.region_rect = Rect2(0, 0, 64, 32)
	h_sprite.scale = Vector2(1.5, 1.5)
	hull.add_child(h_sprite)

	var h_col := CollisionShape2D.new()
	var h_shape := RectangleShape2D.new()
	h_shape.size = Vector2(80, 30)
	h_col.shape = h_shape
	hull.add_child(h_col)
	obstacles_container.add_child(hull)

	# Investigation prompt on Shipwreck Hull
	var inspect_hull := Interactable.new()
	inspect_hull.position = Vector2(680, 460)
	inspect_hull.prompt_text = "E — Inspect Shipwreck"
	inspect_hull.prompt_offset = Vector2(0, -28)
	var col_i := CollisionShape2D.new()
	var circle_i := CircleShape2D.new()
	circle_i.radius = 35.0
	col_i.shape = circle_i
	inspect_hull.add_child(col_i)
	inspect_hull.interacted.connect(func(_p):
		_show_notification("The royal vessel was torn apart by something unnatural.")
	)
	add_child(inspect_hull)

	# 2. Broken Mast with Torn Canvas
	var mast := StaticBody2D.new()
	mast.y_sort_enabled = true
	mast.position = Vector2(740, 430)
	mast.collision_layer = 1
	mast.collision_mask = 0

	var m_sprite := Sprite2D.new()
	m_sprite.texture = objects_texture
	m_sprite.region_enabled = true
	m_sprite.region_rect = Rect2(64, 0, 32, 64)
	mast.add_child(m_sprite)

	var m_col := CollisionShape2D.new()
	var m_shape := RectangleShape2D.new()
	m_shape.size = Vector2(14, 20)
	m_col.position = Vector2(0, 20)
	m_col.shape = m_shape
	mast.add_child(m_col)
	obstacles_container.add_child(mast)

	# 3. Cargo Crates and Barrels
	var crate_positions := [Vector2(620, 480), Vector2(730, 490), Vector2(670, 520)]
	for cp in crate_positions:
		var crate := StaticBody2D.new()
		crate.y_sort_enabled = true
		crate.position = cp
		crate.collision_layer = 1
		crate.collision_mask = 0

		var c_spr := Sprite2D.new()
		c_spr.texture = objects_texture
		c_spr.region_enabled = true
		c_spr.region_rect = Rect2(96, 0, 32, 32)
		crate.add_child(c_spr)

		var c_col := CollisionShape2D.new()
		var c_shape := RectangleShape2D.new()
		c_shape.size = Vector2(20, 18)
		c_col.shape = c_shape
		crate.add_child(c_col)
		obstacles_container.add_child(crate)

	# Investigation on Royal Insignia Stone
	var insignia := Interactable.new()
	insignia.position = Vector2(710, 530)
	insignia.prompt_text = "E — Inspect Royal Crest"
	insignia.prompt_offset = Vector2(0, -18)
	var col_ins := CollisionShape2D.new()
	var shape_ins := CircleShape2D.new()
	shape_ins.radius = 25.0
	col_ins.shape = shape_ins
	insignia.add_child(col_ins)
	insignia.interacted.connect(func(_p):
		_show_notification("The crest of the Silver Stag... We never made it to safety.")
	)
	add_child(insignia)

	# 4. Coastal Pine Trees lining the forest edge (x=38 to 44)
	var tree_coords := [
		Vector2(1180, 200), Vector2(1250, 260), Vector2(1340, 180),
		Vector2(1200, 340), Vector2(1280, 420), Vector2(1360, 360),
		Vector2(1190, 560), Vector2(1270, 620), Vector2(1350, 580),
		Vector2(1220, 720), Vector2(1300, 780), Vector2(1380, 740)
	]
	for tp in tree_coords:
		var tree := StaticBody2D.new()
		tree.y_sort_enabled = true
		tree.position = tp
		tree.collision_layer = 1
		tree.collision_mask = 0

		var t_spr := Sprite2D.new()
		t_spr.texture = objects_texture
		t_spr.region_enabled = true
		t_spr.region_rect = Rect2(128, 0, 64, 64)
		t_spr.position = Vector2(0, -20)
		tree.add_child(t_spr)

		var t_col := CollisionShape2D.new()
		var t_shape := CircleShape2D.new()
		t_shape.radius = 12.0
		t_col.position = Vector2(0, 6)
		t_col.shape = t_shape
		tree.add_child(t_col)
		obstacles_container.add_child(tree)

func _create_resource_nodes() -> void:
	# Driftwood
	var wood := ResourceNode.new()
	wood.resource_id = "driftwood"
	wood.display_name = "Driftwood Log"
	wood.position = Vector2(560, 380)
	var w_spr := Sprite2D.new()
	w_spr.texture = objects_texture
	w_spr.region_enabled = true
	w_spr.region_rect = Rect2(0, 32, 64, 32)
	wood.add_child(w_spr)
	var w_col := CollisionShape2D.new()
	var w_shape := CircleShape2D.new()
	w_shape.radius = 24.0
	w_col.shape = w_shape
	wood.add_child(w_col)
	resources_container.add_child(wood)

	# Sea Rock
	var rock := ResourceNode.new()
	rock.resource_id = "sea_rock"
	rock.display_name = "Coastal Stone"
	rock.position = Vector2(580, 620)
	var r_spr := Sprite2D.new()
	r_spr.texture = objects_texture
	r_spr.region_enabled = true
	r_spr.region_rect = Rect2(96, 32, 32, 32)
	rock.add_child(r_spr)
	var r_col := CollisionShape2D.new()
	var r_shape := CircleShape2D.new()
	r_shape.radius = 20.0
	r_col.shape = r_shape
	rock.add_child(r_col)
	resources_container.add_child(rock)

	# Berry Bush in Forest
	var bush := ResourceNode.new()
	bush.resource_id = "coastal_berry"
	bush.display_name = "Wild Berry Bush"
	bush.position = Vector2(1150, 460)
	var b_spr := Sprite2D.new()
	b_spr.texture = objects_texture
	b_spr.region_enabled = true
	b_spr.region_rect = Rect2(64, 64, 32, 32)
	bush.add_child(b_spr)
	var b_col := CollisionShape2D.new()
	var b_shape := CircleShape2D.new()
	b_shape.radius = 20.0
	b_col.shape = b_shape
	bush.add_child(b_col)
	resources_container.add_child(bush)

func _create_wildlife() -> void:
	# Crabs on wet sand
	var crab1 := Crab.new()
	crab1.position = Vector2(460, 440)
	var spr1 := Sprite2D.new()
	spr1.name = "Sprite2D"
	crab1.add_child(spr1)
	var col1 := CollisionShape2D.new()
	var shape1 := CircleShape2D.new()
	shape1.radius = 8.0
	col1.shape = shape1
	crab1.add_child(col1)
	wildlife_container.add_child(crab1)

	var crab2 := Crab.new()
	crab2.position = Vector2(430, 620)
	var spr2 := Sprite2D.new()
	spr2.name = "Sprite2D"
	crab2.add_child(spr2)
	var col2 := CollisionShape2D.new()
	var shape2 := CircleShape2D.new()
	shape2.radius = 8.0
	col2.shape = shape2
	crab2.add_child(col2)
	wildlife_container.add_child(crab2)

	# Seagulls on beach
	var gull1 := Seagull.new()
	gull1.position = Vector2(620, 340)
	var g_spr1 := Sprite2D.new()
	g_spr1.name = "Sprite2D"
	gull1.add_child(g_spr1)
	var g_col1 := CollisionShape2D.new()
	var g_shape1 := CircleShape2D.new()
	g_shape1.radius = 8.0
	g_col1.shape = g_shape1
	gull1.add_child(g_col1)
	wildlife_container.add_child(gull1)

	# Cows on grassy plain / forest edge
	var cow1 := Cow.new()
	cow1.position = Vector2(1120, 320)
	var cow_spr1 := Sprite2D.new()
	cow_spr1.name = "Sprite2D"
	cow1.add_child(cow_spr1)
	var cow_col1 := CollisionShape2D.new()
	var cow_shape1 := CircleShape2D.new()
	cow_shape1.radius = 16.0
	cow_col1.shape = cow_shape1
	cow1.add_child(cow_col1)
	wildlife_container.add_child(cow1)

	# Dogs near forest path / shelter
	var dog1 := Dog.new()
	dog1.position = Vector2(1280, 520)
	var dog_spr1 := Sprite2D.new()
	dog_spr1.name = "Sprite2D"
	dog1.add_child(dog_spr1)
	var dog_col1 := CollisionShape2D.new()
	var dog_shape1 := CircleShape2D.new()
	dog_shape1.radius = 12.0
	dog_col1.shape = dog_shape1
	dog1.add_child(dog_col1)
	wildlife_container.add_child(dog1)

func _create_shelter_entrance() -> void:
	var door_pos := Vector2(1420, 480)
	var door := Interactable.new()
	door.position = door_pos
	door.prompt_text = "E — Enter Ruined Shelter"
	door.prompt_offset = Vector2(0, -22)

	var col := CollisionShape2D.new()
	var shape := CircleShape2D.new()
	shape.radius = 28.0
	col.shape = shape
	door.add_child(col)

	door.interacted.connect(func(_p):
		var state = _get_game_state()
		if state:
			state.current_objective = "Rest. Tomorrow, begin searching the ruins."
		var st = get_node_or_null("/root/SceneTransition")
		if st and st.has_method("change_scene"):
			st.change_scene("res://scenes/world/home/shelter.tscn", "spawn_home_entrance")
		else:
			get_tree().change_scene_to_file("res://scenes/world/home/shelter.tscn")
	)
	add_child(door)

func _connect_hud_and_death() -> void:
	if player and hud:
		hud.register_player(player)
	if player and death_screen:
		if not player.died.is_connected(death_screen.show_death_screen):
			player.died.connect(death_screen.show_death_screen)

func _connect_weather() -> void:
	if weather_manager:
		if not weather_manager.weather_changed.is_connected(_on_weather_changed):
			weather_manager.weather_changed.connect(_on_weather_changed)
		_on_weather_changed(weather_manager.current_weather)

func _on_weather_changed(weather: String) -> void:
	if rain_particles:
		rain_particles.emitting = (weather == "rain")
	if fog_overlay:
		fog_overlay.visible = (weather == "fog")

func _show_notification(text: String) -> void:
	if hud and hud.has_node("NotificationLabel"):
		var nl: Label = hud.get_node("NotificationLabel") as Label
		nl.text = text
		nl.visible = true
		nl.modulate.a = 1.0
		var tween := create_tween()
		tween.tween_interval(2.2)
		tween.tween_property(nl, "modulate:a", 0.0, 0.5)
		tween.tween_callback(func(): nl.visible = false)

func _get_game_state() -> Node:
	if is_inside_tree():
		var node = get_node_or_null("/root/GameState")
		if node:
			return node
	if get_parent():
		return get_parent().get_node_or_null("GameState")
	return null