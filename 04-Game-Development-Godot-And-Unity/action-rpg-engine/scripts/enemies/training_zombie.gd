class_name TrainingZombie
extends BaseEnemy

func _init() -> void:
	enemy_name = "Training Zombie"
	max_health = 100.0
	current_health = 100.0
	move_speed = 45.0
	attack_damage = 10.0
	attack_knockback = 140.0
	detection_radius = 140.0
	attack_range = 24.0
	attack_cooldown = 1.3
	damage_type = "zombie_claw"
