class_name UnitCombatData
extends Resource

var unit_id: String = ""
var team_id: int = 0
var design_id: String = ""
var max_health: float = 100.0
var current_health: float = 100.0
var move_speed: float = 3.5
var armor: float = 5.0
var damage: float = 12.0
var attack_range: float = 2.0
var attack_interval: float = 1.0
var projectile_speed: float = 0.0
var block_chance: float = 0.0
var is_ranged: bool = false
var is_alive: bool = true

# Tracking for post-battle statistics
var damage_dealt: float = 0.0
var damage_taken: float = 0.0
var kills_count: int = 0

func apply_damage(raw_damage: float, is_ranged_attack: bool = false) -> Dictionary:
	if not is_alive:
		return {"blocked": false, "actual_damage": 0.0, "killed": false}
	
	# Block check
	if block_chance > 0.0 and randf() < block_chance:
		return {"blocked": true, "actual_damage": 0.0, "killed": false}
	
	# Armor reduction formula: effective_damage = raw * (100 / (100 + armor))
	var reduction = 100.0 / (100.0 + armor)
	var final_damage = max(1.0, raw_damage * reduction)
	
	current_health -= final_damage
	damage_taken += final_damage
	
	var killed = false
	if current_health <= 0.0:
		current_health = 0.0
		is_alive = false
		killed = true
		
	return {
		"blocked": false,
		"actual_damage": final_damage,
		"killed": killed
	}
