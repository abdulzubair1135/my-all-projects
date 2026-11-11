extends Area2D
class_name Hitbox

# Evergreen: After the Fall - Hitbox Component
# Deals directional combat damage and knockback to overlapping Hurtbox areas

@export var damage: float = 25.0
@export var knockback_force: float = 200.0
@export var knockback_direction: Vector2 = Vector2.ZERO
@export var attacker: Node2D = null

func _ready() -> void:
	area_entered.connect(_on_area_entered)

func check_overlaps() -> void:
	for area in get_overlapping_areas():
		if area is Hurtbox and area.owner != attacker and area.can_take_damage:
			_on_area_entered(area)

func _on_area_entered(area: Area2D) -> void:
	if area is Hurtbox:
		var hurtbox = area as Hurtbox
		if hurtbox.owner != attacker and hurtbox.can_take_damage:
			var dir = knockback_direction
			if dir == Vector2.ZERO and attacker != null:
				dir = (hurtbox.global_position - attacker.global_position).normalized()
			hurtbox.receive_hit(damage, dir * knockback_force, attacker)
