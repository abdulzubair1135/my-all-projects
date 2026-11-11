extends Node2D

# Evergreen: After the Fall - Farm Environment Generator
# Renders the 32x32 pixel tile grid, paths, farm plots, fences, boundaries, and props

const TILE_SIZE: int = 32
const MAP_WIDTH_TILES: int = 30 # 960 px
const MAP_HEIGHT_TILES: int = 20 # 640 px

const InteractableScript = preload("res://scripts/interactables/interactable.gd")
@onready var tileset_texture: Texture2D = preload("res://assets/tilesets/farm_tiles.png")
@onready var props_texture: Texture2D = preload("res://assets/props/farm_props.png")

func _ready() -> void:
	_generate_ground()
	_generate_boundary_colliders()
	_place_props()

func _generate_ground() -> void:
	# Create ground container
	var ground_node = Node2D.new()
	ground_node.name = "GroundVisuals"
	add_child(ground_node)
	move_child(ground_node, 0)
	
	for y in range(MAP_HEIGHT_TILES):
		for x in range(MAP_WIDTH_TILES):
			var tile_sprite = Sprite2D.new()
			tile_sprite.texture = tileset_texture
			tile_sprite.region_enabled = true
			tile_sprite.centered = false
			tile_sprite.position = Vector2(x * TILE_SIZE, y * TILE_SIZE)
			
			# Cobblestone path:
			# Vertical path from house (x=6..7, y=5..16)
			# Horizontal path to garden (x=8..14, y=8)
			# North exit path to Village (x=14..15, y=0..7)
			# East exit path to Forest (x=19..29, y=10..11)
			if (x >= 6 and x <= 7 and y >= 5 and y <= 16) or \
				 (x >= 8 and x <= 14 and y == 8) or \
				 (x >= 14 and x <= 15 and y >= 0 and y <= 7) or \
				 (x >= 19 and x <= 29 and y >= 10 and y <= 11):
				tile_sprite.region_rect = Rect2(128, 0, 32, 32) # Cobble path
			# Wood porch floor for house: x in [3..7], y in [4..5]
			elif x >= 3 and x <= 7 and y >= 4 and y <= 5:
				tile_sprite.region_rect = Rect2(224, 0, 32, 32) # Oak floorboards
			else:
				# Grass with occasional wildflowers
				if (x * 7 + y * 13) % 9 == 0:
					tile_sprite.region_rect = Rect2(32, 0, 32, 32) # Flower grass
				else:
					tile_sprite.region_rect = Rect2(0, 0, 32, 32) # Plain grass
			
			ground_node.add_child(tile_sprite)

func _generate_boundary_colliders() -> void:
	var bounds = StaticBody2D.new()
	bounds.name = "WorldBounds"
	bounds.collision_layer = 1
	bounds.collision_mask = 0
	add_child(bounds)
	
	# Left wall (x = 0)
	_add_wall_shape(bounds, Vector2(0, 320), Vector2(16, 640))
	# Right wall (top segment, y in 0..300)
	_add_wall_shape(bounds, Vector2(960, 150), Vector2(16, 300))
	# Right wall (bottom segment, y in 380..640)
	_add_wall_shape(bounds, Vector2(960, 510), Vector2(16, 260))
	# Bottom wall (y = 640)
	_add_wall_shape(bounds, Vector2(480, 640), Vector2(960, 16))
	# Top wall (left segment, x in 0..430)
	_add_wall_shape(bounds, Vector2(215, 0), Vector2(430, 16))
	# Top wall (right segment, x in 530..960)
	_add_wall_shape(bounds, Vector2(745, 0), Vector2(430, 16))

func _add_wall_shape(parent: StaticBody2D, pos: Vector2, size: Vector2) -> void:
	var col = CollisionShape2D.new()
	var box = RectangleShape2D.new()
	box.size = size
	col.shape = box
	col.position = pos
	parent.add_child(col)

func _place_props() -> void:
	var ysort_props = Node2D.new()
	ysort_props.name = "YSortProps"
	ysort_props.y_sort_enabled = true
	add_child(ysort_props)
	
	# Farmhouse at (160, 110)
	var house = StaticBody2D.new()
	house.name = "Farmhouse"
	house.position = Vector2(160, 110)
	house.y_sort_enabled = true
	
	var house_sprite = Sprite2D.new()
	house_sprite.texture = props_texture
	house_sprite.region_enabled = true
	house_sprite.region_rect = Rect2(0, 0, 128, 128)
	house_sprite.offset = Vector2(0, -64)
	house.add_child(house_sprite)
	
	var house_col = CollisionShape2D.new()
	var house_box = RectangleShape2D.new()
	house_box.size = Vector2(110, 48)
	house_col.shape = house_box
	house_col.position = Vector2(0, -24)
	house.add_child(house_col)
	
	# Farmhouse Door Interactable
	var door = InteractableScript.new()
	door.name = "HouseDoorInteractable"
	door.collision_layer = 2
	door.collision_mask = 0
	door.interactable_id = "farmhouse_door"
	door.display_name = "Farmhouse Door"
	door.prompt_text = "Rest / Switch Protagonist"
	door.action_type = "farmhouse_door"
	
	var door_col = CollisionShape2D.new()
	var door_circle = CircleShape2D.new()
	door_circle.radius = 24.0
	door_col.shape = door_circle
	door_col.position = Vector2(0, 16)
	door.add_child(door_col)
	house.add_child(door)
	
	# Warm Porch & Window Lantern Light
	var porch_light = _create_radial_light(Color(1.0, 0.82, 0.48), 1.25, 160)
	porch_light.position = Vector2(0, -20)
	house.add_child(porch_light)
	
	ysort_props.add_child(house)
	
	# Water Well at (384, 180)
	var well = StaticBody2D.new()
	well.name = "WaterWell"
	well.position = Vector2(384, 180)
	well.y_sort_enabled = true
	
	var well_sprite = Sprite2D.new()
	well_sprite.texture = props_texture
	well_sprite.region_enabled = true
	well_sprite.region_rect = Rect2(136, 0, 32, 48)
	well_sprite.offset = Vector2(0, -20)
	well.add_child(well_sprite)
	
	var well_col = CollisionShape2D.new()
	var well_box = RectangleShape2D.new()
	well_box.size = Vector2(26, 18)
	well_col.shape = well_box
	well_col.position = Vector2(0, 0)
	well.add_child(well_col)
	
	var well_interact = InteractableScript.new()
	well_interact.name = "WellInteractable"
	well_interact.collision_layer = 2
	well_interact.collision_mask = 0
	well_interact.interactable_id = "water_well"
	well_interact.display_name = "Fresh Water Well"
	well_interact.prompt_text = "Drink / Fill Water"
	well_interact.action_type = "water_well"
	
	var well_interact_col = CollisionShape2D.new()
	var well_int_shape = CircleShape2D.new()
	well_int_shape.radius = 24.0
	well_interact_col.shape = well_int_shape
	well_interact_col.position = Vector2(0, 8)
	well_interact.add_child(well_interact_col)
	well.add_child(well_interact)
	ysort_props.add_child(well)
	
	# Wooden Storage Chest at (234, 170)
	var chest = StaticBody2D.new()
	chest.name = "StorageChest"
	chest.position = Vector2(234, 170)
	chest.y_sort_enabled = true
	
	var chest_sprite = Sprite2D.new()
	chest_sprite.texture = props_texture
	chest_sprite.region_enabled = true
	chest_sprite.region_rect = Rect2(176, 12, 32, 24)
	chest_sprite.offset = Vector2(0, -8)
	chest.add_child(chest_sprite)
	
	var chest_col = CollisionShape2D.new()
	var chest_box = RectangleShape2D.new()
	chest_box.size = Vector2(26, 14)
	chest_col.shape = chest_box
	chest_col.position = Vector2(0, 0)
	chest.add_child(chest_col)
	
	var chest_interact = InteractableScript.new()
	chest_interact.name = "ChestInteractable"
	chest_interact.collision_layer = 2
	chest_interact.collision_mask = 0
	chest_interact.interactable_id = "storage_chest"
	chest_interact.display_name = "Farm Supply Chest"
	chest_interact.prompt_text = "Open Storage"
	chest_interact.action_type = "storage_chest"
	
	var chest_int_col = CollisionShape2D.new()
	var chest_int_shape = CircleShape2D.new()
	chest_int_shape.radius = 22.0
	chest_int_col.shape = chest_int_shape
	chest_int_col.position = Vector2(0, 6)
	chest_interact.add_child(chest_int_col)
	chest.add_child(chest_interact)
	ysort_props.add_child(chest)
	
	# Signpost at (440, 70)
	var signpost = InteractableScript.new()
	signpost.name = "Signpost"
	signpost.position = Vector2(440, 70)
	signpost.collision_layer = 2
	signpost.collision_mask = 0
	signpost.interactable_id = "farm_sign"
	signpost.display_name = "Road Signpost"
	signpost.prompt_text = "Read Sign"
	signpost.action_type = "signpost"
	
	var sign_col = CollisionShape2D.new()
	var sign_shape = CircleShape2D.new()
	sign_shape.radius = 20.0
	sign_col.shape = sign_shape
	signpost.add_child(sign_col)
	ysort_props.add_child(signpost)
	
	# Perimeter Trees
	var tree_coords = [
		Vector2(40, 60), Vector2(100, 50), Vector2(800, 60), Vector2(880, 70),
		Vector2(40, 300), Vector2(50, 480), Vector2(120, 580),
		Vector2(700, 580), Vector2(820, 560), Vector2(900, 480), Vector2(920, 200)
	]
	for pos in tree_coords:
		_spawn_tree(ysort_props, pos)

func _spawn_tree(parent: Node2D, pos: Vector2) -> void:
	var tree = StaticBody2D.new()
	tree.position = pos
	tree.y_sort_enabled = true
	
	var spr = Sprite2D.new()
	spr.texture = props_texture
	spr.region_enabled = true
	spr.region_rect = Rect2(136, 56, 64, 96)
	spr.offset = Vector2(0, -42)
	tree.add_child(spr)
	
	var col = CollisionShape2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 12.0
	col.shape = circle
	col.position = Vector2(0, -4)
	tree.add_child(col)
	parent.add_child(tree)

func _create_radial_light(color: Color, energy: float, size: int) -> PointLight2D:
	var light = PointLight2D.new()
	light.color = color
	light.energy = energy
	var grad = Gradient.new()
	grad.set_color(0, Color(1, 1, 1, 1))
	grad.set_color(1, Color(0, 0, 0, 0))
	var tex = GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.0, 0.5)
	tex.width = size
	tex.height = size
	light.texture = tex
	return light
