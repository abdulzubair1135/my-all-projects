class_name Player
extends CharacterBody3D

# Camera system
@export var first_person_camera: Camera3D
@export var third_person_camera: Camera3D
@export var front_camera: Camera3D
@export var camera_target: Node3D
var camera_view: int = 0

# Movement
@export var walk_speed: float = 4.5
@export var sprint_speed: float = 7.5
@export var jump_velocity: float = 5.0
@export var gravity: float = 16.0
var crouch_height: float = 0.8
var normal_height: float = 2.0
var is_crouching: bool = false

# Mouse look
var mouse_sensitivity: float = 0.002
var mouse_captured: bool = false

# Stats
var health: int = 20
var max_health: int = 20
var hunger: int = 20
var max_hunger: int = 20
var level: int = 1
var xp: int = 0
var xp_to_next_level: int = 100

# Inventory & Block selection
var inventory = []  # Array of 36 slots: {block: int, count: int}
var hotbar_slots: int = 9
var selected_slot: int = 0
var inventory_open: bool = false
var block_ray_distance: float = 6.0
var build_mode: bool = true
var current_block_type: int = 1
var attack_timer: float = 0.0
var attack_cooldown: float = 0.25
var arm_pivot: Node3D = null
var arm_mesh: MeshInstance3D = null
var player_material: StandardMaterial3D

# Character customization
var character_name: String = "Explorer"
var character_color: Color = Color(0.08, 0.08, 0.12)
var character_skin_color: Color = Color(0.25, 0.2, 0.18)
var character_eye_color: Color = Color(0.3, 0.6, 0.9)
var character_hair_color: Color = Color(0.15, 0.1, 0.05)
var character_outfit_color: Color = Color(0.15, 0.2, 0.3)
var character_accessory: String = "none"
var character_gender: String = "neutral"

# Character mesh parts
var body_mesh: MeshInstance3D
var head_mesh: MeshInstance3D
var eye_left_mesh: MeshInstance3D
var eye_right_mesh: MeshInstance3D
var hair_mesh: MeshInstance3D
var outfit_mesh: MeshInstance3D
var accessory_mesh: MeshInstance3D
var hat_mesh: MeshInstance3D

# Hunger timer
var hunger_timer: float = 0.0
var hunger_interval: float = 30.0

# Third person smooth camera
var camera_smooth_speed: float = 5.0
var camera_target_position: Vector3
var camera_target_rotation: Quaternion

# Chest interaction
var open_chest_pos: Vector3 = Vector3.ZERO
var open_chest_inventory: Array = []

# Pickup area
var pickup_area: Area3D

func _ready():
	_ensure_input_map()
	apply_player_theme()
	build_character_model()

	if !first_person_camera:
		first_person_camera = get_node_or_null("FirstPersonCamera")
	if !third_person_camera:
		third_person_camera = get_node_or_null("ThirdPersonCamera")
	if !front_camera:
		var overhead = get_node_or_null("OverheadCamera")
		if overhead:
			front_camera = overhead
			front_camera.name = "FrontCamera"
		else:
			front_camera = Camera3D.new()
			front_camera.name = "FrontCamera"
			front_camera.fov = 65.0
			add_child(front_camera)
	if !camera_target:
		camera_target = get_node_or_null("CameraTarget")

	if third_person_camera:
		third_person_camera.current = false
	if front_camera:
		front_camera.current = false
	if first_person_camera:
		first_person_camera.current = true

	setup_viewmodel_arm()

	var col_shape = get_node_or_null("CollisionShape3D")
	if col_shape:
		var capsule = CapsuleShape3D.new()
		capsule.radius = 0.5
		capsule.height = 1.0
		col_shape.shape = capsule

	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	mouse_captured = false

	# Initialize inventory (36 slots: 0-8 hotbar, 9-35 storage)
	inventory.clear()
	for i in range(36):
		inventory.append({"block": 0, "count": 0})
	# Fill hotbar with default blocks for demonstration (slots 0-8)
	for i in range(9):
		inventory[i] = {"block": i + 1, "count": 64}
	selected_slot = 0
	current_block_type = inventory[0]["block"]

	if has_node("/root/SoundManager"):
		var sm = get_node("/root/SoundManager")
		if sm.has_signal("play_sound"):
			var cb = Callable(self, "_on_sound_played")
			if !sm.is_connected("play_sound", cb):
				sm.connect("play_sound", cb)

	# Setup pickup area
	setup_pickup_area()

	update_ui()

func setup_pickup_area():
	pickup_area = Area3D.new()
	pickup_area.name = "PickupArea"
	var shape = CollisionShape3D.new()
	var sphere = SphereShape3D.new()
	sphere.radius = 1.2
	shape.shape = sphere
	pickup_area.add_child(shape)
	add_child(pickup_area)
	pickup_area.body_entered.connect(_on_pickup_area_entered)

func _on_pickup_area_entered(body):
	if body is DroppedItem:
		# The item's own body_entered will handle pickup, but we can also do it here.
		# We'll let the DroppedItem script handle it to avoid duplication.
		pass

func apply_player_theme():
	player_material = StandardMaterial3D.new()
	player_material.albedo_color = character_color
	player_material.roughness = 0.9
	player_material.metallic = 0.0

func build_character_model():
	body_mesh = MeshInstance3D.new()
	var body_box = BoxMesh.new()
	body_box.size = Vector3(0.8, 0.9, 0.5)
	body_mesh.mesh = body_box
	var body_mat = StandardMaterial3D.new()
	body_mat.albedo_color = character_outfit_color
	body_mat.roughness = 0.8
	body_mesh.material_override = body_mat
	body_mesh.position = Vector3(0, 0.45, 0)
	add_child(body_mesh)
	
	head_mesh = MeshInstance3D.new()
	var head_box = BoxMesh.new()
	head_box.size = Vector3(0.5, 0.5, 0.5)
	head_mesh.mesh = head_box
	var head_mat = StandardMaterial3D.new()
	head_mat.albedo_color = character_skin_color
	head_mat.roughness = 0.7
	head_mesh.material_override = head_mat
	head_mesh.position = Vector3(0, 1.2, 0)
	add_child(head_mesh)
	
	var eye_mat = StandardMaterial3D.new()
	eye_mat.albedo_color = Color(1, 1, 1)
	eye_mat.roughness = 0.1
	
	eye_left_mesh = MeshInstance3D.new()
	var eye_box = BoxMesh.new()
	eye_box.size = Vector3(0.1, 0.08, 0.05)
	eye_left_mesh.mesh = eye_box
	eye_left_mesh.material_override = eye_mat
	eye_left_mesh.position = Vector3(-0.15, 1.25, 0.27)
	add_child(eye_left_mesh)
	
	eye_right_mesh = MeshInstance3D.new()
	eye_right_mesh.mesh = eye_box
	eye_right_mesh.material_override = eye_mat
	eye_right_mesh.position = Vector3(0.15, 1.25, 0.27)
	add_child(eye_right_mesh)
	
	var pupil_mat = StandardMaterial3D.new()
	pupil_mat.albedo_color = character_eye_color
	pupil_mat.roughness = 0.1
	
	var pupil_left = MeshInstance3D.new()
	var pupil_box = BoxMesh.new()
	pupil_box.size = Vector3(0.04, 0.04, 0.02)
	pupil_left.mesh = pupil_box
	pupil_left.material_override = pupil_mat
	pupil_left.position = Vector3(-0.15, 1.25, 0.29)
	add_child(pupil_left)
	
	var pupil_right = MeshInstance3D.new()
	pupil_right.mesh = pupil_box
	pupil_right.material_override = pupil_mat
	pupil_right.position = Vector3(0.15, 1.25, 0.29)
	add_child(pupil_right)
	
	hair_mesh = MeshInstance3D.new()
	var hair_box = BoxMesh.new()
	hair_box.size = Vector3(0.6, 0.15, 0.55)
	hair_mesh.mesh = hair_box
	var hair_mat = StandardMaterial3D.new()
	hair_mat.albedo_color = character_hair_color
	hair_mat.roughness = 0.9
	hair_mesh.material_override = hair_mat
	hair_mesh.position = Vector3(0, 1.4, 0)
	add_child(hair_mesh)
	
	hat_mesh = MeshInstance3D.new()
	var hat_box = BoxMesh.new()
	hat_box.size = Vector3(0.6, 0.15, 0.7)
	hat_mesh.mesh = hat_box
	var hat_mat = StandardMaterial3D.new()
	hat_mat.albedo_color = Color(0.3, 0.2, 0.1)
	hat_mat.roughness = 0.7
	hat_mesh.material_override = hat_mat
	hat_mesh.position = Vector3(0, 1.55, 0.05)
	hat_mesh.visible = false
	add_child(hat_mesh)

func set_character_color(color_name: String):
	match color_name:
		"default":
			character_color = Color(0.08, 0.08, 0.12)
			character_skin_color = Color(0.25, 0.2, 0.18)
			character_eye_color = Color(0.3, 0.6, 0.9)
			character_hair_color = Color(0.15, 0.1, 0.05)
			character_outfit_color = Color(0.15, 0.2, 0.3)
		"light":
			character_color = Color(0.6, 0.5, 0.4)
			character_skin_color = Color(0.85, 0.75, 0.65)
			character_eye_color = Color(0.2, 0.5, 0.8)
			character_hair_color = Color(0.7, 0.6, 0.4)
			character_outfit_color = Color(0.4, 0.5, 0.6)
		"dark":
			character_color = Color(0.02, 0.02, 0.04)
			character_skin_color = Color(0.12, 0.1, 0.08)
			character_eye_color = Color(0.6, 0.8, 1.0)
			character_hair_color = Color(0.05, 0.03, 0.02)
			character_outfit_color = Color(0.08, 0.1, 0.15)
		"red":
			character_color = Color(0.3, 0.05, 0.05)
			character_skin_color = Color(0.3, 0.18, 0.15)
			character_eye_color = Color(0.8, 0.2, 0.2)
			character_hair_color = Color(0.4, 0.1, 0.05)
			character_outfit_color = Color(0.5, 0.1, 0.1)
		"blue":
			character_color = Color(0.05, 0.05, 0.3)
			character_skin_color = Color(0.22, 0.2, 0.25)
			character_eye_color = Color(0.2, 0.4, 0.9)
			character_hair_color = Color(0.1, 0.1, 0.3)
			character_outfit_color = Color(0.1, 0.2, 0.5)
		"green":
			character_color = Color(0.05, 0.2, 0.05)
			character_skin_color = Color(0.2, 0.25, 0.18)
			character_eye_color = Color(0.3, 0.8, 0.3)
			character_hair_color = Color(0.1, 0.2, 0.05)
			character_outfit_color = Color(0.1, 0.4, 0.1)
	rebuild_character_colors()

func rebuild_character_colors():
	if body_mesh and body_mesh.material_override:
		body_mesh.material_override.albedo_color = character_outfit_color
	if head_mesh and head_mesh.material_override:
		head_mesh.material_override.albedo_color = character_skin_color
	if hair_mesh and hair_mesh.material_override:
		hair_mesh.material_override.albedo_color = character_hair_color
	
	var pupils = get_children()
	for child in pupils:
		if child is MeshInstance3D and child.mesh is BoxMesh:
			if child.position.x == -0.15 and child.position.z == 0.29:
				child.material_override.albedo_color = character_eye_color
			if child.position.x == 0.15 and child.position.z == 0.29:
				child.material_override.albedo_color = character_eye_color
	
	if player_material:
		player_material.albedo_color = character_color

func set_accessory(accessory_type: String):
	character_accessory = accessory_type
	if hat_mesh:
		hat_mesh.visible = (accessory_type == "hat")

func is_menu_active() -> bool:
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui:
		var start_menu = ui.get_node_or_null("StartMenu")
		if start_menu and start_menu.visible:
			return true
		var pause_menu = ui.get_node_or_null("PauseMenu")
		if pause_menu and pause_menu.visible:
			return true
		var quit_menu = ui.get_node_or_null("QuitMenu")
		if quit_menu and quit_menu.visible:
			return true
		# Check inventory and chest panels
		if ui.inventory_panel and ui.inventory_panel.visible:
			return true
		if ui.chest_panel and ui.chest_panel.visible:
			return true
	return false

func _ensure_input_map():
	var key_actions = {
		"move_forward": KEY_W,
		"move_back": KEY_S,
		"move_left": KEY_A,
		"move_right": KEY_D,
		"jump": KEY_SPACE,
		"sprint": KEY_SHIFT,
		"crouch": KEY_CTRL,
		"inventory": KEY_E,
		"auto_build": KEY_B,
		"plant_tree": KEY_T,
		"slot_1": KEY_1,
		"slot_2": KEY_2,
		"slot_3": KEY_3,
		"slot_4": KEY_4,
		"slot_5": KEY_5,
		"slot_6": KEY_6,
		"slot_7": KEY_7,
		"slot_8": KEY_8,
		"slot_9": KEY_9,
		"toggle_camera": KEY_F1,
		"camera_view_1": KEY_F2,
		"camera_view_2": KEY_F3,
		"camera_view_3": KEY_F4
	}
	for act in key_actions:
		if not InputMap.has_action(act):
			InputMap.add_action(act)
			var ev = InputEventKey.new()
			ev.physical_keycode = key_actions[act]
			InputMap.action_add_event(act, ev)

	var mouse_actions = {
		"break_block": MOUSE_BUTTON_LEFT,
		"place_block": MOUSE_BUTTON_RIGHT
	}
	for m_act in mouse_actions:
		if not InputMap.has_action(m_act):
			InputMap.add_action(m_act)
			var mev = InputEventMouseButton.new()
			mev.button_index = mouse_actions[m_act]
			InputMap.action_add_event(m_act, mev)

func setup_viewmodel_arm():
	if first_person_camera and !first_person_camera.has_node("ArmPivot"):
		arm_pivot = Node3D.new()
		arm_pivot.name = "ArmPivot"
		arm_pivot.position = Vector3(0.35, -0.35, -0.55)
		first_person_camera.add_child(arm_pivot)

		arm_mesh = MeshInstance3D.new()
		var box = BoxMesh.new()
		box.size = Vector3(0.18, 0.45, 0.18)
		arm_mesh.mesh = box
		arm_mesh.position = Vector3(0, -0.1, 0)
		arm_mesh.rotation_degrees = Vector3(-45, 20, 0)

		var mat = StandardMaterial3D.new()
		mat.albedo_color = character_skin_color
		mat.roughness = 0.9
		arm_mesh.material_override = mat
		arm_pivot.add_child(arm_mesh)

func play_swing_animation():
	if arm_pivot and camera_view == 0:
		var tween = create_tween()
		tween.tween_property(arm_pivot, "rotation_degrees:x", -40.0, 0.08)
		tween.tween_property(arm_pivot, "rotation_degrees:x", 0.0, 0.14)

func _physics_process(delta: float):
	if is_menu_active():
		velocity = Vector3.ZERO
		return

	handle_movement(delta)
	handle_camera_toggle()
	handle_crouch()
	handle_inventory_toggle()
	handle_special_shortcuts()
	handle_block_actions(delta)
	handle_slot_selection()
	handle_hunger(delta)

	if attack_timer > 0.0:
		attack_timer -= delta

	var wg = get_node_or_null("/root/Main/WorldGenerator")
	if !wg and has_node("/root/WorldGenerator"):
		wg = get_node("/root/WorldGenerator")
	if wg:
		wg.update_player_position(global_position)

	if camera_view == 1 and third_person_camera:
		update_third_person_camera(delta, false)
	elif camera_view == 2 and front_camera:
		update_third_person_camera(delta, true)

func update_third_person_camera(delta: float, is_front: bool):
	var target = camera_target if camera_target else self
	var offset = Vector3(0, 2.5, 4.0) if !is_front else Vector3(0, 2.5, -4.0)
	var player_basis = global_transform.basis
	var desired_pos = global_position + player_basis * offset
	var desired_look = target.global_position

	var cam = front_camera if is_front else third_person_camera
	if cam:
		cam.global_position = cam.global_position.lerp(desired_pos, delta * camera_smooth_speed)
		var look_dir = (desired_look - cam.global_position).normalized()
		var target_basis = Basis.looking_at(look_dir, Vector3.UP)
		var target_rot = target_basis.get_rotation_quaternion()
		var current_rot = cam.global_transform.basis.get_rotation_quaternion()
		var new_rot = current_rot.slerp(target_rot, delta * camera_smooth_speed)
		cam.global_transform.basis = Basis(new_rot)

func handle_movement(delta: float):
	var input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var cam = get_active_camera()
	var forward = -cam.global_transform.basis.z if cam else -transform.basis.z
	var right = cam.global_transform.basis.x if cam else transform.basis.x

	forward.y = 0.0
	right.y = 0.0
	forward = forward.normalized()
	right = right.normalized()

	var direction = (forward * -input_dir.y + right * input_dir.x).normalized()

	var speed = walk_speed
	if Input.is_action_pressed("sprint") and !is_crouching:
		speed = sprint_speed

	if is_crouching:
		speed *= 0.5

	if not is_on_floor():
		velocity.y -= gravity * delta

	if Input.is_action_just_pressed("jump") and is_on_floor() and !is_crouching:
		velocity.y = jump_velocity
		if has_node("/root/SoundManager"):
			var sm = get_node("/root/SoundManager")
			if sm.has_method("play_jump"):
				sm.play_jump()

	if direction != Vector3.ZERO:
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed
	else:
		velocity.x = move_toward(velocity.x, 0.0, speed * 0.15)
		velocity.z = move_toward(velocity.z, 0.0, speed * 0.15)

	move_and_slide()

	if velocity.length() > 0.5 and is_on_floor():
		if Engine.get_physics_frames() % 20 == 0:
			if has_node("/root/SoundManager"):
				var sm = get_node("/root/SoundManager")
				if sm.has_method("play_footstep"):
					sm.play_footstep()

func get_active_camera() -> Camera3D:
	if camera_view == 0:
		return first_person_camera
	elif camera_view == 1:
		return third_person_camera
	else:
		return front_camera

func handle_hunger(delta: float):
	hunger_timer += delta
	if hunger_timer >= hunger_interval:
		hunger_timer = 0.0
		hunger = max(0, hunger - 1)
		if hunger <= 0:
			take_damage(1)
		update_ui()

func handle_camera_toggle():
	if Input.is_action_just_pressed("toggle_camera") or Input.is_key_pressed(KEY_F1):
		cycle_camera()
	
	if Input.is_action_just_pressed("camera_view_1") or Input.is_key_pressed(KEY_F2):
		set_camera_view(0)
	if Input.is_action_just_pressed("camera_view_2") or Input.is_key_pressed(KEY_F3):
		set_camera_view(1)
	if Input.is_action_just_pressed("camera_view_3") or Input.is_key_pressed(KEY_F4):
		set_camera_view(2)

func cycle_camera():
	camera_view = (camera_view + 1) % 3
	set_camera_view(camera_view)

func set_camera_view(view: int):
	camera_view = view
	
	if first_person_camera:
		first_person_camera.current = (view == 0)
	if third_person_camera:
		third_person_camera.current = (view == 1)
	if front_camera:
		front_camera.current = (view == 2)
	
	if arm_pivot:
		arm_pivot.visible = (view == 0)
	
	update_ui_camera_label()

func update_ui_camera_label():
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui and ui.has_method("set_camera_view_label"):
		var view_names = ["First Person", "Third Person Back", "Third Person Front"]
		ui.set_camera_view_label(view_names[camera_view])

func toggle_camera():
	cycle_camera()

func handle_crouch():
	if Input.is_action_just_pressed("crouch"):
		is_crouching = !is_crouching
		var target_scale = Vector3(1.0, crouch_height / normal_height, 1.0) if is_crouching else Vector3.ONE
		var tween = create_tween()
		tween.tween_property(self, "scale", target_scale, 0.2)

func handle_inventory_toggle():
	if Input.is_action_just_pressed("inventory") or Input.is_key_pressed(KEY_E):
		# Close any open chest first
		if open_chest_pos != Vector3.ZERO:
			close_chest()
		else:
			toggle_inventory()

func toggle_inventory():
	inventory_open = !inventory_open
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui and ui.has_method("toggle_inventory_panel"):
		ui.toggle_inventory_panel(inventory_open)
	if inventory_open:
		Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
		mouse_captured = false
	else:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
		mouse_captured = true

func open_chest(pos: Vector3, inventory_data: Array):
	open_chest_pos = pos
	open_chest_inventory = inventory_data
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui and ui.has_method("open_chest_panel"):
		ui.open_chest_panel(inventory_data)
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	mouse_captured = false

func close_chest():
	# Save chest inventory
	if open_chest_pos != Vector3.ZERO:
		var wg = get_node_or_null("/root/Main/WorldGenerator")
		if !wg and has_node("/root/WorldGenerator"):
			wg = get_node("/root/WorldGenerator")
		if wg:
			wg.set_chest_inventory(open_chest_pos, open_chest_inventory)
	open_chest_pos = Vector3.ZERO
	open_chest_inventory = []
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui and ui.has_method("close_chest_panel"):
		ui.close_chest_panel()
	# If inventory was also open, keep it open; otherwise capture mouse
	if !inventory_open:
		Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
		mouse_captured = true

func handle_special_shortcuts():
	var world_gen = get_node_or_null("/root/Main/WorldGenerator")
	if !world_gen and has_node("/root/WorldGenerator"):
		world_gen = get_node("/root/WorldGenerator")
	if !world_gen:
		return

	if Input.is_action_just_pressed("auto_build") or Input.is_key_pressed(KEY_B):
		world_gen.auto_build_shelter(global_position)
		if has_node("/root/SoundManager"):
			var sm = get_node("/root/SoundManager")
			if sm.has_method("play_place"):
				sm.play_place()

	if Input.is_action_just_pressed("plant_tree") or Input.is_key_pressed(KEY_T):
		var forward = -transform.basis.z * 3.0
		var target_loc = (global_position + forward).floor()
		world_gen.auto_build_tree(target_loc)
		if has_node("/root/SoundManager"):
			var sm = get_node("/root/SoundManager")
			if sm.has_method("play_place"):
				sm.play_place()

func handle_block_actions(_delta: float):
	if inventory_open or !mouse_captured or open_chest_pos != Vector3.ZERO:
		return

	var world_gen = get_node_or_null("/root/Main/WorldGenerator")
	if !world_gen and has_node("/root/WorldGenerator"):
		world_gen = get_node("/root/WorldGenerator")
	if !world_gen:
		return

	var camera = get_active_camera()
	if !camera:
		return

	var space_state = get_world_3d().direct_space_state
	var ray_start = camera.global_position
	var ray_end = ray_start + -camera.global_transform.basis.z * block_ray_distance
	var query = PhysicsRayQueryParameters3D.create(ray_start, ray_end)
	query.exclude = [self]
	query.collision_mask = 1

	var result = space_state.intersect_ray(query)

	if result:
		var hit_pos = result.position
		var hit_normal = result.normal
		var target = result.collider

		# Right-click: place block or open chest
		if Input.is_action_just_pressed("place_block") or Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
			if attack_timer <= 0.0:
				var hit_block_pos = (hit_pos - hit_normal * 0.1).floor()
				var hit_block = world_gen.get_block(hit_block_pos)
				if hit_block == WorldGenerator.BlockType.CHEST:
					# Open chest
					var chest_inv = world_gen.get_chest_inventory(hit_block_pos)
					open_chest(hit_block_pos, chest_inv)
					return
				else:
					play_swing_animation()
					var place_pos = (hit_pos + hit_normal * 0.1).floor()
					var current_block = world_gen.get_block(place_pos)
					if current_block == 0:
						# Use block from hotbar
						var block_to_place = inventory[selected_slot]["block"]
						if block_to_place != 0 and inventory[selected_slot]["count"] > 0:
							world_gen.set_block(place_pos, block_to_place, false)
							# Decrease count
							inventory[selected_slot]["count"] -= 1
							if inventory[selected_slot]["count"] == 0:
								inventory[selected_slot]["block"] = 0
							attack_timer = 0.2
							if has_node("/root/SoundManager"):
								var sm = get_node("/root/SoundManager")
								if sm.has_method("play_place"):
									sm.play_place()
							update_ui()

		# Left-click: break block or attack
		if Input.is_action_just_pressed("break_block") or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
			if attack_timer <= 0.0:
				play_swing_animation()
				if target and target.has_method("take_damage") and target != self:
					target.take_damage(1)
					attack_timer = attack_cooldown
					gain_xp(5)
					if has_node("/root/SoundManager"):
						var sm = get_node("/root/SoundManager")
						if sm.has_method("play_hit"):
							sm.play_hit()
				else:
					var block_pos = (hit_pos - hit_normal * 0.1).floor()
					var block_type = world_gen.get_block(block_pos)
					if block_type != 0:
						# Check if it's a chest, close chest UI if open
						if block_type == WorldGenerator.BlockType.CHEST and open_chest_pos != Vector3.ZERO:
							close_chest()
						world_gen.set_block(block_pos, 0, true)  # spawn drop
						attack_timer = 0.2
						if has_node("/root/SoundManager"):
							var sm = get_node("/root/SoundManager")
							if sm.has_method("play_break"):
								sm.play_break()

func handle_slot_selection():
	for i in range(9):
		if Input.is_action_just_pressed("slot_" + str(i + 1)) or Input.is_key_pressed(KEY_1 + i):
			selected_slot = i
			current_block_type = inventory[i]["block"]
			update_ui()

func _input(event: InputEvent):
	if is_menu_active():
		return

	if event is InputEventMouseMotion and mouse_captured:
		var camera = get_active_camera()
		if camera:
			rotate_y(-event.relative.x * mouse_sensitivity)
			camera.rotate_x(-event.relative.y * mouse_sensitivity)
			camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-89.0), deg_to_rad(89.0))

	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		if open_chest_pos != Vector3.ZERO:
			close_chest()
		elif inventory_open:
			toggle_inventory()
		elif mouse_captured:
			Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
			mouse_captured = false
		else:
			Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
			mouse_captured = true

func take_damage(amount: int):
	health = max(0, health - amount)
	if has_node("/root/SoundManager"):
		var sm = get_node("/root/SoundManager")
		if sm.has_method("play_damage"):
			sm.play_damage()
	update_ui()

	if health <= 0:
		die()

func die():
	health = max_health
	hunger = int(max_hunger / 2.0)
	global_position = Vector3(0, 30, 0)
	update_ui()

func gain_xp(amount: int):
	xp += amount
	while xp >= xp_to_next_level:
		xp -= xp_to_next_level
		level += 1
		xp_to_next_level = int(xp_to_next_level * 1.5)
	update_ui()

func update_ui():
	var ui = get_node_or_null("/root/Main/UI")
	if !ui and has_node("/root/UI"):
		ui = get_node("/root/UI")
	if ui:
		if ui.has_method("update_stats"):
			ui.update_stats(health, max_health, hunger, max_hunger, level, xp, xp_to_next_level)
		if ui.has_method("update_hotbar"):
			ui.update_hotbar(inventory, selected_slot)
		update_ui_camera_label()
		# Update inventory panels if visible
		if ui.inventory_panel and ui.inventory_panel.visible:
			ui.update_inventory_panel(inventory)
		if ui.chest_panel and ui.chest_panel.visible:
			ui.update_chest_panel(open_chest_inventory)

# Inventory management
func add_item(block_type: int, count: int) -> bool:
	# First try to add to existing stacks
	for i in range(inventory.size()):
		if inventory[i]["block"] == block_type and inventory[i]["count"] < 64:
			var space = 64 - inventory[i]["count"]
			var add = min(space, count)
			inventory[i]["count"] += add
			count -= add
			if count == 0:
				update_ui()
				return true
	# If still have items, find empty slot
	for i in range(inventory.size()):
		if inventory[i]["block"] == 0:
			var add = min(64, count)
			inventory[i] = {"block": block_type, "count": add}
			count -= add
			if count == 0:
				update_ui()
				return true
	# If inventory full, drop remaining items on ground?
	if count > 0:
		# Spawn dropped items at player position
		var wg = get_node_or_null("/root/Main/WorldGenerator")
		if !wg and has_node("/root/WorldGenerator"):
			wg = get_node("/root/WorldGenerator")
		if wg:
			wg.spawn_drop_item(global_position, block_type, count)
	update_ui()
	return count == 0

func remove_item(slot: int, count: int) -> bool:
	if slot < 0 or slot >= inventory.size():
		return false
	if inventory[slot]["count"] >= count:
		inventory[slot]["count"] -= count
		if inventory[slot]["count"] == 0:
			inventory[slot]["block"] = 0
		update_ui()
		return true
	return false

func transfer_item(from_slot: int, to_inventory: Array, to_slot: int) -> bool:
	# Transfer from player inventory to another inventory (e.g., chest)
	if from_slot < 0 or from_slot >= inventory.size():
		return false
	if to_slot < 0 or to_slot >= to_inventory.size():
		return false
	var item = inventory[from_slot]
	if item["block"] == 0 or item["count"] == 0:
		return false
	# Check if target slot has same block and space
	if to_inventory[to_slot]["block"] == item["block"] and to_inventory[to_slot]["count"] < 64:
		var space = 64 - to_inventory[to_slot]["count"]
		var move = min(space, item["count"])
		to_inventory[to_slot]["count"] += move
		item["count"] -= move
		if item["count"] == 0:
			item["block"] = 0
		update_ui()
		return true
	elif to_inventory[to_slot]["block"] == 0:
		var move = min(64, item["count"])
		to_inventory[to_slot] = {"block": item["block"], "count": move}
		item["count"] -= move
		if item["count"] == 0:
			item["block"] = 0
		update_ui()
		return true
	return false

func _on_sound_played(_sound_name: String):
	pass
