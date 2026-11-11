extends CharacterBody2D
class_name BossBase

# Evergreen: After the Fall - Boss AI Architecture (e.g. The Warden)
# Implements multi-phase transitions, telegraphed AoE ground slams, enrage states, and guaranteed quest key drops

signal boss_phase_changed(new_phase: int)
signal boss_defeated(boss_id: String)

enum BossState { IDLE, CHASE, ATTACK_MELEE, TELEGRAPH_SLAM, EXECUTE_SLAM, RECOVER, HURT, DEAD }

@export var boss_id: String = "boss_warden"
@export var boss_name: String = "The Warden"
@export var max_health: float = 250.0
@export var current_health: float = 250.0
@export var phase_1_speed: float = 58.0
@export var phase_2_speed: float = 92.0
@export var melee_damage: float = 28.0
@export var slam_damage: float = 38.0
@export var slam_radius: float = 64.0

var current_state: BossState = BossState.IDLE
var current_phase: int = 1
var target_player: CharacterBody2D = null

var state_timer: float = 0.0
var attack_cooldown: float = 0.0
var flash_timer: float = 0.0
var facing_dir: Vector2 = Vector2.DOWN
var slam_cooldown: float = 5.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Hurtbox = $Hurtbox
@onready var hitbox: Hitbox = $Hitbox
@onready var shockwave_area: Area2D = $ShockwaveArea

func _ready() -> void:
	add_to_group("enemies")
	add_to_group("bosses")
	current_health = max_health
	
	if hurtbox:
		hurtbox.hit_received.connect(_on_hurtbox_hit_received)
	
	if hitbox:
		hitbox.attacker = self
		hitbox.damage = melee_damage
		hitbox.monitoring = false
	
	if shockwave_area:
		shockwave_area.monitoring = false

func _physics_process(delta: float) -> void:
	if current_state == BossState.DEAD:
		return
	
	_handle_flash(delta)
	_update_target()
	_update_timers(delta)
	_run_state_machine(delta)
	_update_animation(delta)

func _handle_flash(delta: float) -> void:
	if flash_timer > 0.0:
		flash_timer -= delta
		if flash_timer <= 0.0:
			if current_phase == 2:
				modulate = Color(1.8, 0.7, 0.7) # Persistent enraged tint
			else:
				modulate = Color(1.0, 1.0, 1.0)

func _update_target() -> void:
	if target_player == null or not is_instance_valid(target_player):
		var players = get_tree().get_nodes_in_group("player")
		if not players.is_empty():
			target_player = players[0]

func _update_timers(delta: float) -> void:
	if attack_cooldown > 0.0:
		attack_cooldown -= delta
	if slam_cooldown > 0.0:
		slam_cooldown -= delta

func _run_state_machine(delta: float) -> void:
	var move_spd = phase_2_speed if current_phase == 2 else phase_1_speed
	
	match current_state:
		BossState.IDLE:
			velocity = velocity.move_toward(Vector2.ZERO, 300.0 * delta)
			if target_player != null and is_instance_valid(target_player):
				current_state = BossState.CHASE
			move_and_slide()
			
		BossState.CHASE:
			if target_player != null and is_instance_valid(target_player):
				var to_player = target_player.global_position - global_position
				var dist = to_player.length()
				facing_dir = to_player.normalized()
				
				# Phase 2 ground slam trigger
				if current_phase == 2 and slam_cooldown <= 0.0 and dist <= (slam_radius * 1.2):
					_start_ground_slam()
				elif dist <= 32.0 and attack_cooldown <= 0.0:
					_start_melee_attack()
				else:
					velocity = facing_dir * move_spd
					move_and_slide()
			else:
				current_state = BossState.IDLE
				
		BossState.ATTACK_MELEE:
			state_timer -= delta
			if state_timer <= 0.2 and hitbox and not hitbox.monitoring:
				hitbox.monitoring = true
				hitbox.position = facing_dir * 18.0
			elif state_timer <= 0.0:
				if hitbox:
					hitbox.monitoring = false
				current_state = BossState.RECOVER
				state_timer = 0.4
				attack_cooldown = 1.0 if current_phase == 2 else 1.6
			move_and_slide()
			
		BossState.TELEGRAPH_SLAM:
			velocity = Vector2.ZERO
			state_timer -= delta
			# Visual pulsing telegraph
			modulate = Color(2.5, 0.3, 0.3) if fmod(state_timer, 0.2) < 0.1 else Color(1.2, 0.2, 0.2)
			if state_timer <= 0.0:
				_execute_ground_slam()
			move_and_slide()
			
		BossState.EXECUTE_SLAM:
			state_timer -= delta
			if state_timer <= 0.0:
				if shockwave_area:
					shockwave_area.monitoring = false
				current_state = BossState.RECOVER
				state_timer = 0.8 # Vulnerable recovery after huge slam
				slam_cooldown = 6.0
				modulate = Color(1.8, 0.7, 0.7) if current_phase == 2 else Color(1.0, 1.0, 1.0)
			move_and_slide()
			
		BossState.RECOVER:
			velocity = velocity.move_toward(Vector2.ZERO, 350.0 * delta)
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = BossState.CHASE
			move_and_slide()
			
		BossState.HURT:
			state_timer -= delta
			if state_timer <= 0.0:
				current_state = BossState.CHASE
			move_and_slide()

func _start_melee_attack() -> void:
	current_state = BossState.ATTACK_MELEE
	state_timer = 0.4
	velocity = facing_dir * (phase_1_speed * 0.5)

func _start_ground_slam() -> void:
	current_state = BossState.TELEGRAPH_SLAM
	state_timer = 0.75 # 0.75s warning telegraph for player to dodge roll
	velocity = Vector2.ZERO
	EventBus.notification_requested.emit("WARNING: %s prepares Ground Slam!" % boss_name, 1.5)

func _execute_ground_slam() -> void:
	current_state = BossState.EXECUTE_SLAM
	state_timer = 0.35
	if shockwave_area:
		shockwave_area.monitoring = true
		# Apply damage to any overlapping player hurtboxes in range
		var overlapping = shockwave_area.get_overlapping_areas()
		for area in overlapping:
			if area is Hurtbox and area.get_parent().is_in_group("player"):
				var push_dir = (area.global_position - global_position).normalized()
				area.take_hit(slam_damage, push_dir * 180.0, self)

func _on_hurtbox_hit_received(damage: float, knockback: Vector2, _attacker: Node2D) -> void:
	# Boss has heavy poise: only receives 25% knockback
	velocity = knockback * 0.25
	current_health -= damage
	modulate = Color(2.0, 0.3, 0.3)
	flash_timer = 0.15
	
	# Check Phase 2 transition
	if current_phase == 1 and current_health <= (max_health * 0.5):
		current_phase = 2
		boss_phase_changed.emit(current_phase)
		EventBus.notification_requested.emit("ENRAGED: %s enters Phase 2!" % boss_name, 3.0)
		modulate = Color(2.0, 0.5, 0.5)
	
	if current_health <= 0.0:
		_die()
	else:
		if current_state != BossState.TELEGRAPH_SLAM and current_state != BossState.EXECUTE_SLAM:
			current_state = BossState.HURT
			state_timer = 0.15

func _die() -> void:
	current_state = BossState.DEAD
	velocity = Vector2.ZERO
	if hurtbox:
		hurtbox.set_deferred("monitoring", false)
		hurtbox.set_deferred("monitorable", false)
	if hitbox:
		hitbox.set_deferred("monitoring", false)
	if shockwave_area:
		shockwave_area.set_deferred("monitoring", false)
	
	# Drop Research Keycard and set narrative flag
	InventoryService.add_item("quest_item_research_key", 1)
	QuestService.story_flags["research_data_secured"] = true
	
	boss_defeated.emit(boss_id)
	EventBus.notification_requested.emit("BOSS DEFEATED: %s! Acquired E.V.E.R. Research Keycard." % boss_name, 4.0)
	
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 1.2)
	tween.tween_callback(queue_free)

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
		BossState.IDLE:
			sprite.frame = base_frame
		BossState.CHASE:
			sprite.frame = base_frame + 2
		BossState.ATTACK_MELEE:
			sprite.frame = base_frame + 4
		BossState.TELEGRAPH_SLAM, BossState.EXECUTE_SLAM:
			sprite.frame = base_frame + 4
		BossState.HURT:
			sprite.frame = base_frame + 5
		BossState.DEAD:
			sprite.frame = base_frame + 5
