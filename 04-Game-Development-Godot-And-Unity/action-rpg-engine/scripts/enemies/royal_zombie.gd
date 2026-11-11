class_name RoyalZombie
extends BaseEnemy

func _init() -> void:
	enemy_name = "Corrupted Royal Guard"
	max_health = 160.0
	current_health = 160.0
	move_speed = 30.0 # heavy, armored gait
	patrol_speed_mult = 0.4
	knockback_resistance = 0.50 # heavy armor resists 50% knockback
	attack_damage = 24.0 # dangerous royal sword strike
	attack_knockback = 240.0
	attack_range = 30.0 # longer melee reach with broken blade
	attack_cooldown = 1.6
	attack_windup = 0.16
	attack_duration = 0.50
	detection_radius = 150.0
	lose_target_radius = 230.0
	patrol_radius = 45.0
	damage_type = "royal_blade"
