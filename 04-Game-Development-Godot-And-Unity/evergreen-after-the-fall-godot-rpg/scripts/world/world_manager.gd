extends Node

# Evergreen: After the Fall - Central World Streaming & Region Manager
# Manages region transitions, spawn point handoffs, camera limits, and persistent world state deltas

signal region_transition_started(target_region: String)
signal region_transition_completed(region_id: String)

var current_region_id: String = "evergreen_farm"
var pending_spawn_id: String = "default"

# Regional scene directory
var regions: Dictionary = {
	"evergreen_farm": {
		"id": "evergreen_farm",
		"name": "Evergreen Farm",
		"scene_path": "res://scenes/world/EvergreenFarm.tscn",
		"safe_zone": true,
		"music": "ambient_farm"
	},
	"evergreen_village": {
		"id": "evergreen_village",
		"name": "Evergreen Village",
		"scene_path": "res://scenes/world/EvergreenVillage.tscn",
		"safe_zone": true,
		"music": "ambient_town"
	},
	"greenwood_forest": {
		"id": "greenwood_forest",
		"name": "Greenwood Forest",
		"scene_path": "res://scenes/world/GreenwoodForest.tscn",
		"safe_zone": false,
		"music": "ambient_forest"
	},
	"crystal_lake": {
		"id": "crystal_lake",
		"name": "Crystal Lake",
		"scene_path": "res://scenes/world/CrystalLake.tscn",
		"safe_zone": true,
		"music": "ambient_lake"
	},
	"old_city": {
		"id": "old_city",
		"name": "Old City",
		"scene_path": "res://scenes/world/OldCity.tscn",
		"safe_zone": false,
		"music": "ambient_city"
	},
	"abandoned_hospital": {
		"id": "abandoned_hospital",
		"name": "Abandoned Hospital",
		"scene_path": "res://scenes/world/AbandonedHospital.tscn",
		"safe_zone": false,
		"music": "ambient_hospital"
	},
	"high_school": {
		"id": "high_school",
		"name": "Evergreen High School",
		"scene_path": "res://scenes/world/HighSchool.tscn",
		"safe_zone": false,
		"music": "ambient_school"
	},
	"police_station": {
		"id": "police_station",
		"name": "Police Station",
		"scene_path": "res://scenes/world/PoliceStation.tscn",
		"safe_zone": false,
		"music": "ambient_station"
	},
	"supermarket_district": {
		"id": "supermarket_district",
		"name": "Supermarket District",
		"scene_path": "res://scenes/world/SupermarketDistrict.tscn",
		"safe_zone": false,
		"music": "ambient_market"
	},
	"railway_station": {
		"id": "railway_station",
		"name": "Railway Station",
		"scene_path": "res://scenes/world/RailwayStation.tscn",
		"safe_zone": false,
		"music": "ambient_train"
	},
	"military_camp": {
		"id": "military_camp",
		"name": "Military Camp",
		"scene_path": "res://scenes/world/MilitaryCamp.tscn",
		"safe_zone": false,
		"music": "ambient_military"
	},
	"underground_lab": {
		"id": "underground_lab",
		"name": "Underground Laboratory",
		"scene_path": "res://scenes/world/UndergroundLab.tscn",
		"safe_zone": false,
		"music": "ambient_lab"
	},
	"snow_mountain": {
		"id": "snow_mountain",
		"name": "Snow Mountain",
		"scene_path": "res://scenes/world/SnowMountain.tscn",
		"safe_zone": false,
		"music": "ambient_mountain"
	},
	"graveyard_chapel": {
		"id": "graveyard_chapel",
		"name": "Graveyard and Chapel",
		"scene_path": "res://scenes/world/GraveyardChapel.tscn",
		"safe_zone": false,
		"music": "ambient_chapel"
	},
	"secret_bunker": {
		"id": "secret_bunker",
		"name": "Secret Bunker",
		"scene_path": "res://scenes/world/SecretBunker.tscn",
		"safe_zone": true,
		"music": "ambient_bunker"
	}
}

# Persistent world deltas: region_id -> Dictionary of changed state
var region_deltas: Dictionary = {}

var discovered_regions: Array[String] = ["evergreen_farm"]

func _ready() -> void:
	EventBus.region_change_requested.connect(transition_to_region)

func transition_to_region(target_region_id: String, target_spawn_id: String = "default") -> void:
	if not regions.has(target_region_id):
		printerr("[WorldManager] Unknown region target: %s" % target_region_id)
		return
	
	print("[WorldManager] Transitioning from %s to %s (Spawn: %s)" % [current_region_id, target_region_id, target_spawn_id])
	region_transition_started.emit(target_region_id)
	
	pending_spawn_id = target_spawn_id
	current_region_id = target_region_id
	GameState.is_in_safe_zone = regions[target_region_id]["safe_zone"]
	
	if not discovered_regions.has(target_region_id):
		discovered_regions.append(target_region_id)
		EventBus.notification_requested.emit("Discovered New Region: %s!" % regions[target_region_id]["name"], 3.5)
	else:
		EventBus.notification_requested.emit("Entering %s" % regions[target_region_id]["name"], 2.0)
	
	var scene_path = regions[target_region_id]["scene_path"]
	get_tree().change_scene_to_file.call_deferred(scene_path)

func apply_player_spawn(player: CharacterBody2D) -> void:
	if not is_instance_valid(player):
		return
	
	var tree = player.get_tree()
	var spawn_node_name = "SpawnPoint_" + pending_spawn_id
	var spawn_marker = tree.current_scene.find_child(spawn_node_name, true, false)
	
	if spawn_marker != null:
		player.global_position = spawn_marker.global_position
		print("[WorldManager] Placed player at spawn marker: %s (%s)" % [spawn_node_name, spawn_marker.global_position])
	else:
		# Fallback to default spawn marker or scene default
		var def_marker = tree.current_scene.find_child("SpawnPoint_default", true, false)
		if def_marker != null:
			player.global_position = def_marker.global_position
	
	region_transition_completed.emit(current_region_id)

func serialize() -> Dictionary:
	return {
		"current_region_id": current_region_id,
		"discovered_regions": discovered_regions.duplicate(),
		"region_deltas": region_deltas.duplicate(true)
	}

func deserialize(data: Dictionary) -> void:
	if data.has("current_region_id"):
		current_region_id = data["current_region_id"]
	if data.has("discovered_regions"):
		discovered_regions = data["discovered_regions"].duplicate()
	if data.has("region_deltas"):
		region_deltas = data["region_deltas"].duplicate(true)
