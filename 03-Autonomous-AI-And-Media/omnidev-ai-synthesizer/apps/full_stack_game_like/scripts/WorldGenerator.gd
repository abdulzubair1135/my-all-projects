extends Node3D

@export var world_size: int = 32
@export var chunk_height: int = 16
var noise = FastNoiseLite.new()

func _ready():
    noise.seed = randi()
    noise.frequency = 0.04
    generate_terrain()

func generate_terrain():
    for x in range(-world_size / 2, world_size / 2):
        for z in range(-world_size / 2, world_size / 2):
            var h = int(abs(noise.get_noise_2d(x, z)) * 12) + 2
            for y in range(h):
                create_voxel(Vector3(x, y, z), "grass" if y == h-1 else "dirt")

func create_voxel(pos: Vector3, block_type: String):
    var mesh_instance = MeshInstance3D.new()
    var box = BoxMesh.new()
    box.size = Vector3(1, 1, 1)
    mesh_instance.mesh = box
    mesh_instance.position = pos
    
    var col_body = StaticBody3D.new()
    var col_shape = CollisionShape3D.new()
    var shape = BoxShape3D.new()
    shape.size = Vector3(1, 1, 1)
    col_shape.shape = shape
    col_body.add_child(col_shape)
    mesh_instance.add_child(col_body)
    
    var mat = StandardMaterial3D.new()
    if block_type == "grass": mat.albedo_color = Color(0.2, 0.7, 0.3)
    elif block_type == "dirt": mat.albedo_color = Color(0.45, 0.28, 0.15)
    elif block_type == "stone": mat.albedo_color = Color(0.5, 0.5, 0.55)
    mesh_instance.material_override = mat
    add_child(mesh_instance)

func break_voxel(hit_pos: Vector3):
    var grid_pos = (hit_pos + Vector3(0.5, 0.5, 0.5)).floor()
    for child in get_children():
        if child is MeshInstance3D and child.position.distance_to(grid_pos) < 0.8:
            child.queue_free()
            return

func place_voxel(hit_pos: Vector3, block_id: int):
    var grid_pos = (hit_pos + Vector3(0.5, 0.5, 0.5)).floor()
    create_voxel(grid_pos, "stone" if block_id == 2 else "grass")
