extends CharacterBody2D
class_name PlayerController

# Evergreen: After the Fall - Player Controller
# Implements 8-direction top-down motion, sprint, dodge roll, real-time melee combat, hurtboxes, and protagonist switching

enum State { IDLE, WALK, SPRINT, DODGE, ATTACK_LIGHT, ATTACK_HEAVY, HURT }

@export var current_state: State = State.IDLE
@export var facing_direction: Vector2 = Vector2.DOWN

# Internal references
@onready var sprite: Sprite2D = $Sprite2D
@onready var interaction_detector: Area2D = $InteractionDetector
@onready var camera: Camera2D = $Camera2D
@onready var interact_prompt: Node2D = $InteractPrompt
@onready var attack_hitbox: Hitbox = $AttackHitbox
@onready var player_hurtbox: Hurtbox = $PlayerHurtbox

# Movement & animation variables
var input_vector: Vector2 = Vector2.ZERO
var dodge_direction: Vector2 = Vector2.DOWN
var action_timer: float = 0.0

const DODGE_DURATION: float = 0.28
const DODGE_STAMINA_COST: float = 22.0
const SPRINT_STAMINA_DRAIN_PER_SEC: float = 16.0
const ATTACK_LIGHT_STAMINA: float = 8.0
const ATTACK_HEAVY_STAMINA: float = 18.0

# Frame animation tracker
var anim_timer: float = 0.0
var walk_frame_index: int = 0
var flash_timer: float = 0.0
const WALK_FRAME_SPEED: float = 0.12
const IDLE_FRAME_SPEED: float = 0.45

# Active interactable target
var nearby_interactables: Array[Area2D] = []
var active_interactable: Area2D = null

func _ready() -> void:
	add_to_group("player")
	
	# Connect to EventBus signals
	EventBus.protagonist_switched.connect(_on_protagonist_switched)
	
	# Connect interaction detector
	if interaction_detector:
		interaction_detector.area_entered.connect(_on_interaction_area_entered)
		interaction_detector.area_exited.connect(_on_interaction_area_exited)
	
	# Connect combat areas
	if attack_hitbox:
		attack_hitbox.attacker = self
		attack_hitbox.monitoring = false
	
	if player_hurtbox:
		player_hurtbox.hit_received.connect(_on_hurtbox_hit_received)
	
	# Update visual appearance for starting protagonist
	_update_protagonist_appearance()
	
	if interact_prompt:
		interact_prompt.visible = false

func _physics_process(delta: float) -> void:
	_handle_flash(delta)
	_handle_input()
	_update_state(delta)
	_apply_movement(delta)
	_update_animation(delta)
	_update_interact_prompt()

func _handle_flash(delta: float) -> void:
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0:
			modulate = Color(1.0, 1.0, 1.0)

func _handle_input() -> void:
	if current_state == State.DODGE or current_state == State.ATTACK_LIGHT or current_state == State.ATTACK_HEAVY or current_state == State.HURT:
		return # Locked in action frames
	
	# Read movement input
	input_vector = Vector2(
		Input.get_action_strength("move_right") - Input.get_action_strength("move_left"),
		Input.get_action_strength("move_down") - Input.get_action_strength("move_up")
	).normalized()
	
	if input_vector != Vector2.ZERO:
		if abs(input_vector.x) > abs(input_vector.y):
			facing_direction = Vector2(sign(input_vector.x), 0)
		else:
			facing_direction = Vector2(0, sign(input_vector.y))
	
	# Check protagonist switch (safe zones only)
	if Input.is_action_just_pressed("switch_protagonist"):
		GameState.switch_protagonist()
	
	# Check Combat: Light Attack (J / Left click)
	if Input.is_action_just_pressed("attack"):
		_perform_attack(false)
		return
		
	# Check Combat: Heavy Attack (K / Right click)
	if Input.is_action_just_pressed("heavy_attack"):
		_perform_attack(true)
		return
	
	# Check dodge roll (Space)
	if Input.is_action_just_pressed("dodge") and input_vector != Vector2.ZERO:
		if GameState.consume_stamina(DODGE_STAMINA_COST):
			current_state = State.DODGE
			dodge_direction = input_vector
			action_timer = DODGE_DURATION
			EventBus.player_action_performed.emit("dodge")
			return
	
	# Check interaction (E)
	if Input.is_action_just_pressed("interact") and active_interactable != null:
		_trigger_interaction()

func _perform_attack(is_heavy: bool) -> void:
	var stamina_cost = ATTACK_HEAVY_STAMINA if is_heavy else ATTACK_LIGHT_STAMINA
	if not GameState.consume_stamina(stamina_cost):
		return
	
	current_state = State.ATTACK_HEAVY if is_heavy else State.ATTACK_LIGHT
	
	# Danish signature perk: +25% melee damage
	var dmg_mult = 1.25 if GameState.current_protagonist == GameState.PROTAGONIST_DANISH else 1.0
	var base_dmg = 48.0 if is_heavy else 26.0
	var kb_force = 280.0 if is_heavy else 180.0
	
	attack_hitbox.damage = base_dmg * dmg_mult
	attack_hitbox.knockback_force = kb_force
	attack_hitbox.knockback_direction = facing_direction
	attack_hitbox.position = facing_direction * 20.0
	attack_hitbox.monitoring = true
	attack_hitbox.check_overlaps()
	
	# Archi signature perk: faster recovery
	var recovery_mult = 0.75 if GameState.current_protagonist == GameState.PROTAGONIST_ARCHI else 1.0
	action_timer = (0.36 if is_heavy else 0.22) * recovery_mult
	
	# Forward step during swing
	velocity = facing_direction * (80.0 if is_heavy else 50.0)
	EventBus.player_action_performed.emit("attack")

func _update_state(delta: float) -> void:
	var stats = GameState.get_current_stats()
	
	if current_state == State.DODGE:
		action_timer -= delta
		if action_timer <= 0.0:
			current_state = State.IDLE if input_vector == Vector2.ZERO else State.WALK
		return
		
	if current_state == State.ATTACK_LIGHT or current_state == State.ATTACK_HEAVY:
		action_timer -= delta
		if action_timer <= 0.08 and attack_hitbox:
			attack_hitbox.monitoring = false
		if action_timer <= 0.0:
			current_state = State.IDLE if input_vector == Vector2.ZERO else State.WALK
		return
		
	if current_state == State.HURT:
		action_timer -= delta
		if action_timer <= 0.0:
			current_state = State.IDLE if input_vector == Vector2.ZERO else State.WALK
		return
	
	if input_vector == Vector2.ZERO:
		current_state = State.IDLE
		GameState.restore_stamina(stats["stamina_recovery"] * delta)
	else:
		if Input.is_action_pressed("sprint") and stats["stamina"] > 5.0:
			current_state = State.SPRINT
			GameState.consume_stamina(SPRINT_STAMINA_DRAIN_PER_SEC * delta)
		else:
			current_state = State.WALK
			GameState.restore_stamina(stats["stamina_recovery"] * 0.4 * delta)

func _apply_movement(delta: float) -> void:
	var stats = GameState.get_current_stats()
	var target_speed: float = 0.0
	
	match current_state:
		State.IDLE:
			velocity = Vector2.ZERO
		State.WALK:
			target_speed = stats["speed_walk"]
			velocity = input_vector * target_speed
		State.SPRINT:
			target_speed = stats["speed_sprint"]
			velocity = input_vector * target_speed
		State.DODGE:
			target_speed = stats["dodge_speed"]
			velocity = dodge_direction * target_speed
		State.ATTACK_LIGHT, State.ATTACK_HEAVY, State.HURT:
			velocity = velocity.move_toward(Vector2.ZERO, 350.0 * delta)
	
	move_and_slide()

func _on_hurtbox_hit_received(damage: float, knockback: Vector2, _attacker: Node2D) -> void:
	GameState.take_damage(damage)
	velocity = knockback
	modulate = Color(2.0, 0.4, 0.4)
	flash_timer = 0.22
	current_state = State.HURT
	action_timer = 0.2
	EventBus.notification_requested.emit("Struck by infected! Took %.0f damage." % damage, 1.8)

func _update_animation(delta: float) -> void:
	if not sprite:
		return
	
	anim_timer += delta
	var row_idx: int = 0
	if facing_direction.y > 0.5:
		row_idx = 0 # Down
	elif facing_direction.y < -0.5:
		row_idx = 1 # Up
	elif facing_direction.x < -0.5:
		row_idx = 2 # Left
	elif facing_direction.x > 0.5:
		row_idx = 3 # Right
	
	var base_frame: int = row_idx * 6
	
	if current_state == State.IDLE:
		if anim_timer >= IDLE_FRAME_SPEED:
			anim_timer = 0.0
			walk_frame_index = (walk_frame_index + 1) % 2
		sprite.frame = base_frame + walk_frame_index
	elif current_state == State.WALK or current_state == State.SPRINT:
		var speed_mult: float = 1.5 if current_state == State.SPRINT else 1.0
		if anim_timer >= (WALK_FRAME_SPEED / speed_mult):
			anim_timer = 0.0
			walk_frame_index = (walk_frame_index + 1) % 4
		sprite.frame = base_frame + 2 + walk_frame_index
	elif current_state == State.DODGE:
		sprite.frame = base_frame + 4
	elif current_state == State.ATTACK_LIGHT or current_state == State.ATTACK_HEAVY:
		sprite.frame = base_frame + 3 # weapon swing frame
	elif current_state == State.HURT:
		sprite.frame = base_frame + 5 # hurt recoil frame

func _on_protagonist_switched(_new_protagonist: String) -> void:
	_update_protagonist_appearance()

func _update_protagonist_appearance() -> void:
	var stats = GameState.get_current_stats()
	var texture_path: String = stats["sprite_sheet"]
	if ResourceLoader.exists(texture_path):
		var tex = load(texture_path)
		if sprite and tex:
			sprite.texture = tex
			sprite.hframes = 6
			sprite.vframes = 4

func _on_interaction_area_entered(area: Area2D) -> void:
	if area.has_method("get_interaction_info") or area.is_in_group("interactables"):
		if not nearby_interactables.has(area):
			nearby_interactables.append(area)
			_refresh_active_interactable()

func _on_interaction_area_exited(area: Area2D) -> void:
	if nearby_interactables.has(area):
		nearby_interactables.erase(area)
		_refresh_active_interactable()

func _refresh_active_interactable() -> void:
	if nearby_interactables.is_empty():
		active_interactable = null
		EventBus.interaction_cleared.emit(null)
	else:
		var closest: Area2D = null
		var min_dist: float = 999999.0
		for item in nearby_interactables:
			var d = global_position.distance_to(item.global_position)
			if d < min_dist:
				min_dist = d
				closest = item
		active_interactable = closest
		EventBus.interaction_available.emit(active_interactable)

func _update_interact_prompt() -> void:
	if interact_prompt:
		interact_prompt.visible = (active_interactable != null)

func _trigger_interaction() -> void:
	if active_interactable:
		if active_interactable.has_method("interact"):
			active_interactable.interact(self)
		elif active_interactable.get_parent() and active_interactable.get_parent().has_method("interact"):
			active_interactable.get_parent().interact(self)
		EventBus.player_interacted.emit(active_interactable)
