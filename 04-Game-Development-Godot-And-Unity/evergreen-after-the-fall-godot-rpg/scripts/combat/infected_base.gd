extends CharacterBody2D
class_name InfectedBase

# Evergreen: After the Fall - Modular Infected Zombie AI
# Implements vision/hearing perception, FSM (Idle/Patrol/Chase/Attack/Hurt/Dead), attack hitboxes, and loot drops

enum AIState { IDLE, PATROL, CHASE, ATTACK, RECOVER, HURT, DEAD }

@export var archetype: String = "drifter" # "drifter" or "sprinter"
@export var max_health: float = 60.0
@export var current_health: float = 60.0
@export var move_speed: float = 55.0
@export var attack_damage: float = 15.0
@export var vision_range: float = 160.0
@export var hearing_range: float = 220.0
@export var attack_reach: float = 24.0

var current_state: AIState = AIState.IDLE
var target_player: CharacterBody2D = null

# Timers
var state_timer: float = 0.0
var attack_cooldown: float = 0.0
var flash_timer: float = 0.0
var facing_dir: Vector2 = Vector2.DOWN

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var hitbox: Hitbox = $Hitbox
@onready var hitbox_shape: CollisionShape2D = $Hitbox/CollisionShape2D

func _ready() -> void:
	add_to_group("enemies")
	_configure_archetype()
	
	if hurtbox:
		hurtbox.hit_received.connect(_on_hurtbox_hit_received)
	
	if hitbox:
		hitbox.attacker = self
		hitbox.damage = attack_damage
		hitbox.monitoring = false
	
	current_health = max_health

func _configure_archetype() -> void:
	if archetype == "sprinter":
		max_health = 45.0
		move_speed = 135.0
		attack_damage = 22.0
		vision_range = 220.0
		hearing_range = 300.0
		if sprite:
			sprite.texture = load("res://assets/characters/infected/sprinter_spritesheet.png")
	else: # Drifter
		max_health = 65.0
		move_speed = 52.0
		attack_damage = 16.0
		vision_range = 160.0
		hearing_range = 220.0
		if sprite:
			sprite.texture = load("res://assets/characters/infected/drifter_spritesheet.png")

func _physics_process(delta: float) -> void:
	if current_state == AIState.DEAD:
		return
	
	_handle_flash(delta)
	_update_perception()
	_run_state_machine(delta)
	_update_animation(delta)

func _handle_flash(delta: float) -> void:
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0:
			modulate = Color(1.0, 1.0, 1.0)

func _update_perception() -> void:
	if target_player == null or not is_instance_valid(target_player):
		var players = get_tree().get_nodes_in_group("player")
		if not players.is_empty():
			target_player = players[0]
	
	if target_player == null or not is_instance_valid(target_player):
		return
	
	var dist = global_position.distance_to(target_player.global_position)
	
	# Hearing check: player running (sprint) makes noise
	var player_sprinting = (target_player.get("current_state") == target_player.State.SPRINT)
	var audible_range = hearing_range if player_sprinting else (hearing_range * 0.4)
	
	if dist <= audible_range:
		if current_state == AIState.IDLE or current_state == AIState.PATROL:
			current_state = AIState.CHASE
	
	# Vision check
	if dist <= vision_range:
		if current_state == AIState.IDLE or current_state == AIState.PATROL:
			current_state = AIState.CHASE

func _run_state_machine(delta: float) -> void:
	if attack_cooldown > 0.0:
		attack_cooldown -= delta
	
	match current_state:
		AIState.IDLE:
			velocity = velocity.move_toward(Vector2.ZERO, 300.0 * delta)
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = AIState.PATROL
				state_timer = randf_range(2.0, 4.0)
				velocity = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized() * (move_speed * 0.5)
			move_and_slide()
			
		AIState.PATROL:
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = AIState.IDLE
				state_timer = randf_range(1.5, 3.0)
				velocity = Vector2.ZERO
			move_and_slide()
			
		AIState.CHASE:
			if target_player != null and is_instance_valid(target_player):
				var to_player = target_player.global_position - global_position
				var dist = to_player.length()
				facing_dir = to_player.normalized()
				
				if dist <= attack_reach and attack_cooldown <= 0.0:
					_start_attack()
				else:
					velocity = facing_dir * move_speed
					move_and_slide()
			else:
				current_state = AIState.IDLE
				
		AIState.ATTACK:
			state_timer -= delta
			if state_timer <= 0.15 and hitbox and not hitbox.monitoring:
				# Active strike window
				hitbox.monitoring = true
				hitbox.position = facing_dir * 14.0
			elif state_timer <= 0.0:
				if hitbox:
					hitbox.monitoring = false
				current_state = AIState.RECOVER
				state_timer = 0.45
				attack_cooldown = 1.2
			move_and_slide()
			
		AIState.RECOVER:
			velocity = velocity.move_toward(Vector2.ZERO, 400.0 * delta)
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = AIState.CHASE
			move_and_slide()
			
		AIState.HURT:
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = AIState.CHASE
			move_and_slide()

func _start_attack() -> void:
	current_state = AIState.ATTACK
	state_timer = 0.35 # Attack startup + active
	velocity = facing_dir * (move_speed * 0.4) # Small forward lunge

func _on_hurtbox_hit_received(damage: float, knockback: Vector2, _attacker: Node2D) -> void:
	current_health -= damage
	velocity = knockback
	modulate = Color(1.8, 0.4, 0.4)
	flash_timer = 0.18
	
	if current_health <= 0.0:
		_die()
	else:
		current_state = AIState.HURT
		state_timer = 0.22

func _die() -> void:
	current_state = AIState.DEAD
	velocity = Vector2.ZERO
	if hurtbox:
		hurtbox.set_deferred("monitoring", false)
		hurtbox.set_deferred("monitorable", false)
	if hitbox:
		hitbox.set_deferred("monitoring", false)
	
	# Loot drop
	_spawn_loot()
	
	# Fade out
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.6)
	tween.tween_callback(queue_free)

func _spawn_loot() -> void:
	# Random scrap / seed drops
	var drop_candidates = ["mat_wood", "mat_stone", "seed_potato"]
	var chosen = drop_candidates[randi() % drop_candidates.size()]
	InventoryService.add_item(chosen, 1)
	EventBus.notification_requested.emit("Defeated %s! Salvaged 1x %s." % [archetype.capitalize(), chosen], 2.0)

func _update_animation(_delta: float) -> void:
	if not sprite:
		return
	
	var row_idx = 0
	if abs(facing_dir.x) > abs(facing_dir.y):
		row_idx = 2 if facing_dir.x < 0 else 3
	else:
		row_idx = 0 if facing_dir.y > 0 else 1
	
	var base_frame = row_idx * 6
	match current_state:
		AIState.IDLE:
			sprite.frame = base_frame
		AIState.PATROL, AIState.CHASE:
			sprite.frame = base_frame + 2 # walk frame
		AIState.ATTACK:
			sprite.frame = base_frame + 4 # lunging attack frame
		AIState.HURT:
			sprite.frame = base_frame + 5 # hurt stagger frame
		AIState.DEAD:
			sprite.frame = base_frame + 5
