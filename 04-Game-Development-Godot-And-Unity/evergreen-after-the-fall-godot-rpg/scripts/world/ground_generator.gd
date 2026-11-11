extends RefCounted
class_name GroundGenerator

# Evergreen: After the Fall - Universal Procedural Region Ground Generator
# Builds rich, beautiful, zero-void 32x32 pixel ground layouts for all regions in the game.

const TILE_SIZE: int = 32
const TILES_TEX = preload("res://assets/tilesets/farm_tiles.png")

# Tile Rect2 Constants:
# Row 0:
const RECT_GRASS: Rect2       = Rect2(0, 0, 32, 32)     # Emerald Meadow Grass
const RECT_FLOWER: Rect2      = Rect2(32, 0, 32, 32)    # Meadow with Wildflowers
const RECT_SOIL_DRY: Rect2    = Rect2(64, 0, 32, 32)    # Dry Tilled Soil
const RECT_SOIL_WET: Rect2    = Rect2(96, 0, 32, 32)    # Watered Soil
const RECT_COBBLE: Rect2      = Rect2(128, 0, 32, 32)   # River Cobblestone Pavers
const RECT_DIRT_ROAD: Rect2   = Rect2(160, 0, 32, 32)   # Sandy Dirt Road / Forest Trail
const RECT_WATER: Rect2       = Rect2(192, 0, 32, 32)   # Shimmering Lake Water
const RECT_WOOD: Rect2        = Rect2(224, 0, 32, 32)   # Cedar Wood Floorboards

# Row 1:
const RECT_SAND: Rect2        = Rect2(0, 32, 32, 32)    # Shoreline Sand & Fine Gravel
const RECT_CONCRETE: Rect2    = Rect2(32, 32, 32, 32)   # Stone Plaza / Concrete Slab
const RECT_CLINIC: Rect2      = Rect2(64, 32, 32, 32)   # Clean Lab / Hospital Floor
const RECT_BALLAST: Rect2     = Rect2(96, 32, 32, 32)   # Dark Railway Ballast

static func generate_region_ground(parent: Node2D, region_id: String, width_px: int = 960, height_px: int = 540) -> Node2D:
	# Avoid duplicate ground containers
	var existing = parent.get_node_or_null("GroundVisuals")
	if existing:
		return existing
	
	var ground_container = Node2D.new()
	ground_container.name = "GroundVisuals"
	parent.add_child(ground_container)
	parent.move_child(ground_container, 0)
	
	var cols = int(ceil(float(width_px) / float(TILE_SIZE)))
	var rows = int(ceil(float(height_px) / float(TILE_SIZE)))
	
	for y in range(rows):
		for x in range(cols):
			var tile_rect = _get_tile_for_coord(region_id, x, y, cols, rows)
			var sprite = Sprite2D.new()
			sprite.texture = TILES_TEX
			sprite.region_enabled = true
			sprite.region_rect = tile_rect
			sprite.centered = false
			sprite.position = Vector2(x * TILE_SIZE, y * TILE_SIZE)
			ground_container.add_child(sprite)
	
	return ground_container

static func _get_tile_for_coord(region_id: String, x: int, y: int, cols: int, rows: int) -> Rect2:
	match region_id:
		"evergreen_village":
			# Cobblestone Plaza in center: x in [9..21], y in [5..13]
			if x >= 9 and x <= 21 and y >= 5 and y <= 13:
				return RECT_COBBLE
			# North-South main thoroughfare: x in [14..16]
			elif x >= 14 and x <= 16:
				return RECT_COBBLE
			# East-West connector: y in [8..9]
			elif y >= 8 and y <= 9:
				return RECT_COBBLE
			# Store foundations: x in [6..10], y in [4..5] or x in [19..23], y in [4..5]
			elif (x >= 6 and x <= 10 and y >= 4 and y <= 5) or (x >= 19 and x <= 23 and y >= 4 and y <= 5):
				return RECT_WOOD
			# Dirt verges around plaza
			elif (x >= 8 and x <= 22 and y >= 4 and y <= 14):
				return RECT_DIRT_ROAD
			else:
				if (x * 7 + y * 13) % 8 == 0:
					return RECT_FLOWER
				return RECT_GRASS

		"greenwood_forest":
			# Winding wilderness trail: roughly diagonal / curved path
			var trail_center = int(rows * 0.5 + sin(float(x) * 0.4) * 3.0)
			if abs(y - trail_center) <= 1:
				return RECT_DIRT_ROAD
			# North-south fork trail
			elif x >= 18 and x <= 19 and y >= 3 and y <= 14:
				return RECT_DIRT_ROAD
			else:
				if (x * 11 + y * 17) % 7 == 0:
					return RECT_FLOWER
				return RECT_GRASS

		"crystal_lake":
			# Lake water body: center-north area
			var in_water = (x >= 5 and x <= 24 and y >= 2 and y <= 10)
			if in_water:
				# Pier: x in [14..15], y in [7..11]
				if x >= 14 and x <= 15 and y >= 7 and y <= 11:
					return RECT_WOOD
				return RECT_WATER
			# Sandy shoreline strip around water
			elif (x >= 4 and x <= 25 and y >= 1 and y <= 11):
				return RECT_SAND
			# Wooden dock approach: x in [14..15], y == 12
			elif x >= 14 and x <= 15 and y == 12:
				return RECT_WOOD
			else:
				if (x * 5 + y * 11) % 9 == 0:
					return RECT_FLOWER
				return RECT_GRASS

		"abandoned_hospital":
			# Clinical tiled indoor floor
			if (x == 0 or x == cols - 1 or y == 0 or y == rows - 1):
				return RECT_CONCRETE
			elif x % 7 == 0 or y % 6 == 0:
				return RECT_WOOD
			return RECT_CLINIC

		"underground_lab":
			if (x >= 10 and x <= 19 and y >= 4 and y <= 12):
				return RECT_CLINIC
			elif (x * 3 + y * 7) % 5 == 0:
				return RECT_BALLAST
			return RECT_CONCRETE

		"old_city":
			# Paved streets and cracked urban slabs
			if (y >= 7 and y <= 9) or (x >= 13 and x <= 16):
				return RECT_COBBLE
			elif (x * 5 + y * 3) % 4 == 0:
				return RECT_DIRT_ROAD
			return RECT_CONCRETE

		"railway_station":
			# Wooden platform: y in [4..7]
			if y >= 4 and y <= 7:
				return RECT_WOOD
			# Track bed: y in [8..12]
			elif y >= 8 and y <= 12:
				return RECT_BALLAST
			else:
				if (x * 7 + y * 5) % 8 == 0:
					return RECT_FLOWER
				return RECT_GRASS

		"secret_bunker":
			# Reinforced concrete military bunker floor
			if x >= 12 and x <= 17 and y >= 5 and y <= 11:
				return RECT_CONCRETE
			elif (x + y) % 6 == 0:
				return RECT_COBBLE
			return RECT_CONCRETE

		_: # Default: emerald grass with wildflower sprigs
			if (x * 7 + y * 13) % 9 == 0:
				return RECT_FLOWER
			return RECT_GRASS
