class_name BaseEnemy
extends CharacterBody2D

signal died(enemy: BaseEnemy)
signal health_changed(current_hp: float, max_hp: float)
signal state_changed(new_state: State)

enum State {
	IDLE,
	PATROL,
	CHASE,
	ATTACK,
	HURT,
	DEAD
}

@export_group("Identity")
@export var enemy_name: String = "BaseEnemy"

@export_group("Stats")
@export var max_health: float = 100.0
@export var current_health: float = 100.0
@export var move_speed: float = 45.0
@export var patrol_speed_mult: float = 0.5
@export var knockback_resistance: float = 0.0 # 0.0 = full knockback, 0.5 = 50% less

@export_group("Combat")
@export var attack_damage: float = 10.0
@export var attack_knockback: float = 140.0
@export var attack_range: float = 24.0
@export var attack_cooldown: float = 1.2
@export var attack_windup: float = 0.12
@export var attack_duration: float = 0.40
@export var damage_type: String = "zombie_melee"

@export_group("Perception & Patrol")
@export var detection_radius: float = 140.0
@export var lose_target_radius: float = 220.0
@export var patrol_radius: float = 60.0

var current_state: State = State.IDLE
var target_player: CharacterBody2D = null
var spawn_position: Vector2 = Vector2.ZERO
var patrol_target: Vector2 = Vector2.ZERO

var attack_cooldown_timer: float = 0.0
var state_timer: float = 0.0
var idle_wander_timer: float = 2.0
var knockback_velocity: Vector2 = Vector2.ZERO
var knockback_decay: float = 750.0

@onready var animated_sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var attack_hitbox: Hitbox = $AttackHitbox

func _ready() -> void:
	current_health = max_health
	spawn_position = global_position

	if hurtbox and not hurtbox.hit_received.is_connected(_on_hit_received):
		hurtbox.hit_received.connect(_on_hit_received)
	if attack_hitbox:
		attack_hitbox.owner_node = self

	_find_player()
	_play_anim("idle")

func _physics_process(delta: float) -> void:
	if current_state == State.DEAD:
		return

	if attack_cooldown_timer > 0.0:
		attack_cooldown_timer = max(0.0, attack_cooldown_timer - delta)

	# Knockback friction decay
	if knockback_velocity.length_squared() > 1.0:
		knockback_velocity = knockback_velocity.move_toward(Vector2.ZERO, knockback_decay * delta)
	else:
		knockback_velocity = Vector2.ZERO

	match current_state:
		State.IDLE:
			_process_idle(delta)
		State.PATROL:
			_process_patrol(delta)
		State.CHASE:
			_process_chase(delta)
		State.ATTACK:
			_process_attack(delta)
		State.HURT:
			_process_hurt(delta)

func _process_idle(delta: float) -> void:
	velocity = knockback_velocity
	move_and_slide()

	if _check_for_player():
		return

	# Wander timer countdown for territorial patrol
	idle_wander_timer -= delta
	if idle_wander_timer <= 0.0 and patrol_radius > 0.0:
		_start_patrol_wander()

func _process_patrol(delta: float) -> void:
	if _check_for_player():
		return

	var to_target := patrol_target - global_position
	var dist := to_target.length()

	state_timer += delta
	# Reached target or timed out
	if dist < 6.0 or state_timer >= 4.0:
		current_state = State.IDLE
		idle_wander_timer = randf_range(1.5, 3.5)
		velocity = Vector2.ZERO
		_play_anim("idle")
		state_changed.emit(current_state)
		return

	var dir := to_target.normalized()
	velocity = dir * (move_speed * patrol_speed_mult) + knockback_velocity
	_update_facing(dir)
	move_and_slide()

func _process_chase(_delta: float) -> void:
	if not target_player or not is_instance_valid(target_player):
		_find_player()
		if not target_player:
			_return_to_idle()
			return

	var to_player := target_player.global_position - global_position
	var dist := to_player.length()

	# Player escaped
	if dist > lose_target_radius:
		_return_to_idle()
		return

	# Close enough to strike
	if dist <= attack_range and attack_cooldown_timer <= 0.0:
		_start_attack()
		return

	# Move toward player
	var dir := to_player.normalized()
	velocity = dir * move_speed + knockback_velocity
	_update_facing(dir)
	move_and_slide()

func _start_attack() -> void:
	current_state = State.ATTACK
	state_timer = 0.0
	velocity = Vector2.ZERO
	_play_anim("attack")
	state_changed.emit(current_state)

func _process_attack(delta: float) -> void:
	state_timer += delta
	if is_inside_tree() and get_world_2d() and get_world_2d().space != RID():
		velocity = knockback_velocity
		move_and_slide()

	# Active strike window
	var window_end := attack_windup + 0.16
	if state_timer >= attack_windup and state_timer <= window_end:
		if attack_hitbox and not attack_hitbox.is_active:
			var dir := _get_attack_direction()
			var dmg := _create_damage_info(dir)
			attack_hitbox.activate(dmg)
	elif state_timer > window_end:
		if attack_hitbox and attack_hitbox.is_active:
			attack_hitbox.deactivate()

	if state_timer >= attack_duration:
		attack_cooldown_timer = attack_cooldown
		current_state = State.CHASE
		_play_anim("walk")
		state_changed.emit(current_state)

func _process_hurt(delta: float) -> void:
	state_timer += delta
	velocity = knockback_velocity
	move_and_slide()
	if state_timer >= 0.20:
		current_state = State.CHASE
		_play_anim("walk")
		state_changed.emit(current_state)

func _start_patrol_wander() -> void:
	current_state = State.PATROL
	state_timer = 0.0
	var random_offset := Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)).normalized() * randf_range(15.0, patrol_radius)
	patrol_target = spawn_position + random_offset
	_play_anim("walk")
	state_changed.emit(current_state)

func _return_to_idle() -> void:
	current_state = State.IDLE
	idle_wander_timer = randf_range(1.5, 3.0)
	velocity = Vector2.ZERO
	_play_anim("idle")
	state_changed.emit(current_state)

func _check_for_player() -> bool:
	if not target_player or not is_instance_valid(target_player):
		_find_player()
		if not target_player:
			return false

	var dist := global_position.distance_to(target_player.global_position)
	if dist <= detection_radius:
		current_state = State.CHASE
		_play_anim("walk")
		state_changed.emit(current_state)
		return true
	return false

func _on_hit_received(damage_info: DamageInfo) -> void:
	if current_state == State.DEAD:
		return

	current_health = max(0.0, current_health - damage_info.amount)
	health_changed.emit(current_health, max_health)

	var force: float = damage_info.knockback_force * (1.0 - clampf(knockback_resistance, 0.0, 0.95))
	knockback_velocity = damage_info.knockback_direction * force

	_flash_feedback()

	if current_health <= 0.0:
		_die()
	else:
		current_state = State.HURT
		state_timer = 0.0
		if attack_hitbox:
			attack_hitbox.deactivate()
		_play_anim("hurt")
		state_changed.emit(current_state)

func _flash_feedback() -> void:
	if animated_sprite:
		animated_sprite.modulate = Color(2.5, 0.4, 0.4, 1.0)
		var tween := create_tween()
		tween.tween_property(animated_sprite, "modulate", Color(1.0, 1.0, 1.0, 1.0), 0.12)

func _die() -> void:
	current_state = State.DEAD
	velocity = Vector2.ZERO
	if attack_hitbox:
		attack_hitbox.deactivate()
	if hurtbox:
		hurtbox.set_deferred("monitoring", false)
		hurtbox.set_deferred("monitorable", false)
	if collision_shape:
		collision_shape.set_deferred("disabled", true)

	_play_anim("death")
	died.emit(self)
	state_changed.emit(current_state)
	print("[%s] Slain at %s" % [enemy_name, str(global_position)])

func _get_attack_direction() -> Vector2:
	if target_player and is_instance_valid(target_player):
		return (target_player.global_position - global_position).normalized()
	if animated_sprite and animated_sprite.flip_h:
		return Vector2.LEFT
	return Vector2.RIGHT

func _create_damage_info(dir: Vector2) -> DamageInfo:
	return DamageInfo.new(attack_damage, attack_knockback, dir, self, damage_type)

func _update_facing(dir: Vector2) -> void:
	if animated_sprite:
		if dir.x > 0.05:
			animated_sprite.flip_h = false
		elif dir.x < -0.05:
			animated_sprite.flip_h = true

func _play_anim(anim: String) -> void:
	if animated_sprite and animated_sprite.sprite_frames and animated_sprite.sprite_frames.has_animation(anim):
		if animated_sprite.animation != anim:
			animated_sprite.play(anim)

func _find_player() -> void:
	if not is_inside_tree():
		return
	var players := get_tree().get_nodes_in_group("player")
	if players.size() > 0:
		target_player = players[0] as CharacterBody2D
