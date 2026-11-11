extends CharacterBody3D

@export var speed: float = 8.0
@export var sprint_speed: float = 13.0
@export var jump_velocity: float = 6.5
@export var mouse_sensitivity: float = 0.003
@export var health: int = 100
@export var max_health: int = 100

var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity", 14.0)
var current_selected_block: int = 1
var is_locked: bool = true

@onready var camera = $Camera3D
@onready var raycast = $Camera3D/RayCast3D

signal health_changed(new_health)
signal block_selected(block_id)

func _ready():
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
    emit_signal("health_changed", health)

func _unhandled_input(event):
    if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
        rotate_y(-event.relative.x * mouse_sensitivity)
        camera.rotate_x(-event.relative.y * mouse_sensitivity)
        camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-89), deg_to_rad(89))
        
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

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta

    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity
        SoundManager.play_jump()

    var move_speed = sprint_speed if Input.is_key_pressed(KEY_SHIFT) else speed
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
        var target = raycast.get_collider()
        if target and target.has_method("break_voxel"):
            target.break_voxel(raycast.get_collision_point() - raycast.get_collision_normal() * 0.4)
            SoundManager.play_block_break()

    if Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT) and raycast and raycast.is_colliding():
        var target = raycast.get_collider()
        if target and target.has_method("place_voxel"):
            target.place_voxel(raycast.get_collision_point() + raycast.get_collision_normal() * 0.4, current_selected_block)
            SoundManager.play_block_place()
