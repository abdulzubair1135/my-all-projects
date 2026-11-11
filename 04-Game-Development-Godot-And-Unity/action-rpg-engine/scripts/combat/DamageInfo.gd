class_name DamageInfo
extends RefCounted

var amount: float = 0.0
var knockback_force: float = 0.0
var knockback_direction: Vector2 = Vector2.ZERO
var source: Node2D = null
var damage_type: String = "physical"
var is_critical: bool = false

func _init(p_amount: float = 0.0, p_knockback_force: float = 0.0, p_knockback_dir: Vector2 = Vector2.ZERO, p_source: Node2D = null, p_type: String = "physical") -> void:
	amount = p_amount
	knockback_force = p_knockback_force
	knockback_direction = p_knockback_dir.normalized()
	source = p_source
	damage_type = p_type
