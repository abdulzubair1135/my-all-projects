class_name PlayerController
extends CharacterBody3D

# Camera modes
enum CameraMode { FIRST_PERSON, THIRD_PERSON_BACK, THIRD_PERSON_FRONT }
var current_camera_mode: CameraMode = CameraMode.FIRST_PERSON

@export var speed: float = 8.0
@export var sprint_speed: float = 13.0
@export var jump_velocity: float = 6.5
@export var mouse_sensitivity: float = 0.003
@export var health: int = 100
@export var max_health: int = 100
@export var hunger: int = 100
@export var max_hunger: int = 100
@export var xp: int = 0
@export var level: int = 1

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 14.0)
var current_selected_block: int = 1
var is_locked: bool = true
var is_crouching: bool = false
var is_sprinting: bool = false
var attack_timer: float = 0.0
var attack_cooldown: float = 0.3

@onready var camera_first = $FirstPersonCamera
@onready var camera_third_back = $ThirdPersonBack
@onready var camera_third_front = $ThirdPersonFront
@onready var raycast = $FirstPersonCamera/RayCast3D
@onready var arm_pivot = $FirstPersonCamera/ArmPivot
@onready var arm_mesh = $FirstPersonCamera/ArmPivot/ArmMesh

signal health_changed(new_health)
signal hunger_changed(new_hunger)
signal xp_changed(new_xp)
signal block_selected(block_id)

func _ready():
	_ensure_input_map()
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
    set_camera_mode(CameraMode.FIRST_PERSON)
    emit_signal("health_changed", health)
    emit_signal("hunger_changed", hunger)
    emit_signal("xp_changed", xp)
    # Set collision height to 2 blocks
    var col = $CollisionShape3D
    if col and col.shape is CapsuleShape3D:
        col.shape.height = 2.0

func _unhandled_input(event):
    if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * mouse_sensitivity)
        # Only rotate active camera (first person) for pitch
        if current_camera_mode == CameraMode.FIRST_PERSON:
            camera_first.rotate_x(-event.relative.y * mouse_sensitivity)
            camera_first.rotation.x = clamp(camera_first.rotation.x, deg_to_rad(-89), deg_to_rad(89))
        # For third person, we rotate the player's head? Actually we keep camera fixed behind.

    if event.is_action_pressed("ui_cancel"):
        if Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
            Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
        else:
            Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

    # Hotbar number keys
    for i in range(1, 10):
        if event is InputEventKey and event.pressed and event.keycode == (KEY_0 + i):
            current_selected_block = i
            emit_signal("block_selected", current_selected_block)

    # Camera switch: F1 -> cycle, F2 -> first, F3 -> third back, F4 -> third front
    if event is InputEventKey:
        if event.pressed:
            match event.keycode:
                KEY_F1:
                    var next = (current_camera_mode + 1) % 3
                    set_camera_mode(next)
                KEY_F2:
                    set_camera_mode(CameraMode.FIRST_PERSON)
                KEY_F3:
                    set_camera_mode(CameraMode.THIRD_PERSON_BACK)
                KEY_F4:
                    set_camera_mode(CameraMode.THIRD_PERSON_FRONT)

func set_camera_mode(mode: CameraMode):
    current_camera_mode = mode
    camera_first.current = (mode == CameraMode.FIRST_PERSON)
    camera_third_back.current = (mode == CameraMode.THIRD_PERSON_BACK)
    camera_third_front.current = (mode == CameraMode.THIRD_PERSON_FRONT)
    # Show arm only in first person
    if arm_pivot:
        arm_pivot.visible = (mode == CameraMode.FIRST_PERSON)

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta

    # Jump
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
        if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_jump()

    # Sprint & Crouch
    is_sprinting = Input.is_key_pressed(KEY_SHIFT) and not is_crouching
    if Input.is_key_pressed(KEY_CTRL):
        is_crouching = true
    else:
        is_crouching = false

    var move_speed = speed
    if is_sprinting:
        move_speed = sprint_speed
    if is_crouching:
        move_speed *= 0.5

    var input_dir = Vector2.ZERO
    if Input.is_action_pressed("move_forward") or Input.is_key_pressed(KEY_W): input_dir.y -= 1
    if Input.is_action_pressed("move_backward") or Input.is_key_pressed(KEY_S): input_dir.y += 1
    if Input.is_action_pressed("move_left") or Input.is_key_pressed(KEY_A): input_dir.x -= 1
    if Input.is_action_pressed("move_right") or Input.is_key_pressed(KEY_D): input_dir.x += 1
    input_dir = input_dir.normalized()

    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    if direction:
        velocity.x = direction.x * move_speed
        velocity.z = direction.z * move_speed
    else:
        velocity.x = move_toward(velocity.x, 0, move_speed)
        velocity.z = move_toward(velocity.z, 0, move_speed)

    move_and_slide()

    # Block interaction (Left Click: Break, Right Click: Place)
    if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and raycast and raycast.is_colliding():
        if attack_timer <= 0:
            var target = raycast.get_collider()
            if target and target.has_method("break_voxel"):
                target.break_voxel(raycast.get_collision_point() - raycast.get_collision_normal() * 0.4)
                if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_break()
                play_swing_animation()
                attack_timer = attack_cooldown

    if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and raycast and raycast.is_colliding():
        if attack_timer <= 0:
            var target = raycast.get_collider()
            if target and target.has_method("place_voxel"):
                target.place_voxel(raycast.get_collision_point() + raycast.get_collision_normal() * 0.4, current_selected_block)
                if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_place()
                play_swing_animation()
                attack_timer = attack_cooldown

    if attack_timer > 0:
        attack_timer -= delta

    # Hunger drain (every 10 seconds)
    if Engine.get_process_frames() % 600 == 0:
        hunger = max(0, hunger - 1)
        if hunger <= 0:
            health = max(0, health - 1)
        emit_signal("hunger_changed", hunger)
        emit_signal("health_changed", health)

func play_swing_animation():
    if arm_pivot:
        var tween = create_tween()
        tween.tween_property(arm_pivot, "rotation_degrees:x", -40.0, 0.08)
        tween.tween_property(arm_pivot, "rotation_degrees:x", 0.0, 0.14)

func take_damage(amount: int):
    health = max(0, health - amount)
    emit_signal("health_changed", health)
    if health <= 0:
        die()

func die():
    health = max_health
    hunger = max_hunger
    global_position = Vector3(0, 20, 0)
    emit_signal("health_changed", health)
    emit_signal("hunger_changed", hunger)

func gain_xp(amount: int):
    xp += amount
    if xp >= 100:
        level += 1
        xp -= 100
    emit_signal("xp_changed", xp)

func _ensure_input_map():
	var actions = {
		"move_forward": KEY_W, "move_back": KEY_S, "move_left": KEY_A, "move_right": KEY_D,
		"jump": KEY_SPACE, "sprint": KEY_SHIFT, "crouch": KEY_CTRL,
		"slot_1": KEY_1, "slot_2": KEY_2, "slot_3": KEY_3, "slot_4": KEY_4,
		"slot_5": KEY_5, "slot_6": KEY_6, "slot_7": KEY_7, "slot_8": KEY_8, "slot_9": KEY_9,
		"toggle_camera": KEY_F1
	}
	for act in actions:
		if not InputMap.has_action(act):
			InputMap.add_action(act)
			var ev = InputEventKey.new()
			ev.physical_keycode = actions[act]
			InputMap.action_add_event(act, ev)

[gd_scene load_steps=5 format=3 uid="uid://playerscene01"]

[ext_resource type="Script" path="res://scripts/Player.gd" id="1_play"]

[sub_resource type="CapsuleShape3D" id="Capsule_1"]
radius = 0.4
height = 1.8

[sub_resource type="BoxMesh" id="BoxMesh_arm"]
size = Vector3(0.15, 0.4, 0.15)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_arm"]
albedo_color = Color(0.85, 0.75, 0.65, 1)
roughness = 0.9

[node name="Player" type="CharacterBody3D" groups=["player"]]
script = ExtResource("1_play")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0.9, 0)
shape = SubResource("Capsule_1")

[node name="FirstPersonCamera" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
current = true

[node name="RayCast3D" type="RayCast3D" parent="FirstPersonCamera"]
target_position = Vector3(0, 0, -5)

[node name="ArmPivot" type="Node3D" parent="FirstPersonCamera"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0.35, -0.35, -0.55)

[node name="ArmMesh" type="MeshInstance3D" parent="FirstPersonCamera/ArmPivot"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -0.1, 0)
mesh = SubResource("BoxMesh_arm")
material_override = SubResource("StandardMaterial3D_arm")

[node name="ThirdPersonBack" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.965926, -0.258819, 0, 0.258819, 0.965926, 0, 2.5, 3.5)
current = false

[node name="ThirdPersonFront" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 0.965926, -0.258819, 0, 0.258819, 0.965926, 0, 2.5, -3.5)
current = false
