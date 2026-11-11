class_name SpawnManager
extends RefCounted

static func find_spawn_point(tree_or_node: Variant, target_id: String) -> SpawnPoint:
	var root: Node = null
	if tree_or_node is SceneTree:
		root = (tree_or_node as SceneTree).current_scene
	elif tree_or_node is Node:
		root = tree_or_node as Node

	var spawn_points: Array = []
	if root and root.is_inside_tree():
		spawn_points = root.get_tree().get_nodes_in_group("spawn_points")
	for node in spawn_points:
		if node is SpawnPoint and (node as SpawnPoint).spawn_id == target_id:
			return node as SpawnPoint

	# Fallback: search recursively if not yet in groups
	if root:
		return _find_recursive(root, target_id)
	return null

static func _find_recursive(parent: Node, target_id: String) -> SpawnPoint:
	if parent is SpawnPoint and (parent as SpawnPoint).spawn_id == target_id:
		return parent as SpawnPoint
	for child in parent.get_children():
		var found := _find_recursive(child, target_id)
		if found:
			return found
	return null

static func position_player_at_spawn(player: Player, spawn_point: SpawnPoint) -> void:
	if not player or not spawn_point:
		return
	player.global_position = spawn_point.global_position
	player.current_facing = spawn_point.facing_direction
	player.velocity = Vector2.ZERO
	player.current_state = Player.State.IDLE
	if player.animated_sprite:
		player._update_animation()

static func apply_saved_state(player: Player, state_dict: Dictionary) -> void:
	if not player or state_dict.is_empty():
		return
	if state_dict.has("health"):
		player.current_health = float(state_dict["health"])
	if state_dict.has("max_health"):
		player.max_health = float(state_dict["max_health"])
	if state_dict.has("stamina"):
		player.current_stamina = float(state_dict["stamina"])
	if state_dict.has("max_stamina"):
		player.max_stamina = float(state_dict["max_stamina"])
	if state_dict.has("facing"):
		player.current_facing = int(state_dict["facing"]) as Player.Facing
	if state_dict.has("position") and state_dict["position"] is Array and state_dict["position"].size() >= 2:
		player.global_position = Vector2(state_dict["position"][0], state_dict["position"][1])

	player.current_state = Player.State.IDLE
	player.velocity = Vector2.ZERO
	player.health_changed.emit(player.current_health, player.max_health)
	player.stamina_changed.emit(player.current_stamina, player.max_stamina)
	if player.animated_sprite:
		player._update_animation()
