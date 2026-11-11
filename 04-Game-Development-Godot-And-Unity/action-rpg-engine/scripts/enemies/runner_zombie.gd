class_name RunnerZombie
extends BaseEnemy

func _init() -> void:
	enemy_name = "Plague Runner"
	max_health = 40.0
	current_health = 40.0
	move_speed = 85.0 # faster than player base walk speed (85 vs 85)
	patrol_speed_mult = 0.65
	attack_damage = 14.0
	attack_knockback = 160.0
	attack_range = 24.0
	attack_cooldown = 0.8 # aggressive, fast recovery
	attack_windup = 0.08
	attack_duration = 0.28
	detection_radius = 175.0 # acute senses
	lose_target_radius = 260.0
	patrol_radius = 80.0
	damage_type = "runner_rend"
