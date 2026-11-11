extends Area2D
class_name RegionExit

# Evergreen: After the Fall - Region Exit & World Transition Trigger
# Connects world borders, roads, and trails to target regions with named spawn points

@export var target_region: String = "evergreen_village"
@export var target_spawn: String = "default"
@export var region_title: String = "Evergreen Village"

func _ready() -> void:
	add_to_group("interactables")
	collision_layer = 2
	collision_mask = 1
	body_entered.connect(_on_body_entered)

func get_interaction_info() -> Dictionary:
	return {
		"id": "exit_" + target_region,
		"name": "Road to " + region_title,
		"prompt": "Travel to " + region_title
	}

func interact(_player: Node2D) -> void:
	WorldManager.transition_to_region(target_region, target_spawn)

func _on_body_entered(body: Node2D) -> void:
	if body is PlayerController or body.is_in_group("player"):
		# Automatic transition when walking through gate
		WorldManager.transition_to_region(target_region, target_spawn)
