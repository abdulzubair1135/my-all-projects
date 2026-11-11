extends CanvasLayer

signal transition_started
signal transition_completed

@onready var color_rect: ColorRect = $ColorRect

var is_transitioning: bool = false

func _ready() -> void:
	if color_rect:
		color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		color_rect.modulate = Color(1, 1, 1, 0)

func change_scene(target_scene_path: String, target_spawn_id: String = "", save_before: bool = true) -> void:
	if is_transitioning:
		return
	is_transitioning = true
	transition_started.emit()

	var state_node: GameState = null
	if has_node("/root/GameState"):
		state_node = get_node("/root/GameState") as GameState
		if state_node:
			state_node.current_scene = target_scene_path
			state_node.pending_spawn_id = target_spawn_id

	# Optional auto-save before leaving
	if save_before and has_node("/root/SaveManager"):
		var sm := get_node("/root/SaveManager") as SaveManager
		sm.autosave()

	# 1. Fade out to black
	if color_rect:
		color_rect.mouse_filter = Control.MOUSE_FILTER_STOP
		var tween := create_tween()
		tween.tween_property(color_rect, "modulate:a", 1.0, 0.22)
		await tween.finished

	# 2. Change Scene
	get_tree().change_scene_to_file(target_scene_path)

	# 3. Wait for new scene root to be ready
	await get_tree().process_frame
	await get_tree().process_frame

	# 4. Position player at requested spawn point
	if target_spawn_id != "":
		_apply_spawn_placement(target_spawn_id)

	# 5. Fade in from black
	if color_rect:
		var tween_in := create_tween()
		tween_in.tween_property(color_rect, "modulate:a", 0.0, 0.25)
		await tween_in.finished
		color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE

	is_transitioning = false
	transition_completed.emit()

func _apply_spawn_placement(spawn_id: String) -> void:
	var root := get_tree().current_scene
	if not root:
		return

	var players := get_tree().get_nodes_in_group("player")
	if players.size() == 0:
		return
	var player: Player = players[0] as Player

	var spawn_point := SpawnManager.find_spawn_point(root, spawn_id)
	if spawn_point:
		SpawnManager.position_player_at_spawn(player, spawn_point)

	# If there was a pending player restore (e.g. from load game), apply it now
	if has_node("/root/GameState"):
		var state_node := get_node("/root/GameState") as GameState
		if state_node and state_node.pending_player_restore.size() > 0:
			SpawnManager.apply_saved_state(player, state_node.pending_player_restore)
			state_node.pending_player_restore.clear()
