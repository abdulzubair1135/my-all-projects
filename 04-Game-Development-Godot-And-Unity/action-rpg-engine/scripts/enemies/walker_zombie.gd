class_name WalkerZombie
extends BaseEnemy

func _init() -> void:
	enemy_name = "Plague Walker"
	max_health = 60.0
	current_health = 60.0
	move_speed = 35.0
	patrol_speed_mult = 0.5
	attack_damage = 10.0
	attack_knockback = 120.0
	attack_range = 22.0
	attack_cooldown = 1.4
	detection_radius = 125.0
	lose_target_radius = 200.0
	patrol_radius = 50.0
	damage_type = "walker_swipe"
