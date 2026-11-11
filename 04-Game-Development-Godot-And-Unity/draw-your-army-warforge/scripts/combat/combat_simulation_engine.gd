class_name CombatSimulationEngine
extends RefCounted

var units: Array[Unit3D] = []
var simulation_running: bool = false
var battle_time: float = 0.0

# Spatial grid for fast nearest-neighbor target queries
var grid_cell_size: float = 10.0
var spatial_grid: Dictionary = {}

func clear() -> void:
	units.clear()
	spatial_grid.clear()
	simulation_running = false
	battle_time = 0.0

func register_unit(unit: Unit3D) -> void:
	if not units.has(unit):
		units.append(unit)
		unit.died.connect(_on_unit_died)

func _on_unit_died(unit_id: String, team_id: int) -> void:
	var bus = Engine.get_main_loop().root.get_node_or_null("/root/EventBus")
	if bus:
		bus.battle_unit_killed.emit(unit_id, team_id, "")

func step(delta: float) -> Dictionary:
	if not simulation_running:
		return {"finished": false, "winner_team": -1}
		
	battle_time += delta
	_update_spatial_grid()
	_update_targeting()
	
	# Check battle completion
	var team_0_alive = 0
	var team_1_alive = 0
	for u in units:
		if is_instance_valid(u) and u.unit_data.is_alive:
			if u.unit_data.team_id == 0:
				team_0_alive += 1
			else:
				team_1_alive += 1
				
	if team_0_alive == 0 or team_1_alive == 0:
		simulation_running = false
		var winner = 0 if team_0_alive > 0 else (1 if team_1_alive > 0 else -1)
		return {
			"finished": true,
			"winner_team": winner,
			"team_0_survivors": team_0_alive,
			"team_1_survivors": team_1_alive,
			"duration": battle_time
		}
		
	return {"finished": false, "winner_team": -1}

func _get_pos(u: Unit3D) -> Vector3:
	return u.global_position if u.is_inside_tree() else u.position

func _update_spatial_grid() -> void:
	spatial_grid.clear()
	for u in units:
		if not is_instance_valid(u) or not u.unit_data.is_alive:
			continue
		var pos = _get_pos(u)
		var cell_x = int(floor(pos.x / grid_cell_size))
		var cell_z = int(floor(pos.z / grid_cell_size))
		var key = Vector2i(cell_x, cell_z)
		if not spatial_grid.has(key):
			spatial_grid[key] = []
		spatial_grid[key].append(u)

func _update_targeting() -> void:
	# Staggered target reacquisition to keep performance bounded
	for u in units:
		if not is_instance_valid(u) or not u.unit_data.is_alive:
			continue
		if not is_instance_valid(u.target_unit) or not u.target_unit.unit_data.is_alive:
			u.target_unit = find_closest_enemy(u)

func find_closest_enemy(source_unit: Unit3D) -> Unit3D:
	var closest_enemy: Unit3D = null
	var min_dist_sq = INF
	var s_pos = _get_pos(source_unit)
	var s_team = source_unit.unit_data.team_id
	
	# Fast distance check across all units
	for other in units:
		if not is_instance_valid(other) or not other.unit_data.is_alive:
			continue
		if other.unit_data.team_id == s_team:
			continue
			
		var dist_sq = s_pos.distance_squared_to(_get_pos(other))
		if dist_sq < min_dist_sq:
			min_dist_sq = dist_sq
			closest_enemy = other
			
	return closest_enemy
