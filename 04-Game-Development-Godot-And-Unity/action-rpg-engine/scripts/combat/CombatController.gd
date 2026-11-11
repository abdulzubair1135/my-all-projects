class_name CombatController
extends Node

signal combat_state_changed(new_state: CombatState)
signal attack_started(is_heavy: bool)
signal attack_finished
signal dodge_started
signal dodge_finished
signal hit_connected(target: Hurtbox, damage_info: DamageInfo)

enum CombatState {
	IDLE,
	ATTACK_LIGHT,
	ATTACK_HEAVY,
	DODGING,
	HURT,
	DEAD
}

@export var character: CharacterBody2D
@export var hitbox_pivot: Node2D
@export var attack_hitbox: Hitbox
@export var character_hurtbox: Hurtbox

# Attack configurations
@export_group("Light Attack")
@export var light_damage: float = 20.0
@export var light_stamina_cost: float = 12.0
@export var light_knockback: float = 160.0
@export var light_duration: float = 0.25
@export var light_hitbox_start: float = 0.06
@export var light_hitbox_end: float = 0.18

@export_group("Heavy Attack")
@export var heavy_damage: float = 40.0
@export var heavy_stamina_cost: float = 25.0
@export var heavy_knockback: float = 300.0
@export var heavy_duration: float = 0.46
@export var heavy_hitbox_start: float = 0.16
@export var heavy_hitbox_end: float = 0.32
@export var heavy_recovery_delay: float = 0.18

@export_group("Dodge")
@export var dodge_duration: float = 0.25
@export var dodge_iframe_duration: float = 0.20
@export var dodge_stamina_cost: float = 25.0
@export var dodge_cooldown: float = 0.50
@export var dodge_speed: float = 210.0

@export_group("Hit Feedback")
@export var hit_stop_duration: float = 0.04

var current_state: CombatState = CombatState.IDLE
var state_timer: float = 0.0
var dodge_cooldown_timer: float = 0.0
var heavy_cooldown_timer: float = 0.0
var dodge_direction: Vector2 = Vector2.DOWN
var knockback_velocity: Vector2 = Vector2.ZERO
var knockback_decay: float = 850.0

# Hit-stop
var hit_stop_timer: float = 0.0

func _ready() -> void:
	if not character and get_parent() is CharacterBody2D:
		character = get_parent() as CharacterBody2D
	if attack_hitbox:
		attack_hitbox.hit_landed.connect(_on_attack_hit_landed)
	if character_hurtbox:
		character_hurtbox.hit_received.connect(_on_character_hit_received)

func update_combat(delta: float) -> void:
	# Update cooldown timers
	if dodge_cooldown_timer > 0.0:
		dodge_cooldown_timer = max(0.0, dodge_cooldown_timer - delta)
	if heavy_cooldown_timer > 0.0:
		heavy_cooldown_timer = max(0.0, heavy_cooldown_timer - delta)

	# Handle micro hit-stop
	if hit_stop_timer > 0.0:
		hit_stop_timer = max(0.0, hit_stop_timer - delta)

	# Knockback decay
	if knockback_velocity.length_squared() > 1.0:
		knockback_velocity = knockback_velocity.move_toward(Vector2.ZERO, knockback_decay * delta)
	else:
		knockback_velocity = Vector2.ZERO

	# State-specific logic
	match current_state:
		CombatState.ATTACK_LIGHT:
			_process_light_attack(delta)
		CombatState.ATTACK_HEAVY:
			_process_heavy_attack(delta)
		CombatState.DODGING:
			_process_dodge(delta)
		CombatState.HURT:
			_process_hurt(delta)

func can_attack() -> bool:
	return current_state == CombatState.IDLE

func can_dodge() -> bool:
	return (current_state == CombatState.IDLE or current_state == CombatState.ATTACK_LIGHT) \
		and dodge_cooldown_timer <= 0.0

func start_light_attack(facing_dir: Vector2) -> bool:
	if not can_attack():
		return false
	_align_hitbox_to_facing(facing_dir)
	current_state = CombatState.ATTACK_LIGHT
	state_timer = 0.0
	attack_started.emit(false)
	combat_state_changed.emit(current_state)
	return true

func start_heavy_attack(facing_dir: Vector2) -> bool:
	if not can_attack() or heavy_cooldown_timer > 0.0:
		return false
	_align_hitbox_to_facing(facing_dir)
	current_state = CombatState.ATTACK_HEAVY
	state_timer = 0.0
	attack_started.emit(true)
	combat_state_changed.emit(current_state)
	return true

func start_dodge(move_or_facing_dir: Vector2) -> bool:
	if not can_dodge():
		return false
	dodge_direction = move_or_facing_dir.normalized()
	if dodge_direction == Vector2.ZERO:
		dodge_direction = Vector2.DOWN
	current_state = CombatState.DODGING
	state_timer = 0.0
	dodge_cooldown_timer = dodge_cooldown
	if character_hurtbox:
		character_hurtbox.is_invulnerable = true
	if attack_hitbox:
		attack_hitbox.deactivate()
	dodge_started.emit()
	combat_state_changed.emit(current_state)
	return true

func apply_knockback(force: float, dir: Vector2) -> void:
	knockback_velocity = dir.normalized() * force

func trigger_hurt(damage_info: DamageInfo) -> void:
	if current_state == CombatState.DEAD:
		return
	if attack_hitbox:
		attack_hitbox.deactivate()
	if character_hurtbox:
		character_hurtbox.is_invulnerable = false
	current_state = CombatState.HURT
	state_timer = 0.0
	apply_knockback(damage_info.knockback_force, damage_info.knockback_direction)
	combat_state_changed.emit(current_state)

func set_dead() -> void:
	current_state = CombatState.DEAD
	if attack_hitbox:
		attack_hitbox.deactivate()
	if character_hurtbox:
		character_hurtbox.is_invulnerable = true
	knockback_velocity = Vector2.ZERO
	combat_state_changed.emit(current_state)

func _process_light_attack(delta: float) -> void:
	state_timer += delta
	# Activate hitbox during damage window
	if state_timer >= light_hitbox_start and state_timer <= light_hitbox_end:
		if attack_hitbox and not attack_hitbox.is_active:
			var facing_dir := _get_facing_vector()
			var dmg := DamageInfo.new(light_damage, light_knockback, facing_dir, character, "physical")
			attack_hitbox.activate(dmg)
	elif state_timer > light_hitbox_end:
		if attack_hitbox and attack_hitbox.is_active:
			attack_hitbox.deactivate()

	if state_timer >= light_duration:
		_finish_attack()

func _process_heavy_attack(delta: float) -> void:
	state_timer += delta
	if state_timer >= heavy_hitbox_start and state_timer <= heavy_hitbox_end:
		if attack_hitbox and not attack_hitbox.is_active:
			var facing_dir := _get_facing_vector()
			var dmg := DamageInfo.new(heavy_damage, heavy_knockback, facing_dir, character, "heavy_physical")
			attack_hitbox.activate(dmg)
	elif state_timer > heavy_hitbox_end:
		if attack_hitbox and attack_hitbox.is_active:
			attack_hitbox.deactivate()

	if state_timer >= heavy_duration:
		heavy_cooldown_timer = heavy_recovery_delay
		_finish_attack()

func _finish_attack() -> void:
	if attack_hitbox:
		attack_hitbox.deactivate()
	current_state = CombatState.IDLE
	attack_finished.emit()
	combat_state_changed.emit(current_state)

func _process_dodge(delta: float) -> void:
	state_timer += delta
	# i-frames expire slightly before full dodge recovery
	if state_timer >= dodge_iframe_duration:
		if character_hurtbox and character_hurtbox.is_invulnerable:
			character_hurtbox.is_invulnerable = false

	if state_timer >= dodge_duration:
		if character_hurtbox:
			character_hurtbox.is_invulnerable = false
		current_state = CombatState.IDLE
		dodge_finished.emit()
		combat_state_changed.emit(current_state)

func _process_hurt(delta: float) -> void:
	state_timer += delta
	if state_timer >= 0.22:
		current_state = CombatState.IDLE
		combat_state_changed.emit(current_state)

func _align_hitbox_to_facing(dir: Vector2) -> void:
	if not hitbox_pivot:
		return
	if abs(dir.x) > abs(dir.y):
		hitbox_pivot.position = Vector2(16.0 if dir.x > 0 else -16.0, -8.0)
		hitbox_pivot.rotation = 0.0 if dir.x > 0 else PI
	else:
		hitbox_pivot.position = Vector2(0.0, 10.0 if dir.y > 0 else -20.0)
		hitbox_pivot.rotation = PI / 2.0 if dir.y > 0 else -PI / 2.0

func _get_facing_vector() -> Vector2:
	if not hitbox_pivot:
		return Vector2.DOWN
	return Vector2.RIGHT.rotated(hitbox_pivot.rotation)

func _on_attack_hit_landed(target: Hurtbox, damage_info: DamageInfo) -> void:
	hit_stop_timer = hit_stop_duration
	hit_connected.emit(target, damage_info)

func _on_character_hit_received(damage_info: DamageInfo) -> void:
	trigger_hurt(damage_info)
