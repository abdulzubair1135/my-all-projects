class_name Player
extends CharacterBody2D

# Signals for UI and external systems
signal health_changed(current_hp: float, max_hp: float)
signal stamina_changed(current_stamina: float, max_stamina: float)
signal state_changed(new_state: State)
signal died

enum State {
	IDLE,
	WALK,
	ATTACK_LIGHT,
	ATTACK_HEAVY,
	DODGE,
	HURT,
	DEAD
}

enum Facing {
	DOWN,
	UP,
	LEFT,
	RIGHT
}

# Stats
@export_group("Stats")
@export var max_health: float = 100.0
@export var current_health: float = 100.0
@export var max_stamina: float = 100.0
@export var current_stamina: float = 100.0
@export var stamina_regen: float = 20.0
@export var sprint_stamina_drain: float = 18.0

@export_group("Movement")
@export var base_speed: float = 85.0
@export var sprint_multiplier: float = 1.45
@export var acceleration: float = 650.0
@export var friction: float = 800.0

# Current status
var current_state: State = State.IDLE
var current_facing: Facing = Facing.DOWN
var is_sprinting: bool = false
var stamina_pause_timer: float = 0.0

# Node references
@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var camera: Camera2D = $Camera2D
@onready var combat_controller: CombatController = $CombatController
@onready var hurtbox: Hurtbox = $Hurtbox

func _ready() -> void:
	_ensure_default_input_actions()
	current_health = max_health
	current_stamina = max_stamina
	health_changed.emit(current_health, max_health)
	stamina_changed.emit(current_stamina, max_stamina)

	if hurtbox and not hurtbox.hit_received.is_connected(_on_hurtbox_hit_received):
		hurtbox.hit_received.connect(_on_hurtbox_hit_received)
	if combat_controller:
		if not combat_controller.combat_state_changed.is_connected(_on_combat_state_changed):
			combat_controller.combat_state_changed.connect(_on_combat_state_changed)
		if not combat_controller.attack_finished.is_connected(_on_combat_action_finished):
			combat_controller.attack_finished.connect(_on_combat_action_finished)
		if not combat_controller.dodge_finished.is_connected(_on_combat_action_finished):
			combat_controller.dodge_finished.connect(_on_combat_action_finished)

	_play_animation("idle_down")

func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		return

	if combat_controller:
		combat_controller.update_combat(delta)

	_handle_stamina(delta)
	_handle_combat_inputs()
	_handle_movement(delta)
	_update_animation()

func _handle_combat_inputs() -> void:
	if not combat_controller:
		return

	# Attack inputs
	if Input.is_action_just_pressed("attack_light"):
		if current_stamina >= combat_controller.light_stamina_cost and combat_controller.can_attack():
			var facing_vec := get_facing_vector()
			if combat_controller.start_light_attack(facing_vec):
				current_stamina = max(0.0, current_stamina - combat_controller.light_stamina_cost)
				stamina_pause_timer = 0.4
				stamina_changed.emit(current_stamina, max_stamina)
				current_state = State.ATTACK_LIGHT
				state_changed.emit(current_state)

	elif Input.is_action_just_pressed("attack_heavy"):
		if current_stamina >= combat_controller.heavy_stamina_cost and combat_controller.can_attack() and combat_controller.heavy_cooldown_timer <= 0.0:
			var facing_vec := get_facing_vector()
			if combat_controller.start_heavy_attack(facing_vec):
				current_stamina = max(0.0, current_stamina - combat_controller.heavy_stamina_cost)
				stamina_pause_timer = 0.7
				stamina_changed.emit(current_stamina, max_stamina)
				current_state = State.ATTACK_HEAVY
				state_changed.emit(current_state)

	# Dodge input
	elif Input.is_action_just_pressed("dodge"):
		if current_stamina >= combat_controller.dodge_stamina_cost and combat_controller.can_dodge():
			var input_vec: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")
			var dodge_dir := input_vec if input_vec.length_squared() > 0.01 else get_facing_vector()
			if combat_controller.start_dodge(dodge_dir):
				current_stamina = max(0.0, current_stamina - combat_controller.dodge_stamina_cost)
				stamina_pause_timer = 0.7
				stamina_changed.emit(current_stamina, max_stamina)
				current_state = State.DODGE
				state_changed.emit(current_state)

func _handle_movement(delta: float) -> void:
	# Combat locking states
	if current_state == State.ATTACK_LIGHT or current_state == State.ATTACK_HEAVY:
		velocity = velocity.move_toward(Vector2.ZERO, friction * 1.5 * delta)
		move_and_slide()
		return

	if current_state == State.DODGE:
		if combat_controller:
			velocity = combat_controller.dodge_direction * combat_controller.dodge_speed
		move_and_slide()
		return

	if current_state == State.HURT:
		if combat_controller:
			velocity = combat_controller.knockback_velocity
		move_and_slide()
		return

	# Normal 8-directional movement
	var input_vector: Vector2 = Input.get_vector("move_left", "move_right", "move_up", "move_down")

	var wants_sprint: bool = Input.is_action_pressed("sprint") and input_vector.length_squared() > 0.01
	is_sprinting = wants_sprint and current_stamina > 2.0

	var target_speed: float = base_speed * (sprint_multiplier if is_sprinting else 1.0)
	var target_velocity: Vector2 = input_vector * target_speed

	if input_vector.length_squared() > 0.01:
		velocity = velocity.move_toward(target_velocity, acceleration * delta)
		current_state = State.WALK
		_update_facing(input_vector)
	else:
		velocity = velocity.move_toward(Vector2.ZERO, friction * delta)
		if velocity.length_squared() < 1.0:
			velocity = Vector2.ZERO
			current_state = State.IDLE

	move_and_slide()

func _update_facing(input_vector: Vector2) -> void:
	if abs(input_vector.x) > abs(input_vector.y):
		current_facing = Facing.RIGHT if input_vector.x > 0 else Facing.LEFT
	else:
		current_facing = Facing.DOWN if input_vector.y > 0 else Facing.UP

func get_facing_vector() -> Vector2:
	match current_facing:
		Facing.DOWN:
			return Vector2(0, 1)
		Facing.UP:
			return Vector2(0, -1)
		Facing.RIGHT:
			return Vector2(1, 0)
		Facing.LEFT:
			return Vector2(-1, 0)
	return Vector2(0, 1)

func _update_animation() -> void:
	if not animated_sprite:
		return

	animated_sprite.flip_h = false  # New atlas: each direction is unique, no flip_h needed

	if current_state == State.DEAD:
		match current_facing:
			Facing.DOWN: _play_animation("death_down")
			Facing.LEFT: _play_animation("death_left")
			Facing.RIGHT: _play_animation("death_right")
			Facing.UP:   _play_animation("death_up")
		return

	if current_state == State.HURT:
		match current_facing:
			Facing.DOWN: _play_animation("hurt_down")
			Facing.LEFT: _play_animation("hurt_left")
			Facing.RIGHT: _play_animation("hurt_right")
			Facing.UP:   _play_animation("hurt_up")
		return

	if current_state == State.DODGE:
		match current_facing:
			Facing.DOWN: _play_animation("dodge_down")
			Facing.LEFT: _play_animation("dodge_left")
			Facing.RIGHT: _play_animation("dodge_right")
			Facing.UP:   _play_animation("dodge_up")
		return

	if current_state == State.ATTACK_LIGHT:
		match current_facing:
			Facing.DOWN: _play_animation("light_attack_down")
			Facing.LEFT: _play_animation("light_attack_left")
			Facing.RIGHT: _play_animation("light_attack_right")
			Facing.UP:   _play_animation("light_attack_up")
		return

	if current_state == State.ATTACK_HEAVY:
		match current_facing:
			Facing.DOWN: _play_animation("heavy_attack_down")
			Facing.LEFT: _play_animation("heavy_attack_left")
			Facing.RIGHT: _play_animation("heavy_attack_right")
			Facing.UP:   _play_animation("heavy_attack_up")
		return

	# Idle and Walk
	var base: String = "idle" if current_state == State.IDLE else "walk"
	match current_facing:
		Facing.DOWN: _play_animation(base + "_down")
		Facing.LEFT: _play_animation(base + "_left")
		Facing.RIGHT: _play_animation(base + "_right")
		Facing.UP:   _play_animation(base + "_up")

func _play_animation(anim: String) -> void:
	if not animated_sprite:
		return
	if animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(anim):
		if animated_sprite.animation != anim:
			animated_sprite.play(anim)

func _handle_stamina(delta: float) -> void:
	if stamina_pause_timer > 0.0:
		stamina_pause_timer = max(0.0, stamina_pause_timer - delta)
		return

	if is_sprinting:
		current_stamina = max(0.0, current_stamina - sprint_stamina_drain * delta)
		stamina_changed.emit(current_stamina, max_stamina)
	elif current_stamina < max_stamina:
		current_stamina = min(max_stamina, current_stamina + stamina_regen * delta)
		stamina_changed.emit(current_stamina, max_stamina)

func take_damage(amount: float) -> void:
	if current_state == State.DEAD:
		return
	current_health = max(0.0, current_health - amount)
	health_changed.emit(current_health, max_health)
	if current_health <= 0.0:
		_die()

func _die() -> void:
	current_state = State.DEAD
	velocity = Vector2.ZERO
	if combat_controller:
		combat_controller.set_dead()
	# Play directional death animation
	var death_anim: String = "death_down"
	match current_facing:
		Facing.LEFT:  death_anim = "death_left"
		Facing.RIGHT: death_anim = "death_right"
		Facing.UP:    death_anim = "death_up"
	_play_animation(death_anim)
	died.emit()
	print("[Player] Fallen to the ruins...")

func _on_hurtbox_hit_received(damage_info: DamageInfo) -> void:
	if current_state == State.DEAD:
		return
	take_damage(damage_info.amount)
	if current_state != State.DEAD:
		current_state = State.HURT
		state_changed.emit(current_state)

func _on_combat_state_changed(c_state: CombatController.CombatState) -> void:
	if c_state == CombatController.CombatState.IDLE and (current_state == State.ATTACK_LIGHT or current_state == State.ATTACK_HEAVY or current_state == State.DODGE or current_state == State.HURT):
		current_state = State.IDLE
		state_changed.emit(current_state)

func _on_combat_action_finished() -> void:
	if current_state != State.DEAD:
		current_state = State.IDLE
		state_changed.emit(current_state)

# Safety helper to ensure input bindings exist even if running in ad-hoc test environments
func _ensure_default_input_actions() -> void:
	var defaults: Dictionary = {
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"move_up": [KEY_W, KEY_UP],
		"move_down": [KEY_S, KEY_DOWN],
		"sprint": [KEY_SHIFT],
		"dodge": [KEY_SPACE],
		"attack_light": [KEY_J],
		"attack_heavy": [KEY_K],
		"interact": [KEY_E]
	}
	for action: String in defaults:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			for keycode: int in defaults[action]:
				var ev := InputEventKey.new()
				ev.physical_keycode = keycode
				InputMap.action_add_event(action, ev)
