class_name Unit3D
extends CharacterBody3D

signal died(unit_id: String, team_id: int)

enum State {
	IDLE,
	APPROACHING,
	ATTACKING,
	DEAD
}

@export var unit_data: UnitCombatData
var current_state: State = State.IDLE
var target_unit: Unit3D = null
var attack_cooldown_timer: float = 0.0

var visual_root: Node3D
var torso_mesh: MeshInstance3D
var head_mesh: MeshInstance3D
var helmet_mesh: MeshInstance3D
var left_arm: MeshInstance3D
var right_arm: MeshInstance3D
var left_leg: MeshInstance3D
var right_leg: MeshInstance3D
var weapon_pivot: Node3D
var weapon_mesh: MeshInstance3D
var shield_mesh: MeshInstance3D

var walk_cycle_timer: float = 0.0

func _ready() -> void:
	if not unit_data:
		unit_data = UnitCombatData.new()
	if not visual_root:
		setup_visuals()

func setup_from_design(design: SoldierDesign, team: int, p_unit_id: String) -> void:
	if not unit_data:
		unit_data = UnitCombatData.new()
	unit_data.unit_id = p_unit_id
	unit_data.team_id = team
	unit_data.design_id = design.id
	
	var stats = design.calculate_derived_stats()
	unit_data.max_health = stats.max_health
	unit_data.current_health = stats.max_health
	unit_data.move_speed = stats.move_speed
	unit_data.armor = stats.armor
	unit_data.damage = stats.damage
	unit_data.attack_range = stats.attack_range
	unit_data.attack_interval = stats.attack_interval
	unit_data.projectile_speed = stats.projectile_speed
	unit_data.block_chance = stats.block_chance
	unit_data.is_ranged = stats.is_ranged
	
	setup_visuals(design)

func setup_visuals(design: SoldierDesign = null) -> void:
	for child in get_children():
		if child is Node3D and child.name == "VisualRoot":
			child.queue_free()
			
	visual_root = Node3D.new()
	visual_root.name = "VisualRoot"
	add_child(visual_root)
	
	# Determine colors
	var primary_col = Color(0.2, 0.45, 0.85)
	var secondary_col = Color(0.85, 0.7, 0.2)
	var skin_col = Color(0.92, 0.75, 0.6)
	var metal_col = Color(0.65, 0.68, 0.72)
	var dark_metal_col = Color(0.3, 0.33, 0.38)
	var leather_col = Color(0.42, 0.28, 0.16)
	
	if design:
		primary_col = design.primary_color
		secondary_col = design.secondary_color
	if unit_data and unit_data.team_id == 1:
		primary_col = Color(0.85, 0.22, 0.22) # Red enemy
		secondary_col = Color(0.25, 0.25, 0.25)
		
	# Material definitions
	var armor_mat = StandardMaterial3D.new()
	armor_mat.albedo_color = primary_col
	armor_mat.metallic = 0.5
	armor_mat.roughness = 0.4
	
	var skin_mat = StandardMaterial3D.new()
	skin_mat.albedo_color = skin_col
	skin_mat.roughness = 0.8
	
	var metal_mat = StandardMaterial3D.new()
	metal_mat.albedo_color = metal_col
	metal_mat.metallic = 0.85
	metal_mat.roughness = 0.25
	
	var trim_mat = StandardMaterial3D.new()
	trim_mat.albedo_color = secondary_col
	trim_mat.metallic = 0.6
	trim_mat.roughness = 0.3
	
	var leather_mat = StandardMaterial3D.new()
	leather_mat.albedo_color = leather_col
	leather_mat.roughness = 0.75
	
	var dark_metal_mat = StandardMaterial3D.new()
	dark_metal_mat.albedo_color = dark_metal_col
	dark_metal_mat.metallic = 0.7
	dark_metal_mat.roughness = 0.4
	
	# 1. Torso / Chestplate
	torso_mesh = MeshInstance3D.new()
	var box_torso = BoxMesh.new()
	box_torso.size = Vector3(0.55, 0.65, 0.32)
	torso_mesh.mesh = box_torso
	torso_mesh.position = Vector3(0, 0.95, 0)
	torso_mesh.set_surface_override_material(0, armor_mat)
	visual_root.add_child(torso_mesh)
	
	# Belt / Waist
	var belt = MeshInstance3D.new()
	var box_belt = BoxMesh.new()
	box_belt.size = Vector3(0.58, 0.12, 0.35)
	belt.mesh = box_belt
	belt.position = Vector3(0, 0.65, 0)
	belt.set_surface_override_material(0, leather_mat)
	visual_root.add_child(belt)
	
	# 2. Head (Spherical)
	head_mesh = MeshInstance3D.new()
	var head_sphere = SphereMesh.new()
	head_sphere.radius = 0.18
	head_sphere.height = 0.36
	head_mesh.mesh = head_sphere
	head_mesh.position = Vector3(0, 1.45, 0)
	head_mesh.set_surface_override_material(0, skin_mat)
	visual_root.add_child(head_mesh)
	
	# Helmet / Crown (If equipped)
	var helmet_id = design.helmet_id if design else "hlm_iron_sallet"
	if helmet_id == "hlm_crown_gold":
		helmet_mesh = MeshInstance3D.new()
		var crown_cyl = CylinderMesh.new()
		crown_cyl.top_radius = 0.22
		crown_cyl.bottom_radius = 0.2
		crown_cyl.height = 0.16
		helmet_mesh.mesh = crown_cyl
		helmet_mesh.position = Vector3(0, 1.6, 0)
		var crown_gold = StandardMaterial3D.new()
		crown_gold.albedo_color = Color(1.0, 0.82, 0.2)
		crown_gold.metallic = 0.95
		crown_gold.roughness = 0.15
		helmet_mesh.set_surface_override_material(0, crown_gold)
		visual_root.add_child(helmet_mesh)
		
		# Crown Jewels
		for ang in [0, 90, 180, 270]:
			var jewel = MeshInstance3D.new()
			var j_box = BoxMesh.new()
			j_box.size = Vector3(0.06, 0.08, 0.06)
			jewel.mesh = j_box
			var rad = deg_to_rad(ang)
			jewel.position = Vector3(cos(rad) * 0.21, 1.65, sin(rad) * 0.21)
			var ruby_mat = StandardMaterial3D.new()
			ruby_mat.albedo_color = Color(0.9, 0.1, 0.2)
			ruby_mat.metallic = 0.5
			jewel.set_surface_override_material(0, ruby_mat)
			visual_root.add_child(jewel)
	elif helmet_id != "hlm_none":
		helmet_mesh = MeshInstance3D.new()
		var hlm_box = BoxMesh.new()
		hlm_box.size = Vector3(0.42, 0.32, 0.42)
		helmet_mesh.mesh = hlm_box
		helmet_mesh.position = Vector3(0, 1.5, 0)
		helmet_mesh.set_surface_override_material(0, metal_mat)
		visual_root.add_child(helmet_mesh)
		
		# Visor slit
		var visor = MeshInstance3D.new()
		var visor_box = BoxMesh.new()
		visor_box.size = Vector3(0.32, 0.08, 0.05)
		visor.mesh = visor_box
		visor.position = Vector3(0, 1.48, -0.2)
		var black_mat = StandardMaterial3D.new()
		black_mat.albedo_color = Color(0.1, 0.1, 0.12)
		visor.set_surface_override_material(0, black_mat)
		visual_root.add_child(visor)
	
	# 3. Shoulder Pauldrons
	for side in [-1, 1]:
		var pauldron = MeshInstance3D.new()
		var p_box = BoxMesh.new()
		p_box.size = Vector3(0.2, 0.22, 0.3)
		pauldron.mesh = p_box
		pauldron.position = Vector3(side * 0.38, 1.25, 0)
		pauldron.rotation_degrees = Vector3(0, 0, -side * 15)
		pauldron.set_surface_override_material(0, trim_mat)
		visual_root.add_child(pauldron)
	
	# 4. Arms
	left_arm = MeshInstance3D.new()
	var arm_mesh = BoxMesh.new()
	arm_mesh.size = Vector3(0.16, 0.55, 0.16)
	left_arm.mesh = arm_mesh
	left_arm.position = Vector3(-0.38, 0.88, 0)
	left_arm.set_surface_override_material(0, armor_mat)
	visual_root.add_child(left_arm)
	
	right_arm = MeshInstance3D.new()
	right_arm.mesh = arm_mesh
	right_arm.position = Vector3(0.38, 0.88, 0)
	right_arm.set_surface_override_material(0, armor_mat)
	visual_root.add_child(right_arm)
	
	# 5. Legs
	var leg_mesh = BoxMesh.new()
	leg_mesh.size = Vector3(0.2, 0.65, 0.2)
	
	left_leg = MeshInstance3D.new()
	left_leg.mesh = leg_mesh
	left_leg.position = Vector3(-0.16, 0.32, 0)
	left_leg.set_surface_override_material(0, dark_metal_mat)
	visual_root.add_child(left_leg)
	
	right_leg = MeshInstance3D.new()
	right_leg.mesh = leg_mesh
	right_leg.position = Vector3(0.16, 0.32, 0)
	right_leg.set_surface_override_material(0, dark_metal_mat)
	visual_root.add_child(right_leg)
	
	# 6. Weapon in Right Hand Pivot
	weapon_pivot = Node3D.new()
	weapon_pivot.name = "WeaponPivot"
	weapon_pivot.position = Vector3(0.38, 0.65, -0.1)
	visual_root.add_child(weapon_pivot)
	
	var weapon_id = design.weapon_id if design else "wpn_sword_iron"
	_create_weapon_model(weapon_id, metal_mat, leather_mat, trim_mat)
	
	# 7. Shield on Left Arm (if equipped)
	var shield_id = design.shield_id if design else "shd_round_buckler"
	if shield_id != "shd_none":
		shield_mesh = MeshInstance3D.new()
		var s_box = BoxMesh.new()
		s_box.size = Vector3(0.1, 0.6, 0.45)
		shield_mesh.mesh = s_box
		shield_mesh.position = Vector3(-0.48, 0.85, -0.1)
		shield_mesh.set_surface_override_material(0, trim_mat)
		visual_root.add_child(shield_mesh)

func _create_weapon_model(wpn_id: String, metal: Material, wood: Material, trim: Material) -> void:
	weapon_mesh = MeshInstance3D.new()
	
	if wpn_id.contains("spear"):
		var shaft = CylinderMesh.new()
		shaft.top_radius = 0.03
		shaft.bottom_radius = 0.03
		shaft.height = 2.4
		weapon_mesh.mesh = shaft
		weapon_mesh.position = Vector3(0, 0.5, -0.4)
		weapon_mesh.rotation_degrees = Vector3(-70, 0, 0)
		weapon_mesh.set_surface_override_material(0, wood)
	elif wpn_id.contains("axe"):
		var shaft = CylinderMesh.new()
		shaft.top_radius = 0.04
		shaft.bottom_radius = 0.04
		shaft.height = 1.2
		weapon_mesh.mesh = shaft
		weapon_mesh.position = Vector3(0, 0.2, -0.2)
		weapon_mesh.rotation_degrees = Vector3(-35, 0, 0)
		weapon_mesh.set_surface_override_material(0, wood)
		
		var blade = MeshInstance3D.new()
		var b_box = BoxMesh.new()
		b_box.size = Vector3(0.05, 0.35, 0.3)
		blade.mesh = b_box
		blade.position = Vector3(0, 0.5, 0)
		blade.set_surface_override_material(0, metal)
		weapon_mesh.add_child(blade)
	elif wpn_id.contains("excalibur"):
		var blade = BoxMesh.new()
		blade.size = Vector3(0.12, 1.35, 0.04)
		weapon_mesh.mesh = blade
		weapon_mesh.position = Vector3(0, 0.6, -0.2)
		weapon_mesh.rotation_degrees = Vector3(-25, 0, 0)
		var gold_blade = StandardMaterial3D.new()
		gold_blade.albedo_color = Color(1.0, 0.88, 0.3)
		gold_blade.metallic = 0.95
		gold_blade.roughness = 0.15
		weapon_mesh.set_surface_override_material(0, gold_blade)
		
		var crossguard = MeshInstance3D.new()
		var cg_box = BoxMesh.new()
		cg_box.size = Vector3(0.4, 0.08, 0.08)
		crossguard.mesh = cg_box
		crossguard.position = Vector3(0, -0.5, 0)
		crossguard.set_surface_override_material(0, gold_blade)
		weapon_mesh.add_child(crossguard)
	elif wpn_id.contains("staff"):
		var shaft = CylinderMesh.new()
		shaft.top_radius = 0.04
		shaft.bottom_radius = 0.04
		shaft.height = 1.9
		weapon_mesh.mesh = shaft
		weapon_mesh.position = Vector3(0, 0.4, -0.2)
		weapon_mesh.set_surface_override_material(0, wood)
		
		var crystal = MeshInstance3D.new()
		var s_mesh = SphereMesh.new()
		s_mesh.radius = 0.14
		s_mesh.height = 0.28
		crystal.mesh = s_mesh
		crystal.position = Vector3(0, 0.95, 0)
		var crystal_mat = StandardMaterial3D.new()
		crystal_mat.albedo_color = Color(0.2, 0.7, 1.0)
		crystal_mat.emission_enabled = true
		crystal_mat.emission = Color(0.3, 0.8, 1.0)
		crystal_mat.emission_energy_multiplier = 2.0
		crystal.set_surface_override_material(0, crystal_mat)
		weapon_mesh.add_child(crystal)
	elif wpn_id.contains("bow"):
		var arc = BoxMesh.new()
		arc.size = Vector3(0.06, 1.2, 0.15)
		weapon_mesh.mesh = arc
		weapon_mesh.position = Vector3(0, 0.1, -0.2)
		weapon_mesh.set_surface_override_material(0, wood)
	else: # Default Sword
		var blade = BoxMesh.new()
		blade.size = Vector3(0.08, 0.95, 0.03)
		weapon_mesh.mesh = blade
		weapon_mesh.position = Vector3(0, 0.45, -0.15)
		weapon_mesh.rotation_degrees = Vector3(-25, 0, 0)
		weapon_mesh.set_surface_override_material(0, metal)
		
		var crossguard = MeshInstance3D.new()
		var cg_box = BoxMesh.new()
		cg_box.size = Vector3(0.28, 0.05, 0.06)
		crossguard.mesh = cg_box
		crossguard.position = Vector3(0, -0.4, 0)
		crossguard.set_surface_override_material(0, trim)
		weapon_mesh.add_child(crossguard)
		
	weapon_pivot.add_child(weapon_mesh)

func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		return
		
	if attack_cooldown_timer > 0.0:
		attack_cooldown_timer -= delta
		
	match current_state:
		State.IDLE:
			_process_idle_state()
		State.APPROACHING:
			_process_approaching_state(delta)
		State.ATTACKING:
			_process_attacking_state()

func _process_idle_state() -> void:
	if is_instance_valid(target_unit) and target_unit.unit_data.is_alive:
		current_state = State.APPROACHING
	else:
		target_unit = null

func _process_approaching_state(delta: float) -> void:
	if not is_instance_valid(target_unit) or not target_unit.unit_data.is_alive:
		target_unit = null
		current_state = State.IDLE
		velocity = Vector3.ZERO
		return
		
	var diff = target_unit.global_position - global_position
	diff.y = 0.0
	var dist = diff.length()
	
	if dist <= unit_data.attack_range:
		current_state = State.ATTACKING
		velocity = Vector3.ZERO
		return
		
	var dir = diff.normalized()
	look_at(Vector3(target_unit.global_position.x, global_position.y, target_unit.global_position.z), Vector3.UP)
	velocity = dir * unit_data.move_speed
	move_and_slide()
	
	# Procedural walk cycle animation
	walk_cycle_timer += delta * unit_data.move_speed * 4.0
	if is_instance_valid(left_leg) and is_instance_valid(right_leg):
		left_leg.rotation_degrees.x = sin(walk_cycle_timer) * 25.0
		right_leg.rotation_degrees.x = -sin(walk_cycle_timer) * 25.0
	if is_instance_valid(left_arm) and is_instance_valid(right_arm):
		left_arm.rotation_degrees.x = -sin(walk_cycle_timer) * 20.0
		right_arm.rotation_degrees.x = sin(walk_cycle_timer) * 20.0

func _process_attacking_state() -> void:
	if not is_instance_valid(target_unit) or not target_unit.unit_data.is_alive:
		target_unit = null
		current_state = State.IDLE
		return
		
	var dist = global_position.distance_to(target_unit.global_position)
	if dist > unit_data.attack_range * 1.3:
		current_state = State.APPROACHING
		return
		
	look_at(Vector3(target_unit.global_position.x, global_position.y, target_unit.global_position.z), Vector3.UP)
	
	if attack_cooldown_timer <= 0.0:
		perform_attack()

func perform_attack() -> void:
	attack_cooldown_timer = unit_data.attack_interval
	
	# Attack slash animation on weapon_pivot
	if is_instance_valid(weapon_pivot):
		var tw = create_tween()
		tw.tween_property(weapon_pivot, "rotation_degrees:x", 65.0, 0.1)
		tw.tween_property(weapon_pivot, "rotation_degrees:x", 0.0, 0.18)
		
	var audio = get_node_or_null("/root/AudioManager")
	if audio:
		audio.play_sword_clash()
	
	if is_instance_valid(target_unit) and target_unit.unit_data.is_alive:
		var result = target_unit.take_damage(unit_data.damage, unit_data.is_ranged, self)
		if not result.blocked:
			unit_data.damage_dealt += result.actual_damage
			if result.killed:
				unit_data.kills_count += 1
				target_unit = null
				current_state = State.IDLE

func take_damage(dmg: float, ranged: bool, attacker: Unit3D) -> Dictionary:
	var res = unit_data.apply_damage(dmg, ranged)
	
	if res.actual_damage > 0.0 and is_instance_valid(torso_mesh):
		var tw = create_tween()
		tw.tween_property(torso_mesh, "scale", Vector3(1.2, 0.9, 1.2), 0.08)
		tw.tween_property(torso_mesh, "scale", Vector3.ONE, 0.08)
		
	if res.killed:
		die()
	return res

func die() -> void:
	current_state = State.DEAD
	velocity = Vector3.ZERO
	died.emit(unit_data.unit_id, unit_data.team_id)
	
	var audio = get_node_or_null("/root/AudioManager")
	if audio:
		audio.play_unit_death()
		
	if is_instance_valid(visual_root):
		var tw = create_tween()
		tw.tween_property(visual_root, "rotation_degrees:x", 90.0, 0.25)
		tw.parallel().tween_property(visual_root, "position:y", -0.2, 0.25)
		tw.tween_interval(3.0)
		tw.tween_callback(queue_free)
