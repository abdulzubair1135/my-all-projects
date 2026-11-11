class_name WildlifeBase
extends CharacterBody2D

enum State {
	IDLE,
	WANDER,
	FLEE
}

@export var wander_speed: float = 20.0
@export var flee_speed: float = 60.0
@export var detection_radius: float = 75.0

var current_state: State = State.IDLE
var wander_target: Vector2 = Vector2.ZERO
var home_position: Vector2 = Vector2.ZERO
var state_timer: float = 2.0
var player_ref: Player = null

@onready var sprite: Sprite2D = get_node_or_null("Sprite2D")

func _ready() -> void:
	home_position = global_position
	_pick_wander_target()

func _physics_process(delta: float) -> void:
	_check_player_distance()
	_update_state(delta)
	move_and_slide()

func _check_player_distance() -> void:
	if not player_ref:
		var players := get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			player_ref = players[0] as Player

	if player_ref and is_instance_valid(player_ref):
		var dist := global_position.distance_to(player_ref.global_position)
		if dist < detection_radius and current_state != State.FLEE:
			current_state = State.FLEE
			state_timer = 2.5

func _update_state(delta: float) -> void:
	state_timer -= delta
	match current_state:
		State.IDLE:
			velocity = Vector2.ZERO
			if state_timer <= 0.0:
				current_state = State.WANDER
				state_timer = randf_range(2.0, 4.0)
				_pick_wander_target()
		State.WANDER:
			var dir := (wander_target - global_position).normalized()
			velocity = dir * wander_speed
			if sprite and dir.x != 0.0:
				sprite.flip_h = (dir.x < 0.0)
			if global_position.distance_to(wander_target) < 6.0 or state_timer <= 0.0:
				current_state = State.IDLE
				state_timer = randf_range(1.5, 3.5)
		State.FLEE:
			if player_ref and is_instance_valid(player_ref):
				var away_dir := (global_position - player_ref.global_position).normalized()
				velocity = away_dir * flee_speed
				if sprite and away_dir.x != 0.0:
					sprite.flip_h = (away_dir.x < 0.0)
			if state_timer <= 0.0:
				current_state = State.IDLE
				state_timer = 2.0

func _pick_wander_target() -> void:
	var angle := randf() * TAU
	var dist := randf_range(10.0, 45.0)
	wander_target = home_position + Vector2(cos(angle), sin(angle)) * dist