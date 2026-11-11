extends Node2D
class_name CropPlot

# Evergreen: After the Fall - Crop Plot Component
# Handles individual soil hydration, seed planting, stage progression, and harvesting

@export var plot_id: String = "plot_0"
@export var is_tilled: bool = true
@export var is_watered: bool = false
@export var crop_id: String = ""
@export var current_stage: int = 0 # 0: Sprout, 1: Growing, 2: Mature

@onready var soil_sprite: Sprite2D = $SoilSprite
@onready var crop_sprite: Sprite2D = $CropSprite
@onready var interact_area: Area2D = $InteractArea

const TILES_TEX = preload("res://assets/tilesets/farm_tiles.png")
const CROPS_TEX = preload("res://assets/props/crops.png")

# Crop metadata dictionary
const CROP_SPECS = {
	"crop_turnip": {
		"name": "Turnip",
		"harvest_item": "produce_turnip",
		"row": 0,
		"max_stage": 2,
		"xp": 10
	},
	"crop_carrot": {
		"name": "Carrot",
		"harvest_item": "produce_carrot",
		"row": 1,
		"max_stage": 2,
		"xp": 15
	},
	"crop_potato": {
		"name": "Potato",
		"harvest_item": "produce_potato",
		"row": 2,
		"max_stage": 2,
		"xp": 20
	}
}

func _ready() -> void:
	if interact_area:
		interact_area.add_to_group("interactables")
	_update_visuals()

func get_interaction_info() -> Dictionary:
	var active = InventoryService.get_active_item()
	var prompt = "Examine Plot"
	
	if crop_id != "" and current_stage >= 2:
		var cname = CROP_SPECS[crop_id]["name"]
		prompt = "Harvest %s" % cname
	elif not is_watered and active.get("use_type") == "water":
		prompt = "Water Soil"
	elif is_tilled and crop_id == "" and active.get("use_type") == "plant":
		prompt = "Plant %s" % active.get("name", "Seeds")
	elif not is_tilled and active.get("use_type") == "till":
		prompt = "Till Soil"
	
	return {
		"id": plot_id,
		"name": "Farm Plot",
		"prompt": prompt
	}

func interact(player: Node2D) -> void:
	var active = InventoryService.get_active_item()
	
	# 1. Harvest mature crop
	if crop_id != "" and current_stage >= 2:
		_harvest_crop()
		return
	
	# 2. Water plot with Watering Can
	if is_tilled and not is_watered and active.get("use_type") == "water":
		if GameState.consume_stamina(4.0):
			is_watered = true
			_update_visuals()
			EventBus.notification_requested.emit("Watered crop plot.", 1.5)
		return
	
	# 3. Plant Seeds
	if is_tilled and crop_id == "" and active.get("use_type") == "plant":
		var plant_crop_id = active.get("crop_id", "")
		if CROP_SPECS.has(plant_crop_id):
			if InventoryService.consume_active_item(1):
				crop_id = plant_crop_id
				current_stage = 0
				_update_visuals()
				EventBus.notification_requested.emit("Planted %s." % active["name"], 1.8)
		return
	
	# 4. Till untilled soil with Hoe
	if not is_tilled and active.get("use_type") == "till":
		if GameState.consume_stamina(6.0):
			is_tilled = true
			_update_visuals()
			EventBus.notification_requested.emit("Tilled soil with field hoe.", 1.5)
		return
	
	# Default inspection
	if crop_id != "":
		var spec = CROP_SPECS[crop_id]
		var stage_desc = "Sprouting" if current_stage == 0 else ("Growing" if current_stage == 1 else "Ready for Harvest!")
		var water_desc = "Watered" if is_watered else "Needs Water"
		EventBus.notification_requested.emit("%s (%s • %s)" % [spec["name"], stage_desc, water_desc], 2.2)
	else:
		var state_desc = "Watered Soil" if is_watered else ("Tilled Soil (Ready for seeds)" if is_tilled else "Untilled Ground")
		EventBus.notification_requested.emit("Plot: %s" % state_desc, 2.0)

func _harvest_crop() -> void:
	if not CROP_SPECS.has(crop_id):
		return
	
	var spec = CROP_SPECS[crop_id]
	var harvest_item = spec["harvest_item"]
	var count = 1
	
	# Archi's Signature Perk: Green Thumb (bonus harvest)
	if GameState.current_protagonist == GameState.PROTAGONIST_ARCHI:
		count = 2 # Double yield from careful harvesting
		EventBus.notification_requested.emit("Green Thumb bonus! Harvested 2x %s!" % spec["name"], 2.5)
	else:
		EventBus.notification_requested.emit("Harvested %s." % spec["name"], 2.0)
	
	InventoryService.add_item(harvest_item, count)
	
	# Reset plot
	crop_id = ""
	current_stage = 0
	_update_visuals()

func advance_day() -> void:
	if is_watered:
		if crop_id != "" and current_stage < 2:
			current_stage += 1
		# Soil dries out each morning
		is_watered = false
	_update_visuals()

func _update_visuals() -> void:
	if not soil_sprite:
		return
	
	# Update Soil texture
	if not is_tilled:
		soil_sprite.region_rect = Rect2(0, 0, 32, 32) # Plain grass
	elif is_watered:
		soil_sprite.region_rect = Rect2(96, 0, 32, 32) # Watered soil
	else:
		soil_sprite.region_rect = Rect2(64, 0, 32, 32) # Dry soil
	
	# Update Crop texture
	if crop_sprite:
		if crop_id != "" and CROP_SPECS.has(crop_id):
			crop_sprite.visible = true
			var row = CROP_SPECS[crop_id]["row"]
			var col = clamp(current_stage, 0, 2)
			crop_sprite.region_rect = Rect2(col * 32, row * 32, 32, 32)
		else:
			crop_sprite.visible = false

func serialize() -> Dictionary:
	return {
		"plot_id": plot_id,
		"is_tilled": is_tilled,
		"is_watered": is_watered,
		"crop_id": crop_id,
		"current_stage": current_stage
	}

func deserialize(data: Dictionary) -> void:
	plot_id = str(data.get("plot_id", plot_id))
	is_tilled = bool(data.get("is_tilled", is_tilled))
	is_watered = bool(data.get("is_watered", is_watered))
	crop_id = str(data.get("crop_id", crop_id))
	current_stage = int(data.get("current_stage", current_stage))
	_update_visuals()
