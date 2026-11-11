class_name WorldGenerator
extends Node3D

const CHUNK_SIZE = 16
const WORLD_HEIGHT = 40
const BLOCK_SIZE = 1.0

enum BlockType {
	EMPTY = 0,
	DIRT = 1,
	GRASS = 2,
	STONE = 3,
	WOOD = 4,
	LEAVES = 5,
	PLANK = 6,
	GLASS = 7,
	CHEST = 8,
	COBBLESTONE = 9,
	SAND = 10,
	WATER = 11,
	SNOW = 12,
	BRICK = 13
}

var noise = FastNoiseLite.new()
var detail_noise = FastNoiseLite.new()
var height_noise = FastNoiseLite.new()
var chunk_data = {}
var mesh_instances = {}
var block_meshes = {}

# Animal spawning
var animal_scene: PackedScene
var animals = []
var max_animals: int = 80

# Day / Night Cycle & Sun
var sun_pivot: Node3D
var sun_light: DirectionalLight3D
var day_time: float = 0.25
var day_speed: float = 0.006

# Chunk terrain material
var terrain_material: ShaderMaterial
var texture_atlas: Texture2D

# Tree spawn tracking
var tree_positions: Array = []

# World seed
var world_seed: int = 0

# Texture atlas
const ATLAS_TILE_SIZE = 16
const ATLAS_GRID = 4
var tile_rects = {}

# Chest inventory storage: key = position string -> Array of 27 slots (each {block: int, count: int})
var chest_inventories: Dictionary = {}

func _ready():
	world_seed = randi()
	
	noise.noise_type = FastNoiseLite.TYPE_PERLIN
	noise.frequency = 0.012
	noise.fractal_type = FastNoiseLite.FRACTAL_FBM
	noise.fractal_octaves = 6
	noise.fractal_lacunarity = 2.1
	noise.fractal_gain = 0.52
	noise.seed = world_seed

	detail_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	detail_noise.frequency = 0.035
	detail_noise.seed = world_seed + 1000

	height_noise.noise_type = FastNoiseLite.TYPE_PERLIN
	height_noise.frequency = 0.008
	height_noise.seed = world_seed + 2000

	generate_texture_atlas()
	setup_terrain_material()

	setup_sun_and_environment()

	animal_scene = load("res://scenes/Animal.tscn") if ResourceLoader.exists("res://scenes/Animal.tscn") else null

	generate_initial_chunks(Vector3.ZERO)
	spawn_initial_animals()

func _process(delta: float):
	update_day_night_cycle(delta)

func setup_sun_and_environment():
	sun_pivot = Node3D.new()
	sun_pivot.name = "SunPivot"
	add_child(sun_pivot)

	sun_light = DirectionalLight3D.new()
	sun_light.name = "SunLight"
	sun_light.shadow_enabled = true
	sun_light.shadow_bias = 0.1
	sun_light.shadow_normal_bias = 0.05
	sun_light.shadow_max_distance = 50.0
	sun_light.light_energy = 0.7
	sun_light.light_color = Color(1.0, 0.95, 0.85)
	sun_pivot.add_child(sun_light)

	var sun_mesh_inst = MeshInstance3D.new()
	var s_sphere = SphereMesh.new()
	s_sphere.radius = 10.0
	s_sphere.height = 20.0
	sun_mesh_inst.mesh = s_sphere
	var s_mat = StandardMaterial3D.new()
	s_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	s_mat.albedo_color = Color(1.0, 0.9, 0.4)
	sun_mesh_inst.material_override = s_mat
	sun_mesh_inst.position = Vector3(0, 0, -220)
	sun_pivot.add_child(sun_mesh_inst)

	var moon_mesh_inst = MeshInstance3D.new()
	var m_sphere = SphereMesh.new()
	m_sphere.radius = 8.0
	m_sphere.height = 16.0
	moon_mesh_inst.mesh = m_sphere
	var m_mat = StandardMaterial3D.new()
	m_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m_mat.albedo_color = Color(0.85, 0.85, 0.95)
	moon_mesh_inst.material_override = m_mat
	moon_mesh_inst.position = Vector3(0, 0, 220)
	sun_pivot.add_child(moon_mesh_inst)

func update_day_night_cycle(delta: float):
	if !sun_pivot or !sun_light:
		return
	day_time += delta * day_speed
	if day_time >= 1.0:
		day_time = 0.0

	var angle = day_time * TAU
	sun_pivot.rotation.x = angle
	sun_pivot.rotation.y = deg_to_rad(25.0)

	var height = sin(angle)
	if height > 0.15:
		sun_light.light_energy = clamp(height * 0.85, 0.3, 0.85)
		sun_light.light_color = Color(1.0, 0.95, 0.85)
	elif height > -0.15:
		sun_light.light_energy = 0.3
		sun_light.light_color = Color(1.0, 0.6, 0.3)
	else:
		sun_light.light_energy = 0.06
		sun_light.light_color = Color(0.3, 0.4, 0.7)

func generate_texture_atlas():
	var img = Image.create(ATLAS_GRID * ATLAS_TILE_SIZE, ATLAS_GRID * ATLAS_TILE_SIZE, false, Image.FORMAT_RGBA8)
	img.fill(Color(0,0,0,0))
	
	var tile_data = {
		0: {"base": Color(0.4, 0.28, 0.15), "pattern": "checker"},
		1: {"base": Color(0.18, 0.5, 0.12), "pattern": "grass"},
		2: {"base": Color(0.42, 0.42, 0.45), "pattern": "stone"},
		3: {"base": Color(0.6, 0.5, 0.32), "pattern": "wood_top"},
		4: {"base": Color(0.32, 0.18, 0.08), "pattern": "wood_side"},
		5: {"base": Color(0.08, 0.38, 0.08), "pattern": "leaves"},
		6: {"base": Color(0.65, 0.55, 0.35), "pattern": "plank"},
		7: {"base": Color(0.65, 0.8, 0.9, 0.9), "pattern": "glass"},
		8: {"base": Color(0.45, 0.28, 0.10), "pattern": "chest"},
		9: {"base": Color(0.28, 0.28, 0.3), "pattern": "cobblestone"},
		10: {"base": Color(0.8, 0.75, 0.55), "pattern": "sand"},
		11: {"base": Color(0.18, 0.35, 0.65, 0.7), "pattern": "water"},
		12: {"base": Color(0.92, 0.95, 0.98), "pattern": "snow"},
		13: {"base": Color(0.5, 0.25, 0.15), "pattern": "brick"}
	}
	
	var tile_index = 0
	for block_type in range(1, 14):
		var base_color = tile_data.get(block_type, {"base": Color(0.5,0.5,0.5)})["base"]
		var pattern = tile_data.get(block_type, {"pattern": "none"})["pattern"]
		if block_type == BlockType.WOOD:
			draw_tile(img, tile_index, base_color, "wood_top")
			tile_rects[(block_type, Vector3.UP)] = get_tile_rect(tile_index)
			tile_rects[(block_type, Vector3.DOWN)] = get_tile_rect(tile_index)
			tile_index += 1
			draw_tile(img, tile_index, Color(0.32, 0.18, 0.08), "wood_side")
			tile_rects[(block_type, Vector3.RIGHT)] = get_tile_rect(tile_index)
			tile_rects[(block_type, Vector3.LEFT)] = get_tile_rect(tile_index)
			tile_rects[(block_type, Vector3.FORWARD)] = get_tile_rect(tile_index)
			tile_rects[(block_type, Vector3.BACK)] = get_tile_rect(tile_index)
		else:
			draw_tile(img, tile_index, base_color, pattern)
			for norm in [Vector3.UP, Vector3.DOWN, Vector3.RIGHT, Vector3.LEFT, Vector3.FORWARD, Vector3.BACK]:
				tile_rects[(block_type, norm)] = get_tile_rect(tile_index)
			tile_index += 1
	
	texture_atlas = ImageTexture.create_from_image(img)
	texture_atlas.mag_filter = Texture.MAG_FILTER_NEAREST
	texture_atlas.min_filter = Texture.MIN_FILTER_NEAREST

func draw_tile(image: Image, tile_index: int, base_color: Color, pattern: String):
	var tile_x = (tile_index % ATLAS_GRID) * ATLAS_TILE_SIZE
	var tile_y = (tile_index / ATLAS_GRID) * ATLAS_TILE_SIZE
	for x in range(ATLAS_TILE_SIZE):
		for y in range(ATLAS_TILE_SIZE):
			var px = tile_x + x
			var py = tile_y + y
			var col = base_color
			match pattern:
				"checker":
					if (x/4 + y/4) % 2 == 0:
						col = base_color * 0.8
				"grass":
					if y > 10:
						col = Color(0.3, 0.6, 0.15)
					elif y > 8:
						col = Color(0.2, 0.5, 0.1)
					else:
						col = Color(0.4, 0.28, 0.15)
				"stone":
					if (x % 4 == 0 or y % 4 == 0):
						col = base_color * 0.7
				"wood_top":
					if (x % 3 == 0 or y % 3 == 0):
						col = base_color * 0.7
				"wood_side":
					if y % 4 == 0:
						col = base_color * 0.6
				"leaves":
					if (x + y) % 3 == 0:
						col = Color(0.02, 0.25, 0.02)
				"plank":
					if (x % 4 == 0 or y % 4 == 0):
						col = base_color * 0.7
				"glass":
					col.a = 0.6
				"chest":
					if (x > 4 and x < 12 and y > 4 and y < 8):
						col = Color(0.6, 0.4, 0.15)
				"cobblestone":
					if (x % 3 == 0 and y % 3 == 0):
						col = base_color * 0.6
				"sand":
					if (x % 5 == 0 or y % 5 == 0):
						col = base_color * 0.8
				"water":
					col = Color(0.1, 0.3, 0.6, 0.5)
				"snow":
					if (x % 4 == 0 or y % 4 == 0):
						col = Color(0.95, 0.97, 1.0)
				"brick":
					if (x % 8 < 2 or y % 8 < 2):
						col = Color(0.35, 0.15, 0.08)
				_:
					pass
			image.set_pixel(px, py, col)

func get_tile_rect(index: int) -> Rect2:
	var tx = (index % ATLAS_GRID) * ATLAS_TILE_SIZE
	var ty = (index / ATLAS_GRID) * ATLAS_TILE_SIZE
	var tex_size = ATLAS_GRID * ATLAS_TILE_SIZE
	return Rect2(Vector2(tx, ty) / tex_size, Vector2(ATLAS_TILE_SIZE, ATLAS_TILE_SIZE) / tex_size)

func setup_terrain_material():
	var shader_code = """
	shader_type spatial;
	render_mode blend_mix, diffuse_lambert, specular_disabled;
	uniform sampler2D texture_atlas : source_color;
	void fragment() {
		vec4 tex = texture(texture_atlas, UV);
		vec4 col = tex * COLOR;
		ALBEDO = col.rgb;
		ALPHA = col.a;
	}
	"""
	var shader = Shader.new()
	shader.code = shader_code
	terrain_material = ShaderMaterial.new()
	terrain_material.shader = shader
	terrain_material.set_shader_parameter("texture_atlas", texture_atlas)

func generate_initial_chunks(player_pos: Vector3):
	var chunk_x = int(floor(player_pos.x / CHUNK_SIZE))
	var chunk_z = int(floor(player_pos.z / CHUNK_SIZE))

	for x in range(-6, 7):
		for z in range(-6, 7):
			generate_chunk(chunk_x + x, chunk_z + z)

func generate_chunk(cx: int, cz: int):
	var key = str(cx) + "," + str(cz)
	if chunk_data.has(key):
		return

	var blocks = {}

	for x in range(CHUNK_SIZE):
		for z in range(CHUNK_SIZE):
			var world_x = cx * CHUNK_SIZE + x
			var world_z = cz * CHUNK_SIZE + z

			var height = get_terrain_height(world_x, world_z)

			for y in range(WORLD_HEIGHT):
				if y <= height:
					var block_type = BlockType.DIRT
					if y == 0:
						block_type = BlockType.COBBLESTONE
					elif y == height:
						if height > 28:
							block_type = BlockType.SNOW
						elif height > 24:
							block_type = BlockType.STONE
						elif height > 16:
							block_type = BlockType.GRASS
						elif height > 10:
							block_type = BlockType.GRASS
						else:
							block_type = BlockType.SAND
					elif y >= height - 3:
						block_type = BlockType.DIRT
					else:
						block_type = BlockType.STONE

					var pos = Vector3(world_x, y, world_z)
					blocks[pos] = block_type

	generate_trees(cx, cz, blocks)

	# Surface chests
	if randf() < 0.05:
		var cx_pos = cx * CHUNK_SIZE + randi_range(3, CHUNK_SIZE - 4)
		var cz_pos = cz * CHUNK_SIZE + randi_range(3, CHUNK_SIZE - 4)
		var cy_pos = get_terrain_height(cx_pos, cz_pos) + 1
		if cy_pos > 3 and cy_pos < WORLD_HEIGHT - 2:
			var chest_pos = Vector3(cx_pos, cy_pos, cz_pos)
			blocks[chest_pos] = BlockType.CHEST
			# Initialize chest inventory with some random items
			var inv = []
			for i in range(27):
				inv.append({"block": 0, "count": 0})
			# Add some random items
			for i in range(randi_range(1, 5)):
				var slot = randi_range(0, 26)
				var btype = randi_range(1, 6)
				inv[slot] = {"block": btype, "count": randi_range(1, 10)}
			chest_inventories[vec3_to_key(chest_pos)] = inv

	chunk_data[key] = blocks
	rebuild_chunk(key)

func vec3_to_key(v: Vector3) -> String:
	return str(floor(v.x)) + "," + str(floor(v.y)) + "," + str(floor(v.z))

func get_terrain_height(x: int, z: int) -> int:
	var base_h = noise.get_noise_2d(x, z) * 12.0 + 15.0
	var detail_h = detail_noise.get_noise_2d(x, z) * 3.5
	var height_var = height_noise.get_noise_2d(x * 0.5, z * 0.5) * 2.0
	var final_h = clamp(round(base_h + detail_h + height_var), 2.0, WORLD_HEIGHT - 10)
	return int(final_h)

func generate_trees(cx: int, cz: int, blocks: Dictionary):
	var tree_count = randi_range(5, 12)
	var placed = 0
	var attempts = 0

	while placed < tree_count and attempts < 250:
		attempts += 1
		var local_x = randi_range(2, CHUNK_SIZE - 3)
		var local_z = randi_range(2, CHUNK_SIZE - 3)
		var world_x = cx * CHUNK_SIZE + local_x
		var world_z = cz * CHUNK_SIZE + local_z
		var height = get_terrain_height(world_x, world_z)

		var surface_block = blocks.get(Vector3(world_x, height, world_z), BlockType.EMPTY)
		if (surface_block == BlockType.GRASS or surface_block == BlockType.DIRT) and height > 4 and height < WORLD_HEIGHT - 12:
			var pos = Vector3(world_x, 0, world_z)
			var too_close = false
			for tree_pos in tree_positions:
				if tree_pos.distance_to(pos) < 4.0:
					too_close = true
					break
			if !too_close:
				plant_tree_at(Vector3(world_x, height + 1, world_z), blocks)
				tree_positions.append(pos)
				placed += 1

func plant_tree_at(base_pos: Vector3, blocks: Dictionary):
	var bx = int(base_pos.x)
	var by = int(base_pos.y)
	var bz = int(base_pos.z)
	
	var tree_height = randi_range(5, 9)

	for y in range(by, by + tree_height):
		blocks[Vector3(bx, y, bz)] = BlockType.WOOD

	var leaf_start = by + tree_height - 4
	for dx in range(-3, 4):
		for dz in range(-3, 4):
			for dy in range(leaf_start, by + tree_height + 2):
				var dist = abs(dx) + abs(dz)
				var height_offset = dy - (by + tree_height)
				
				if dist == 0 and height_offset >= -1:
					continue
				if dist > 2 and height_offset > -2:
					continue
				if dist > 1 and height_offset > 0:
					continue
				if abs(dx) == 3 and abs(dz) == 3:
					continue
					
				var pos = Vector3(bx + dx, dy, bz + dz)
				if !blocks.has(pos):
					blocks[pos] = BlockType.LEAVES

func get_face_color(block_type: int, normal: Vector3) -> Color:
	match block_type:
		BlockType.GRASS:
			if normal == Vector3.UP:
				return Color(0.18, 0.5, 0.12)
			elif normal == Vector3.DOWN:
				return Color(0.4, 0.28, 0.15)
			else:
				return Color(0.32, 0.42, 0.16)
		BlockType.DIRT:
			return Color(0.4, 0.28, 0.15)
		BlockType.STONE:
			return Color(0.42, 0.42, 0.45)
		BlockType.WOOD:
			if normal == Vector3.UP or normal == Vector3.DOWN:
				return Color(0.6, 0.5, 0.32)
			else:
				return Color(0.32, 0.18, 0.08)
		BlockType.LEAVES:
			return Color(0.08, 0.38, 0.08)
		BlockType.PLANK:
			return Color(0.65, 0.55, 0.35)
		BlockType.GLASS:
			return Color(0.65, 0.8, 0.9, 0.5)
		BlockType.CHEST:
			if normal == Vector3.UP or normal == Vector3.DOWN:
				return Color(0.5, 0.32, 0.12)
			else:
				return Color(0.55, 0.38, 0.15)
		BlockType.COBBLESTONE:
			return Color(0.28, 0.28, 0.3)
		BlockType.SAND:
			return Color(0.8, 0.75, 0.55)
		BlockType.SNOW:
			return Color(0.92, 0.95, 0.98)
		BlockType.BRICK:
			return Color(0.5, 0.25, 0.15)
		_:
			return Color(0.7, 0.7, 0.7)

func get_uv_for_face(block_type: int, normal: Vector3, vertex_index: int) -> Vector2:
	var rect = tile_rects.get((block_type, normal))
	if rect == null:
		rect = Rect2(0,0,1,1)
	var corners = [Vector2(0,0), Vector2(1,0), Vector2(1,1), Vector2(0,1)]
	var corner = corners[vertex_index % 4]
	return rect.position + corner * rect.size

func build_mesh_from_blocks(blocks: Dictionary) -> ArrayMesh:
	var vertices = []
	var normals = []
	var colors = []
	var uvs = []
	var indices = []

	for pos in blocks:
		var block_type = blocks[pos]
		if block_type == BlockType.EMPTY:
			continue

		var faces = [
			{"dir": Vector3.RIGHT, "normal": Vector3.RIGHT, "verts": get_face_vertices(pos, "right")},
			{"dir": Vector3.LEFT, "normal": Vector3.LEFT, "verts": get_face_vertices(pos, "left")},
			{"dir": Vector3.UP, "normal": Vector3.UP, "verts": get_face_vertices(pos, "up")},
			{"dir": Vector3.DOWN, "normal": Vector3.DOWN, "verts": get_face_vertices(pos, "down")},
			{"dir": Vector3.FORWARD, "normal": Vector3.FORWARD, "verts": get_face_vertices(pos, "forward")},
			{"dir": Vector3.BACK, "normal": Vector3.BACK, "verts": get_face_vertices(pos, "back")}
		]

		for face in faces:
			var neighbor_pos = pos + face.dir
			var neighbor = blocks.get(neighbor_pos, BlockType.EMPTY)

			if neighbor == BlockType.EMPTY or (neighbor == BlockType.GLASS and block_type != BlockType.GLASS):
				var start_idx = vertices.size()
				var face_verts = face.verts
				var normal = face.normal
				var base_col = get_face_color(block_type, normal)

				var shade_factor = 1.0
				if normal == Vector3.UP:
					shade_factor = 1.08
				elif normal == Vector3.DOWN:
					shade_factor = 0.55
				elif abs(normal.x) > 0.5:
					shade_factor = 0.82
				else:
					shade_factor = 0.88

				var face_col = Color(
					clamp(shade_factor, 0.0, 1.0),
					clamp(shade_factor, 0.0, 1.0),
					clamp(shade_factor, 0.0, 1.0),
					1.0
				)

				for v_idx in range(face_verts.size()):
					var v = face_verts[v_idx]
					vertices.append(Vector3(v.x, v.y, v.z))
					normals.append(normal)
					colors.append(face_col)
					var uv = get_uv_for_face(block_type, normal, v_idx)
					uvs.append(uv)

				indices.append(start_idx)
				indices.append(start_idx + 1)
				indices.append(start_idx + 2)
				indices.append(start_idx)
				indices.append(start_idx + 2)
				indices.append(start_idx + 3)

	var array_mesh = ArrayMesh.new()
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = PackedVector3Array(vertices)
	arrays[Mesh.ARRAY_NORMAL] = PackedVector3Array(normals)
	arrays[Mesh.ARRAY_COLOR] = PackedColorArray(colors)
	arrays[Mesh.ARRAY_TEX_UV] = PackedVector2Array(uvs)
	arrays[Mesh.ARRAY_INDEX] = PackedInt32Array(indices)

	array_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return array_mesh

func get_face_vertices(pos: Vector3, face: String) -> Array:
	var x = pos.x
	var y = pos.y
	var z = pos.z

	match face:
		"right":
			return [Vector3(x+1, y, z), Vector3(x+1, y+1, z), Vector3(x+1, y+1, z+1), Vector3(x+1, y, z+1)]
		"left":
			return [Vector3(x, y, z+1), Vector3(x, y+1, z+1), Vector3(x, y+1, z), Vector3(x, y, z)]
		"up":
			return [Vector3(x, y+1, z+1), Vector3(x+1, y+1, z+1), Vector3(x+1, y+1, z), Vector3(x, y+1, z)]
		"down":
			return [Vector3(x, y, z), Vector3(x+1, y, z), Vector3(x+1, y, z+1), Vector3(x, y, z+1)]
		"forward":
			return [Vector3(x, y, z+1), Vector3(x+1, y+1, z+1), Vector3(x+1, y+1, z), Vector3(x, y, z)]
		"back":
			return [Vector3(x+1, y, z), Vector3(x+1, y+1, z), Vector3(x, y+1, z), Vector3(x, y, z)]
	return []

func get_block(pos: Vector3) -> int:
	var key = str(int(floor(pos.x / CHUNK_SIZE))) + "," + str(int(floor(pos.z / CHUNK_SIZE)))
	if chunk_data.has(key):
		var local_pos = Vector3(floor(pos.x), floor(pos.y), floor(pos.z))
		return chunk_data[key].get(local_pos, BlockType.EMPTY)
	return BlockType.EMPTY

func set_block(pos: Vector3, block_type: int, spawn_drop: bool = true):
	var key = str(int(floor(pos.x / CHUNK_SIZE))) + "," + str(int(floor(pos.z / CHUNK_SIZE)))
	if chunk_data.has(key):
		var local_pos = Vector3(floor(pos.x), floor(pos.y), floor(pos.z))
		var old_type = chunk_data[key].get(local_pos, BlockType.EMPTY)
		
		# If removing a block, spawn drop and handle chest inventory
		if block_type == BlockType.EMPTY and old_type != BlockType.EMPTY and spawn_drop:
			# Drop the block item
			spawn_drop_item(pos, old_type, 1)
			# If it was a chest, drop its contents too
			if old_type == BlockType.CHEST:
				var chest_key = vec3_to_key(local_pos)
				if chest_inventories.has(chest_key):
					var inv = chest_inventories[chest_key]
					for slot in inv:
						if slot["block"] != 0 and slot["count"] > 0:
							spawn_drop_item(pos, slot["block"], slot["count"])
					chest_inventories.erase(chest_key)
		
		# If placing a chest, initialize its inventory
		if block_type == BlockType.CHEST:
			var chest_key = vec3_to_key(local_pos)
			if !chest_inventories.has(chest_key):
				var inv = []
				for i in range(27):
					inv.append({"block": 0, "count": 0})
				chest_inventories[chest_key] = inv
		
		chunk_data[key][local_pos] = block_type
		rebuild_chunk(key)

func spawn_drop_item(pos: Vector3, block_type: int, count: int):
	var drop = DroppedItem.new()
	drop.block_type = block_type
	drop.count = count
	drop.position = pos + Vector3(0.5, 0.5, 0.5)  # center of block
	add_child(drop)

func get_chest_inventory(pos: Vector3) -> Array:
	var key = vec3_to_key(pos)
	if chest_inventories.has(key):
		return chest_inventories[key]
	return []

func set_chest_inventory(pos: Vector3, inv: Array):
	var key = vec3_to_key(pos)
	chest_inventories[key] = inv

func rebuild_chunk(chunk_key: String):
	if mesh_instances.has(chunk_key):
		mesh_instances[chunk_key].queue_free()
		mesh_instances.erase(chunk_key)

	var mesh = build_mesh_from_blocks(chunk_data[chunk_key])

	var static_body = StaticBody3D.new()
	static_body.name = "ChunkBody_" + chunk_key

	var mesh_instance = MeshInstance3D.new()
	mesh_instance.mesh = mesh
	mesh_instance.material_override = terrain_material
	static_body.add_child(mesh_instance)

	var collision_shape = CollisionShape3D.new()
	var shape = mesh.create_trimesh_shape()
	if shape:
		collision_shape.shape = shape
		static_body.add_child(collision_shape)

	add_child(static_body)
	mesh_instances[chunk_key] = static_body

func auto_build_shelter(center_pos: Vector3):
	var bx = int(floor(center_pos.x))
	var by = int(floor(center_pos.y))
	var bz = int(floor(center_pos.z))

	for x in range(bx - 4, bx + 5):
		for z in range(bz - 4, bz + 5):
			set_block(Vector3(x, by - 1, z), BlockType.COBBLESTONE, false)
			set_block(Vector3(x, by + 4, z), BlockType.BRICK, false)

			if x == bx - 4 or x == bx + 4 or z == bz - 4 or z == bz + 4:
				for y in range(by, by + 4):
					if x == bx and z == bz - 4 and (y == by or y == by + 1):
						set_block(Vector3(x, y, z), BlockType.EMPTY, false)
					elif (x == bx or z == bz) and y == by + 2:
						set_block(Vector3(x, y, z), BlockType.GLASS, false)
					else:
						set_block(Vector3(x, y, z), BlockType.BRICK, false)

	set_block(Vector3(bx + 3, by, bz + 3), BlockType.CHEST, false)
	set_block(Vector3(bx - 3, by, bz - 3), BlockType.CHEST, false)

func auto_build_tree(pos: Vector3):
	var key = str(int(floor(pos.x / CHUNK_SIZE))) + "," + str(int(floor(pos.z / CHUNK_SIZE)))
	if chunk_data.has(key):
		plant_tree_at(pos, chunk_data[key])
		rebuild_chunk(key)

func spawn_initial_animals():
	if animal_scene == null:
		return

	var spawn_count = randi_range(12, 25)
	var attempts = 0

	while animals.size() < spawn_count and attempts < 500:
		attempts += 1
		var x = randf_range(-150, 150)
		var z = randf_range(-150, 150)
		var height = get_terrain_height(int(x), int(z))
		var y = float(height) + 1.0

		if y > 3 and y < WORLD_HEIGHT - 3:
			var animal = animal_scene.instantiate()
			animal.position = Vector3(x, y, z)
			var type_choice = randi() % 3
			match type_choice:
				0:
					animal.animal_type = Animal.AnimalType.COW
				1:
					animal.animal_type = Animal.AnimalType.SHEEP
				2:
					animal.animal_type = Animal.AnimalType.PIG
			add_child(animal)
			animals.append(animal)

func spawn_animals_in_chunk(cx: int, cz: int):
	if animal_scene == null:
		return

	if animals.size() >= max_animals:
		return

	var spawn_count = randi_range(1, 4)
	var attempts = 0

	for i in range(spawn_count):
		var local_x = randi_range(2, CHUNK_SIZE - 3)
		var local_z = randi_range(2, CHUNK_SIZE - 3)
		var world_x = cx * CHUNK_SIZE + local_x
		var world_z = cz * CHUNK_SIZE + local_z
		var height = get_terrain_height(world_x, world_z)
		var y = float(height) + 1.0

		if y > 3 and y < WORLD_HEIGHT - 3:
			var animal = animal_scene.instantiate()
			animal.position = Vector3(world_x, y, world_z)
			var type_choice = randi() % 3
			match type_choice:
				0:
					animal.animal_type = Animal.AnimalType.COW
				1:
					animal.animal_type = Animal.AnimalType.SHEEP
				2:
					animal.animal_type = Animal.AnimalType.PIG
			add_child(animal)
			animals.append(animal)
			break
		attempts += 1
		if attempts > 20:
			break

func update_player_position(player_pos: Vector3):
	var chunk_x = int(floor(player_pos.x / CHUNK_SIZE))
	var chunk_z = int(floor(player_pos.z / CHUNK_SIZE))

	for x in range(-6, 7):
		for z in range(-6, 7):
			var key = str(chunk_x + x) + "," + str(chunk_z + z)
			if !chunk_data.has(key):
				generate_chunk(chunk_x + x, chunk_z + z)
				spawn_animals_in_chunk(chunk_x + x, chunk_z + z)

	clear_distant_chunks(player_pos)

func clear_distant_chunks(player_pos: Vector3):
	var chunk_x = int(floor(player_pos.x / CHUNK_SIZE))
	var chunk_z = int(floor(player_pos.z / CHUNK_SIZE))

	var to_remove = []
	for key in chunk_data:
		var parts = key.split(",")
		var cx = int(parts[0])
		var cz = int(parts[1])

		if abs(cx - chunk_x) > 8 or abs(cz - chunk_z) > 8:
			to_remove.append(key)

	for key in to_remove:
		if mesh_instances.has(key):
			mesh_instances[key].queue_free()
			mesh_instances.erase(key)
		chunk_data.erase(key)

		var animals_to_remove = []
		for animal in animals:
			if is_instance_valid(animal):
				var animal_chunk_x = int(floor(animal.position.x / CHUNK_SIZE))
				var animal_chunk_z = int(floor(animal.position.z / CHUNK_SIZE))
				if str(animal_chunk_x) + "," + str(animal_chunk_z) == key:
					animal.queue_free()
					animals_to_remove.append(animal)
		for animal in animals_to_remove:
			animals.erase(animal)

func get_world_seed() -> int:
	return world_seed