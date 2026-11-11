class_name Animal
class_name Villager
extends CharacterBody3D

var _animal_type: String = "cow"

enum AIState { WANDERING, FLEEING, DEAD, IDLE }

@export var wander_speed: float = 1.0
@export var flee_speed: float = 3.5
@export var health: int = 6
@export var max_health: int = 6
@export var detection_range: float = 8.0

var state: AIState = AIState.WANDERING
var wander_target: Vector3
var wander_timer: float = 0.0
var leg_phase: float = 0.0
var death_timer: float = 0.0
var is_dead: bool = false
var original_position: Vector3
var hit_flash_timer: float = 0.0
var is_flashing: bool = false

var body_material: StandardMaterial3D
var original_color: Color

var torso: MeshInstance3D
var head: MeshInstance3D
var left_arm: MeshInstance3D
var right_arm: MeshInstance3D
var left_leg: MeshInstance3D
var right_leg: MeshInstance3D

var player_ref: Node3D

func _ready():
	original_position = global_position
	build_procedural_model()
	pick_new_wander_target()
	var players = get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		player_ref = players[0]

func build_procedural_model():
	body_material = StandardMaterial3D.new()
	body_material.albedo_color = Color(0.8, 0.7, 0.6)
	body_material.roughness = 0.9
	original_color = body_material.albedo_color
	
	# Torso
	torso = MeshInstance3D.new()
	var t_box = BoxMesh.new()
	t_box.size = Vector3(0.8, 0.9, 0.5)
	torso.mesh = t_box
	torso.material_override = body_material
	torso.position = Vector3(0, 0.9, 0)
	add_child(torso)
	
	# Head
	head = MeshInstance3D.new()
	var h_box = BoxMesh.new()
	h_box.size = Vector3(0.5, 0.5, 0.5)
	head.mesh = h_box
	head.material_override = body_material
	head.position = Vector3(0, 1.5, 0)
	add_child(head)
	
	# Arms
	var arm_size = Vector3(0.15, 0.6, 0.15)
	left_arm = create_limb(Vector3(-0.55, 0.8, 0), arm_size)
	right_arm = create_limb(Vector3(0.55, 0.8, 0), arm_size)
	
	# Legs
	var leg_size = Vector3(0.2, 0.6, 0.2)
	left_leg = create_limb(Vector3(-0.25, 0.3, 0), leg_size)
	right_leg = create_limb(Vector3(0.25, 0.3, 0), leg_size)

func create_limb(pos: Vector3, size: Vector3) -> MeshInstance3D:
	var limb = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = size
	limb.mesh = box
	limb.material_override = body_material
	limb.position = pos
	add_child(limb)
	return limb

func _physics_process(delta: float):
	if is_dead:
		return
	if is_flashing:
		hit_flash_timer -= delta
		if hit_flash_timer <= 0:
			set_body_color(original_color)
			is_flashing = false
	
	match state:
		AIState.WANDERING:
			handle_wandering(delta)
		AIState.FLEEING:
			handle_fleeing(delta)
		AIState.DEAD:
			handle_death(delta)
	
	if velocity.length() > 0.1 and state != AIState.DEAD:
		leg_phase += delta * velocity.length() * 2.5
		animate_limbs(leg_phase)
	else:
		animate_limbs(0.0)

func handle_wandering(delta: float):
	var direction = (wander_target - global_position).normalized()
	direction.y = 0
	var distance = global_position.distance_to(wander_target)
	if distance < 0.8:
		pick_new_wander_target()
		return
	velocity = direction * wander_speed
	move_and_slide()
	if velocity.length() > 0.1:
		var target_rot = atan2(direction.x, direction.z)
		rotation.y = lerp_angle(rotation.y, target_rot, delta * 4.0)
	wander_timer -= delta
	if wander_timer <= 0:
		pick_new_wander_target()
	if player_ref:
		var dist = global_position.distance_to(player_ref.global_position)
		if dist < detection_range:
			state = AIState.FLEEING

func handle_fleeing(delta: float):
	if not player_ref:
		state = AIState.WANDERING
		return
	var flee_dir = (global_position - player_ref.global_position).normalized()
	flee_dir.y = 0
	if flee_dir.length() < 0.1:
		flee_dir = Vector3(0,0,1)
	velocity = flee_dir * flee_speed
	move_and_slide()
	if velocity.length() > 0.1:
		var target_rot = atan2(flee_dir.x, flee_dir.z)
		rotation.y = lerp_angle(rotation.y, target_rot, delta * 5.0)
	if player_ref:
		var dist = global_position.distance_to(player_ref.global_position)
		if dist > detection_range * 1.8:
			state = AIState.WANDERING
			pick_new_wander_target()

func handle_death(delta: float):
	death_timer += delta
	rotation.x = lerp_angle(rotation.x, deg_to_rad(-90.0), delta * 3.0)
	position.y = original_position.y - 0.3
	if death_timer > 2.0:
		queue_free()

func animate_limbs(phase: float):
	var swing = sin(phase) * 0.3
	if left_leg: left_leg.rotation.x = swing
	if right_leg: right_leg.rotation.x = -swing
	if left_arm: left_arm.rotation.x = -swing * 0.5
	if right_arm: right_arm.rotation.x = swing * 0.5

func pick_new_wander_target():
	var range_ = 6.0
	wander_target = global_position + Vector3(randf_range(-range_, range_), 0, randf_range(-range_, range_))
	wander_timer = randf_range(3.0, 8.0)

func set_body_color(color: Color):
	body_material.albedo_color = color
	for node in [torso, head, left_arm, right_arm, left_leg, right_leg]:
		if node:
			node.material_override = body_material

func take_damage(amount: int):
	if is_dead:
		return
	health -= amount
	is_flashing = true
	hit_flash_timer = 0.15
	set_body_color(Color(1,0.2,0.2))
	SoundManager.play_hit()
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
	SoundManager.play_block_break()

func spawn_drop_item():
	var drop = MeshInstance3D.new()
	var box = BoxMesh.new()
	box.size = Vector3(0.3, 0.3, 0.3)
	drop.mesh = box
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(0.9, 0.8, 0.5)
	mat.roughness = 0.6
	drop.material_override = mat
	drop.position = global_position + Vector3(0, 0.5, 0)
	get_parent().add_child(drop)

func lerp_angle(from: float, to: float, weight: float) -> float:
	var diff = to - from
	while diff > PI: diff -= TAU
	while diff < -PI: diff += TAU
	return from + diff * weight
