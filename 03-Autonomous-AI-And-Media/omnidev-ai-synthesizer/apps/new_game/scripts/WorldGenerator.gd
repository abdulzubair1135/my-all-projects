class_name WorldGenerator
extends Node3D

@export var world_size: int = 32
@export var chunk_height: int = 16
var noise = FastNoiseLite.new()
var tree_noise = FastNoiseLite.new()
var block_meshes: Dictionary = {}

func _ready():
    noise.seed = randi()
    noise.frequency = 0.04
    tree_noise.seed = randi()
    tree_noise.frequency = 0.02
    generate_terrain()

func generate_terrain():
    for x in range(-world_size / 2, world_size / 2):
        for z in range(-world_size / 2, world_size / 2):
            var h = int(abs(noise.get_noise_2d(x, z)) * 12) + 2
            for y in range(h):
                var block_type = "grass" if y == h-1 else "dirt"
                if y == 0:
                    block_type = "stone"
                elif y == h-1 and h < 4:
                    block_type = "sand"
                create_voxel(Vector3(x, y, z), block_type)
            # Place trees
            if h > 4 and tree_noise.get_noise_2d(x, z) > 0.5:
                place_tree(Vector3(x, h, z))

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
    mat.roughness = 0.9
    mat.metallic = 0.0
    match block_type:
        "grass":
            mat.albedo_color = Color(0.12, 0.35, 0.08)
        "dirt":
            mat.albedo_color = Color(0.25, 0.15, 0.08)
        "stone":
            mat.albedo_color = Color(0.35, 0.35, 0.40)
        "sand":
            mat.albedo_color = Color(0.70, 0.65, 0.50)
        "water":
            mat.albedo_color = Color(0.05, 0.15, 0.40, 0.6)
            mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
        "wood":
            mat.albedo_color = Color(0.25, 0.12, 0.04)
        "leaves":
            mat.albedo_color = Color(0.02, 0.20, 0.02, 0.8)
            mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
        _:
            mat.albedo_color = Color(0.5, 0.5, 0.5)
    mesh_instance.material_override = mat
    add_child(mesh_instance)
    block_meshes[pos] = mesh_instance

func place_tree(base_pos: Vector3):
    var trunk_height = randi_range(4, 6)
    for y in range(trunk_height):
        create_voxel(Vector3(base_pos.x, base_pos.y + y, base_pos.z), "wood")
    var leaf_start = base_pos.y + trunk_height - 2
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            for dy in range(leaf_start, base_pos.y + trunk_height + 1):
                if abs(dx) == 2 and abs(dz) == 2 and dy == leaf_start + 1:
                    continue
                if abs(dx) + abs(dz) > 3:
                    continue
                var pos = Vector3(base_pos.x + dx, dy, base_pos.z + dz)
                if not block_meshes.has(pos):
                    create_voxel(pos, "leaves")

func break_voxel(hit_pos: Vector3):
    var grid_pos = (hit_pos + Vector3(0.5, 0.5, 0.5)).floor()
    var key = grid_pos
    if block_meshes.has(key):
        block_meshes[key].queue_free()
        block_meshes.erase(key)

func place_voxel(hit_pos: Vector3, block_id: int):
    var grid_pos = (hit_pos + Vector3(0.5, 0.5, 0.5)).floor()
    var type_map = {
        1: "grass",
        2: "dirt",
        3: "stone",
        4: "wood",
        5: "leaves",
        6: "sand",
        7: "water"
    }
    var block_type = type_map.get(block_id, "grass")
    if not block_meshes.has(grid_pos):
        create_voxel(grid_pos, block_type)

func get_block_type(pos: Vector3) -> String:
    var key = pos.floor()
    if block_meshes.has(key):
        var mesh = block_meshes[key]
        if mesh and mesh.material_override:
            var col = mesh.material_override.albedo_color
            if col == Color(0.12, 0.35, 0.08): return "grass"
            if col == Color(0.25, 0.15, 0.08): return "dirt"
            if col == Color(0.35, 0.35, 0.40): return "stone"
            if col == Color(0.70, 0.65, 0.50): return "sand"
            if col == Color(0.05, 0.15, 0.40, 0.6): return "water"
            if col == Color(0.25, 0.12, 0.04): return "wood"
            if col == Color(0.02, 0.20, 0.02, 0.8): return "leaves"
    return ""

# Auto-build shelter (B key)
func auto_build_shelter(center: Vector3):
    var bx = center.x
    var by = center.y
    var bz = center.z
    for x in range(bx - 3, bx + 4):
        for z in range(bz - 3, bz + 4):
            var floor_pos = Vector3(x, by - 1, z)
            if not block_meshes.has(floor_pos):
                create_voxel(floor_pos, "stone")
            if x == bx - 3 or x == bx + 3 or z == bz - 3 or z == bz + 3:
                for y in range(by, by + 3):
                    var wall_pos = Vector3(x, y, z)
                    if not block_meshes.has(wall_pos):
                        create_voxel(wall_pos, "stone")
            # Roof
            var roof_pos = Vector3(x, by + 3, z)
            if not block_meshes.has(roof_pos):
                create_voxel(roof_pos, "stone")
    # Door
    var door_pos = Vector3(bx, by, bz - 3)
    if block_meshes.has(door_pos):
        block_meshes[door_pos].queue_free()
        block_meshes.erase(door_pos)
    var door_pos2 = Vector3(bx, by + 1, bz - 3)
    if block_meshes.has(door_pos2):
        block_meshes[door_pos2].queue_free()
        block_meshes.erase(door_pos2)

# Plant tree (T key)
func plant_tree(pos: Vector3):
    var floor_pos = pos.floor()
    var h = 1
    while block_meshes.has(Vector3(floor_pos.x, floor_pos.y + h, floor_pos.z)):
        h += 1
    place_tree(Vector3(floor_pos.x, floor_pos.y + h, floor_pos.z))