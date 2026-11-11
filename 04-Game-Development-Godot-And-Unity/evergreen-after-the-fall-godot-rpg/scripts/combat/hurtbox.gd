extends Area2D
class_name Hurtbox

# Evergreen: After the Fall - Hurtbox Component
# Receives incoming combat strikes, handles invulnerability frames, and notifies owner

signal hit_received(damage: float, knockback: Vector2, attacker: Node2D)

@export var can_take_damage: bool = true
@export var invulnerability_duration: float = 0.25

var invuln_timer: float = 0.0

func _process(delta: float) -> void:
	if invuln_timer > 0.0:
		invuln_timer -= delta
		if invuln_timer <= 0.0:
			can_take_damage = true

func receive_hit(damage: float, knockback: Vector2, attacker: Node2D) -> void:
	if not can_take_damage:
		return
	
	can_take_damage = false
	invuln_timer = invulnerability_duration
	hit_received.emit(damage, knockback, attacker)

func take_hit(damage: float, knockback: Vector2, attacker: Node2D) -> void:
	receive_hit(damage, knockback, attacker)
