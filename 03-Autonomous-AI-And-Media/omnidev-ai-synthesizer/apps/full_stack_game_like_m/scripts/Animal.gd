class_name Animal
extends CharacterBody3D

var _animal_type: String = "cow"

# Animal types
enum AnimalType {
	COW,
	SHEEP,
	PIG
}

# AI States
enum AIState {
	WANDERING,
	FLEEING,
	DEAD,
	IDLE
}

# Core properties
@export var animal_type: int = AnimalType.COW
@export var wander_speed: float = 1.2
@export var flee_speed: float = 4.0
@export var health: int = 4
@export var max_health: int = 4
@export var detection_range: float = 10.0
@export var death_rotation_time: float = 0.6

# Internal state
var state: AIState = AIState.WANDERING
var wander_target: Vector3
var wander_timer: float = 0.0
var wander_interval: float = 3.0
var graze_timer: float = 0.0
var is_grazing: bool = false
var leg_phase: float = 0.0
var death_timer: float = 0.0
var is_dead: bool = false
var original_position: Vector3
var original_rotation: Vector3
var hit_flash_timer: float = 0.0
var is_flashing: bool = false
var idle_timer: float = 0.0
var is_idle: bool = false

# Mesh components
var torso_mesh: MeshInstance3D
var head_mesh: MeshInstance3D
var leg_fl: MeshInstance3D
var leg_fr: MeshInstance3D
var leg_bl: MeshInstance3D
var leg_br: MeshInstance3D
var ear_l: MeshInstance3D
var ear_r: MeshInstance3D
var horn_l: MeshInstance3D
var horn_r: MeshInstance3D
var tail_mesh: MeshInstance3D

# Materials
var body_material: StandardMaterial3D
var original_color: Color
var flash_material: StandardMaterial3D

# References
var player_ref: Node3D

func _ready():
	original_position = global_position
	original_rotation = rotation
	
	if has_node("CollisionShape3D"):
		var col = get_node("CollisionShape3D")
		var shape = BoxShape3D.new()
		shape.size = Vector3(1.4, 1.2, 1.8)
		col.shape = shape
	
	build_procedural_model()
	pick_new_wander_target()
	
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player_ref = players[0]

func build_procedural_model():
	body_material = StandardMaterial3D.new()
	body_material.albedo_color = get_animal_color()
	body_material.roughness = 0.9
	body_material.metallic = 0.0
	original_color = body_material.albedo_color
	
	flash_material = StandardMaterial3D.new()
	flash_material.albedo_color = Color(1.0, 0.2, 0.2)
	flash_material.roughness = 0.5
	
	# Torso
	torso_mesh = MeshInstance3D.new()
	var torso_box = BoxMesh.new()
	torso_box.size = Vector3(1.2, 0.8, 2.0)
	torso_mesh.mesh = torso_box
	torso_mesh.material_override = body_material
	torso_mesh.position = Vector3(0, 0.6, 0)
	add_child(torso_mesh)
	
	# Head
	head_mesh = MeshInstance3D.new()
	var head_box = BoxMesh.new()
	head_box.size = Vector3(0.8, 0.6, 0.8)
	head_mesh.mesh = head_box
	head_mesh.material_override = body_material
	head_mesh.position = Vector3(0, 0.9, 1.2)
	add_child(head_mesh)
	
	# Legs
	var leg_size = Vector3(0.2, 0.7, 0.2)
	leg_fl = create_leg(Vector3(-0.5, 0.0, -0.8), leg_size)
	leg_fr = create_leg(Vector3(0.5, 0.0, -0.8), leg_size)
	leg_bl = create_leg(Vector3(-0.5, 0.0, 0.8), leg_size)
	leg_br = create_leg(Vector3(0.5, 0.0, 0.8), leg_size)
	
	# Ears (sheep and cow)
	if animal_type == AnimalType.SHEEP or animal_type == AnimalType.COW:
		var ear_size = Vector3(0.15, 0.05, 0.2)
		ear_l = create_ear(Vector3(-0.45, 0.95, 1.4), ear_size, true)
		ear_r = create_ear(Vector3(0.45, 0.95, 1.4), ear_size, false)
	
	# Horns (cow only)
	if animal_type == AnimalType.COW:
		var horn_size = Vector3(0.08, 0.15, 0.08)
		horn_l = create_horn(Vector3(-0.35, 1.05, 1.3), horn_size, true)
		horn_r = create_horn(Vector3(0.35, 1.05, 1.3), horn_size, false)
	
	# Tail
	tail_mesh = MeshInstance3D.new()
	var tail_box = BoxMesh.new()
	tail_box.size = Vector3(0.08, 0.08, 0.4)
	tail_mesh.mesh = tail_box
	tail_mesh.material_override = body_material
	tail_mesh.position = Vector3(0, 0.6, -1.1)
	add_child(tail_mesh)

func create_leg(position: Vector3, size: Vector3) -> MeshInstance3D:
	var leg = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = size
	leg.mesh = box
	leg.material_override = body_material
	leg.position = position
	add_child(leg)
	return leg

func create_ear(position: Vector3, size: Vector3, is_left: bool) -> MeshInstance3D:
	var ear = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = size
	ear.mesh = box
	ear.material_override = body_material
	ear.position = position
	if is_left:
		ear.rotation.z = 0.3
	else:
		ear.rotation.z = -0.3
	add_child(ear)
	return ear

func create_horn(position: Vector3, size: Vector3, is_left: bool) -> MeshInstance3D:
	var horn = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = size
	horn.mesh = box
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.7, 0.65, 0.6)
	mat.roughness = 0.7
	horn.material_override = mat
	horn.position = position
	if is_left:
		horn.rotation.z = -0.3
	else:
		horn.rotation.z = 0.3
	add_child(horn)
	return horn

func get_animal_color() -> Color:
	match animal_type:
		AnimalType.COW:
			return Color(0.55, 0.3, 0.2)
		AnimalType.SHEEP:
			return Color(0.85, 0.82, 0.78)
		AnimalType.PIG:
			return Color(0.8, 0.55, 0.55)
		_:
			return Color(0.7, 0.7, 0.7)

func _physics_process(delta: float):
	if is_dead:
		return
	
	if is_flashing:
		hit_flash_timer -= delta
		if hit_flash_timer <= 0.0:
			set_body_color(original_color)
			is_flashing = false
	
	match state:
		AIState.WANDERING:
			handle_wandering(delta)
		AIState.FLEEING:
			handle_fleeing(delta)
		AIState.DEAD:
			handle_death(delta)
		AIState.IDLE:
			handle_idle(delta)
	
	if velocity.length() > 0.1 and state != AIState.DEAD:
		leg_phase += delta * velocity.length() * 2.5
		animate_legs(leg_phase)
	else:
		animate_legs(0.0)

func handle_wandering(delta: float):
	if is_grazing:
		graze_timer -= delta
		if graze_timer <= 0.0:
			is_grazing = false
			pick_new_wander_target()
		velocity = Vector3.ZERO
		return
	
	if is_idle:
		idle_timer -= delta
		if idle_timer <= 0.0:
			is_idle = false
			pick_new_wander_target()
		velocity = Vector3.ZERO
		return
	
	var direction = (wander_target - global_position).normalized()
	direction.y = 0.0
	var distance = global_position.distance_to(wander_target)
	
	if distance < 0.8:
		if randf() < 0.4:
			is_idle = true
			idle_timer = randf_range(0.5, 2.0)
		else:
			pick_new_wander_target()
		return
	
	velocity = direction * wander_speed
	move_and_slide()
	
	if velocity.length() > 0.1:
		var target_rotation = atan2(direction.x, direction.z)
		rotation.y = lerp_angle(rotation.y, target_rotation, delta * 4.0)
	
	wander_timer -= delta
	if wander_timer <= 0.0 and not is_grazing and not is_idle:
		if randf() < 0.35:
			is_grazing = true
			graze_timer = randf_range(1.5, 4.0)
		else:
			pick_new_wander_target()
	
	if player_ref:
		var distance_to_player = global_position.distance_to(player_ref.global_position)
		if distance_to_player < detection_range:
			state = AIState.FLEEING

func handle_fleeing(delta: float):
	if not player_ref:
		state = AIState.WANDERING
		return
	
	var flee_direction = (global_position - player_ref.global_position).normalized()
	flee_direction.y = 0.0
	
	if flee_direction.length() < 0.1:
		flee_direction = Vector3(0, 0, 1)
	
	velocity = flee_direction * flee_speed
	move_and_slide()
	
	if velocity.length() > 0.1:
		var target_rotation = atan2(flee_direction.x, flee_direction.z)
		rotation.y = lerp_angle(rotation.y, target_rotation, delta * 5.0)
	
	if player_ref:
		var distance = global_position.distance_to(player_ref.global_position)
		if distance > detection_range * 1.8:
			state = AIState.WANDERING
			pick_new_wander_target()

func handle_idle(delta: float):
	idle_timer -= delta
	if idle_timer <= 0.0:
		is_idle = false
		pick_new_wander_target()

func handle_death(delta: float):
	death_timer += delta
	var target_rotation_x = deg_to_rad(-90.0)
	rotation.x = lerp_angle(rotation.x, target_rotation_x, delta * 3.0)
	position.y = original_position.y - 0.3
	
	if death_timer > 1.5:
		queue_free()

func animate_legs(phase: float):
	var leg_swing = sin(phase) * 0.3
	
	if leg_fl:
		leg_fl.rotation.x = leg_swing
	if leg_fr:
		leg_fr.rotation.x = -leg_swing
	if leg_bl:
		leg_bl.rotation.x = -leg_swing
	if leg_br:
		leg_br.rotation.x = leg_swing

func pick_new_wander_target():
	var range_x = randf_range(-8.0, 8.0)
	var range_z = randf_range(-8.0, 8.0)
	wander_target = global_position + Vector3(range_x, 0, range_z)
	wander_timer = randf_range(2.0, 6.0)
	is_grazing = false
	is_idle = false

func set_body_color(color: Color):
	body_material.albedo_color = color
	if torso_mesh:
		torso_mesh.material_override = body_material
	if head_mesh:
		head_mesh.material_override = body_material
	if leg_fl:
		leg_fl.material_override = body_material
	if leg_fr:
		leg_fr.material_override = body_material
	if leg_bl:
		leg_bl.material_override = body_material
	if leg_br:
		leg_br.material_override = body_material
	if ear_l:
		ear_l.material_override = body_material
	if ear_r:
		ear_r.material_override = body_material
	if tail_mesh:
		tail_mesh.material_override = body_material

func take_damage(amount: int):
	if is_dead:
		return
	
	health -= amount
	
	is_flashing = true
	hit_flash_timer = 0.15
	set_body_color(Color(1.0, 0.2, 0.2))
	
	if has_node("/root/SoundManager"):
		var sm = get_node("/root/SoundManager")
		if sm.has_method("play_hit"):
			sm.play_hit()
	
	if health <= 0:
		die()
	else:
		state = AIState.FLEEING
		if player_ref:
			var flee_dir = (global_position - player_ref.global_position).normalized()
			wander_target = global_position + flee_dir * 8.0

func die():
	is_dead = true
	state = AIState.DEAD
	death_timer = 0.0
	velocity = Vector3.ZERO
	
	spawn_drop_item()
	
	if has_node("/root/SoundManager"):
		var sm = get_node("/root/SoundManager")
		if sm.has_method("play_break"):
			sm.play_break()

func spawn_drop_item():
	var drop = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = Vector3(0.3, 0.3, 0.3)
	drop.mesh = box
	
	var mat = StandardMaterial3D.new()
	mat.roughness = 0.6
	match animal_type:
		AnimalType.COW:
			mat.albedo_color = Color(0.5, 0.15, 0.1)
		AnimalType.SHEEP:
			mat.albedo_color = Color(0.9, 0.85, 0.8)
		AnimalType.PIG:
			mat.albedo_color = Color(0.85, 0.5, 0.5)
	mat.albedo_color.a = 1.0
	drop.material_override = mat
	drop.position = global_position + Vector3(0, 0.5, 0)
	get_parent().add_child(drop)

func lerp_angle(from: float, to: float, weight: float) -> float:
	var diff = to - from
	while diff > PI:
		diff -= TAU
	while diff < -PI:
		diff += TAU
	return from + diff * weight
