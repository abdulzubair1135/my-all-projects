class_name Hurtbox
extends Area2D

signal hit_received(damage_info: DamageInfo)

@export var owner_node: Node2D
var is_invulnerable: bool = false

func _ready() -> void:
	if not owner_node and get_parent() is Node2D:
		owner_node = get_parent() as Node2D
	# Hurtboxes are passive targets: monitorable = true, monitoring = false
	monitoring = false
	monitorable = true

func receive_damage(damage_info: DamageInfo) -> bool:
	if is_invulnerable:
		return false
	hit_received.emit(damage_info)
	return true
