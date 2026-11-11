class_name SpawnPoint
extends Marker2D

@export var spawn_id: String = "spawn_default"
@export var facing_direction: Player.Facing = Player.Facing.DOWN

func _ready() -> void:
	add_to_group("spawn_points")
