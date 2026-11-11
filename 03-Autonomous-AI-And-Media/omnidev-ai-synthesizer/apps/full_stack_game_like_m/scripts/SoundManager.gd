class_name DroppedItem
extends StaticBody3D

@export var block_type: int = 1
@export var count: int = 1

var _float_time: float = 0.0

func _ready():
	# Mesh
	var mesh_instance = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = Vector3(0.25, 0.25, 0.25)
	mesh_instance.mesh = box
	var mat = StandardMaterial3D.new()
	mat.albedo_color = get_block_color(block_type)
	mat.roughness = 0.6
	mesh_instance.material_override = mat
	add_child(mesh_instance)
	
	# Collision
	var collision = CollisionShape3D.new()
	var shape = BoxShape3D.new()
	shape.size = Vector3(0.25, 0.25, 0.25)
	collision.shape = shape
	add_child(collision)
	
	# Area for pickup detection
	var area = Area3D.new()
	area.name = "PickupArea"
	var area_shape = CollisionShape3D.new()
	area_shape.shape = BoxShape3D.new()
	area_shape.shape.size = Vector3(0.5, 0.5, 0.5)
	area.add_child(area_shape)
	add_child(area)
	area.body_entered.connect(_on_body_entered)
	
	# Slight random rotation
	rotation.y = randf_range(0, TAU)
	
	# Float animation setup
	set_process(true)

func _process(delta: float):
	_float_time += delta
	# Bob up and down
	position.y += sin(_float_time * 2.0) * 0.002
	# Gentle rotation
	rotation.y += delta * 0.5

func _on_body_entered(body):
	if body is Player:
		var player = body
		if player.add_item(block_type, count):
			# Play pickup sound
			if has_node("/root/SoundManager"):
				var sm = get_node("/root/SoundManager")
				if sm.has_method("play_pickup"):
					sm.play_pickup()
			queue_free()

func get_block_color(type: int) -> Color:
	match type:
		1: return Color(0.32, 0.20, 0.10)   # DIRT
		2: return Color(0.15, 0.38, 0.08)   # GRASS
		3: return Color(0.32, 0.32, 0.35)   # STONE
		4: return Color(0.22, 0.12, 0.05)   # WOOD
		5: return Color(0.05, 0.30, 0.05)   # LEAVES
		6: return Color(0.55, 0.45, 0.28)   # PLANK
		7: return Color(0.55, 0.70, 0.80, 0.35) # GLASS
		8: return Color(0.45, 0.28, 0.10)   # CHEST
		9: return Color(0.20, 0.20, 0.22)   # COBBLESTONE
		10: return Color(0.70, 0.65, 0.48)  # SAND
		11: return Color(0.18, 0.35, 0.65, 0.45) # WATER
		12: return Color(0.80, 0.82, 0.88)  # SNOW
		13: return Color(0.40, 0.18, 0.10)  # BRICK
		_: return Color(0.6, 0.6, 0.6)