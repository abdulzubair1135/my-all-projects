class_name ArmyLoadout
extends RefCounted

const SCHEMA_VERSION = "1.0.0"

var id: String = ""
var name: String = "Vanguard Legion"
var description: String = "Balanced battle formation"
# units array contains elements:
# { "unit_id": String, "design_id": String, "position": Vector3, "rotation_y": float }
var units: Array[Dictionary] = []
var custom_soldiers: Dictionary = {} # design_id -> SoldierDesign.serialize()

func _init(p_id: String = "", p_name: String = "Vanguard Legion") -> void:
	if p_id.is_empty():
		id = "army_" + str(Time.get_unix_time_from_system()).sha1_text().substr(0, 8)
	else:
		id = p_id
	name = p_name

func calculate_total_cost() -> int:
	var total = 0
	# Cache calculated costs per design
	var cost_cache: Dictionary = {}
	for design_id in custom_soldiers:
		var design = SoldierDesign.deserialize(custom_soldiers[design_id])
		cost_cache[design_id] = design.calculate_derived_stats().total_cost
		
	for unit in units:
		var d_id = unit.get("design_id", "")
		if cost_cache.has(d_id):
			total += cost_cache[d_id]
		else:
			# Default infantry cost fallback
			total += 15
	return total

func validate_army(budget_limit: int = 1000, max_units: int = 300) -> Dictionary:
	var errors: Array[String] = []
	var total_cost = calculate_total_cost()
	
	if units.is_empty():
		errors.append("Army cannot be empty. Place at least one unit.")
	if units.size() > max_units:
		errors.append("Army unit count exceeds maximum limit (" + str(units.size()) + " > " + str(max_units) + ").")
	if total_cost > budget_limit:
		errors.append("Army cost exceeds points budget (" + str(total_cost) + " > " + str(budget_limit) + ").")
		
	# Check spatial collisions and duplicates
	var pos_set = {}
	for i in range(units.size()):
		var u = units[i]
		var pos = u.get("position", Vector3.ZERO)
		if typeof(pos) == TYPE_ARRAY:
			pos = Vector3(pos[0], pos[1], pos[2])
		var key = "%0.1f_%0.1f" % [pos.x, pos.z]
		if pos_set.has(key):
			errors.append("Overlapping units detected at coordinates: (" + key + ").")
			break
		pos_set[key] = true
		
	return {
		"is_valid": errors.is_empty(),
		"total_cost": total_cost,
		"unit_count": units.size(),
		"errors": errors
	}

func serialize() -> Dictionary:
	var serialized_units: Array = []
	for u in units:
		var pos = u.get("position", Vector3.ZERO)
		var p_arr = [pos.x, pos.y, pos.z] if typeof(pos) == TYPE_VECTOR3 else pos
		serialized_units.append({
			"unit_id": u.get("unit_id", ""),
			"design_id": u.get("design_id", ""),
			"position": p_arr,
			"rotation_y": float(u.get("rotation_y", 0.0))
		})
	return {
		"schema_version": SCHEMA_VERSION,
		"id": id,
		"name": name,
		"description": description,
		"units": serialized_units,
		"custom_soldiers": custom_soldiers
	}

static func deserialize(data: Dictionary) -> ArmyLoadout:
	var army = ArmyLoadout.new(data.get("id", ""), data.get("name", "Vanguard Legion"))
	army.description = data.get("description", "")
	var raw_units = data.get("units", [])
	army.units = []
	for u in raw_units:
		var p = u.get("position", [0,0,0])
		var vec = Vector3(p[0], p[1], p[2]) if typeof(p) == TYPE_ARRAY and p.size() >= 3 else Vector3.ZERO
		army.units.append({
			"unit_id": u.get("unit_id", ""),
			"design_id": u.get("design_id", ""),
			"position": vec,
			"rotation_y": float(u.get("rotation_y", 0.0))
		})
	army.custom_soldiers = data.get("custom_soldiers", {})
	return army
