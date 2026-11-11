extends Node2D

const NPC_TEXTURE = preload("res://ShadowKingdom/pixel art/rpg_npcs.png")
const ANIMAL_TEXTURE = preload("res://ShadowKingdom/pixel art/rpg_animals.png")
const ITEM_TEXTURE = preload("res://ShadowKingdom/pixel art/rpg_items_decor.png")

# Spawning boundaries centered around the starting player location
# This ensures characters spawn near the player and stay within the grass/town area
var spawn_min = Vector2(100, 100)
var spawn_max = Vector2(800, 450)

func _ready():
	randomize()
	# Wait for 0.2s to let Godot import and initialize the map
	await get_tree().create_timer(0.2).timeout
	spawn_all_elements()

func spawn_all_elements():
	# Spawn 10 NPCs (mix of shopkeepers, guards, old ladies, kids)
	for i in range(10):
		var npc_type = randi() % 4
		var scale_val = 0.35 if npc_type == 3 else 0.45
		spawn_wanderer("NPC_" + str(i), NPC_TEXTURE, npc_type, 4, 4, 4, scale_val)
		
	# Spawn 10 Domestic Animals
	for i in range(10):
		var domestic_types = [0, 1, 2, 3, 4, 5]
		var animal_type = domestic_types[randi() % domestic_types.size()]
		var scale_val = 0.4
		if animal_type == 2: scale_val = 0.55 # Cow
		elif animal_type == 4: scale_val = 0.6 # Horse
		elif animal_type == 1: scale_val = 0.3 # Cat
		elif animal_type == 5: scale_val = 0.25 # Chicken
		spawn_wanderer("Domestic_" + str(i), ANIMAL_TEXTURE, animal_type, 12, 12, 12, scale_val)
		
	# Spawn 10 Wild Animals
	for i in range(10):
		var wild_types = [6, 7, 8, 9]
		var animal_type = wild_types[randi() % wild_types.size()]
		var scale_val = 0.4
		if animal_type == 7: scale_val = 0.48 # Deer
		elif animal_type == 9: scale_val = 0.25 # Rabbit
		spawn_wanderer("Wild_" + str(i), ANIMAL_TEXTURE, animal_type, 12, 12, 12, scale_val)
		
	# Spawn 10 Birds (sparrows, pigeons - scaled very small to look like flying birds)
	for i in range(10):
		var bird_types = [10, 11]
		var bird_type = bird_types[randi() % bird_types.size()]
		spawn_wanderer("Bird_" + str(i), ANIMAL_TEXTURE, bird_type, 12, 12, 12, 0.2, true)
		
	# Spawn 10 Collectible Items (1x1 tiles: coins, potions, keys)
	for i in range(10):
		var item_indices = [16, 17, 20, 24, 25, 26]
		var item_idx = item_indices[randi() % item_indices.size()]
		spawn_static_item("Item_" + str(i), ITEM_TEXTURE, 31 * 32 + item_idx, 32, 32)

func spawn_wanderer(name: String, texture: Texture2D, row: int, cols: int, hframes: int, vframes: int, scale_val: float, is_bird: bool = false):
	var body = CharacterBody2D.new()
	body.name = name
	body.y_sort_enabled = true
	
	# Apply realistic proportional scale
	body.scale = Vector2(scale_val, scale_val)
	
	# Spawn closer to player start to ensure immediate visibility
	body.position = Vector2(randf_range(150, 700), randf_range(150, 400))
	
	# Add Sprite
	var sprite = Sprite2D.new()
	sprite.name = "Sprite"
	sprite.texture = texture
	sprite.hframes = hframes
	sprite.vframes = vframes
	sprite.frame = row * cols
	body.add_child(sprite)
	
	# Add Collision
	var collision = CollisionShape2D.new()
	var shape = CircleShape2D.new()
	shape.radius = 8.0
	collision.shape = shape
	collision.position = Vector2(0, 8)
	body.add_child(collision)
	
	# Add Wander Logic script dynamically with boundary restriction and smooth speed (less jitter)
	var wander_script = GDScript.new()
	wander_script.source_code = """
extends CharacterBody2D

var speed = 15.0
var wander_dir = Vector2.ZERO
var wander_timer = 0.0
var anim_timer = 0.0
var anim_frame = 0

var row_idx = 0
var cols_count = 4
var is_flying = false

var limit_min = Vector2(100, 100)
var limit_max = Vector2(800, 450)

func _ready():
	choose_new_direction()
	if name.contains("Bird"):
		is_flying = true
		speed = 25.0
		collision_layer = 0
		collision_mask = 0

func _physics_process(delta):
	wander_timer -= delta
	if wander_timer <= 0.0:
		choose_new_direction()
		
	velocity = wander_dir * speed
	move_and_slide()
	
	# Force characters to stay inside the grass map boundaries
	position.x = clamp(position.x, limit_min.x, limit_max.x)
	position.y = clamp(position.y, limit_min.y, limit_max.y)
	
	# If they hit the boundary, force a direction change
	if position.x == limit_min.x or position.x == limit_max.x or position.y == limit_min.y or position.y == limit_max.y:
		choose_new_direction()
	
	# Animation loop (slower cycle rate to smooth out AI pixel offset wobbles)
	if velocity.length() > 0.1:
		anim_timer += delta
		if anim_timer >= 0.22:
			anim_timer = 0.0
			anim_frame = (anim_frame + 1) % 4
			update_sprite_frame()
	else:
		anim_frame = 0
		update_sprite_frame()

func choose_new_direction():
	wander_timer = randf_range(2.5, 6.0)
	if randf() < 0.4:
		wander_dir = Vector2.ZERO
	else:
		var angle = randf() * PI * 2
		wander_dir = Vector2(cos(angle), sin(angle))

func update_sprite_frame():
	var sprite = get_node("Sprite")
	if cols_count == 4:
		var base_frame = row_idx * 4
		if abs(wander_dir.x) > abs(wander_dir.y):
			sprite.flip_h = (wander_dir.x > 0)
			sprite.frame = base_frame + 2 + (anim_frame % 2)
		else:
			sprite.flip_h = false
			if wander_dir.y < 0:
				sprite.frame = base_frame + 1
			else:
				sprite.frame = base_frame + 0
	elif cols_count == 12:
		var base_frame = row_idx * 12
		if abs(wander_dir.x) > abs(wander_dir.y):
			sprite.flip_h = (wander_dir.x > 0)
			sprite.frame = base_frame + 6 + (anim_frame % 6)
		else:
			sprite.flip_h = false
			if wander_dir.y < 0:
				sprite.frame = base_frame + 3 + (anim_frame % 3)
			else:
				sprite.frame = base_frame + 0 + (anim_frame % 3)
"""
	wander_script.reload()
	body.set_script(wander_script)
	body.row_idx = row
	body.cols_count = cols
	body.limit_min = spawn_min
	body.limit_max = spawn_max
	
	add_child(body)

func spawn_static_item(name: String, texture: Texture2D, frame: int, hframes: int, vframes: int):
	var body = StaticBody2D.new()
	body.name = name
	body.y_sort_enabled = true
	
	body.scale = Vector2(1.0, 1.0)
	# Items spawn centered around the player area
	body.position = Vector2(randf_range(spawn_min.x + 50, spawn_max.x - 50), randf_range(spawn_min.y + 50, spawn_max.y - 50))
	
	var sprite = Sprite2D.new()
	sprite.name = "Sprite"
	sprite.texture = texture
	sprite.hframes = hframes
	sprite.vframes = vframes
	sprite.frame = frame
	body.add_child(sprite)
	
	var collision = CollisionShape2D.new()
	var shape = RectangleShape2D.new()
	shape.size = Vector2(10.0, 10.0)
	collision.shape = shape
	body.add_child(collision)
	
	add_child(body)
