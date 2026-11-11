extends Node

signal game_saved(slot_id: String)
signal game_loaded(slot_id: String)
signal save_deleted(slot_id: String)
signal save_error(slot_id: String, message: String)

const SAVE_DIR: String = "user://saves/"
const SLOTS: Array[String] = ["slot_1", "slot_2", "slot_3"]

var is_saving: bool = false

func _ready() -> void:
	_ensure_save_directory()

func _ensure_save_directory() -> void:
	if not DirAccess.dir_exists_absolute(SAVE_DIR):
		DirAccess.make_dir_recursive_absolute(SAVE_DIR)

func get_slot_path(slot_id: String) -> String:
	return SAVE_DIR + slot_id + ".save"

func get_temp_slot_path(slot_id: String) -> String:
	return SAVE_DIR + slot_id + ".tmp"

func has_save(slot_id: String) -> bool:
	return FileAccess.file_exists(get_slot_path(slot_id))

func create_new_game(slot_id: String = "slot_1") -> bool:
	var state_node = _get_game_state()
	if state_node:
		state_node.reset_for_new_game(slot_id)
	return save_game(slot_id)

func save_game(slot_id: String, player: Player = null) -> bool:
	if is_saving:
		return false
	is_saving = true
	_ensure_save_directory()

	var state_node = _get_game_state()
	if not player and is_inside_tree():
		var players := get_tree().get_nodes_in_group("player")
		if players.size() > 0:
			player = players[0] as Player

	var save_dict := SaveData.create_save_dictionary(state_node, player)
	var json_str := JSON.stringify(save_dict, "\t")

	var temp_path := get_temp_slot_path(slot_id)
	var final_path := get_slot_path(slot_id)

	# 1. Write to temporary file
	var temp_file := FileAccess.open(temp_path, FileAccess.WRITE)
	if not temp_file:
		var err := FileAccess.get_open_error()
		var msg := "Failed to open temporary save file %s (Error %d)" % [temp_path, err]
		push_error(msg)
		save_error.emit(slot_id, msg)
		is_saving = false
		return false

	temp_file.store_string(json_str)
	temp_file.close()

	# 2. Verify temporary file can be read and parsed correctly
	var verify_file := FileAccess.open(temp_path, FileAccess.READ)
	if not verify_file:
		push_error("Could not verify temporary save file.")
		save_error.emit(slot_id, "Verification failed")
		is_saving = false
		return false

	var verify_str := verify_file.get_as_text()
	verify_file.close()

	var parse_result: Variant = JSON.parse_string(verify_str)
	if not SaveData.validate_save_data(parse_result):
		push_error("Temporary save data validation failed.")
		save_error.emit(slot_id, "Data validation failed")
		DirAccess.remove_absolute(temp_path)
		is_saving = false
		return false

	# 3. Replace target save file atomically
	if FileAccess.file_exists(final_path):
		DirAccess.remove_absolute(final_path)

	var rename_err := DirAccess.rename_absolute(temp_path, final_path)
	if rename_err != OK:
		# Fallback to copy & delete
		var copy_err := DirAccess.copy_absolute(temp_path, final_path)
		DirAccess.remove_absolute(temp_path)
		if copy_err != OK:
			push_error("Failed to commit save file to %s" % final_path)
			save_error.emit(slot_id, "Commit failed")
			is_saving = false
			return false

	if state_node:
		state_node.current_save_slot = slot_id

	is_saving = false
	game_saved.emit(slot_id)
	print("[SaveManager] Successfully saved game to %s" % slot_id)
	return true

func load_game(slot_id: String) -> Dictionary:
	var file_path := get_slot_path(slot_id)
	if not FileAccess.file_exists(file_path):
		save_error.emit(slot_id, "Save file does not exist")
		return {}

	var file := FileAccess.open(file_path, FileAccess.READ)
	if not file:
		save_error.emit(slot_id, "Could not open save file")
		return {}

	var json_str := file.get_as_text()
	file.close()

	var data: Variant = JSON.parse_string(json_str)
	if not SaveData.validate_save_data(data):
		save_error.emit(slot_id, "Corrupted save file data")
		return {}

	var dict := data as Dictionary
	var state_node: GameState = _get_game_state()
	if state_node:
		state_node.current_save_slot = slot_id
		if dict.has("world") and dict["world"] is Dictionary:
			var w: Dictionary = dict["world"]
			state_node.current_scene = w.get("current_scene", "res://scenes/world/home/shelter.tscn")
			state_node.current_spawn_id = w.get("current_spawn_id", "spawn_home")
			state_node.pending_spawn_id = state_node.current_spawn_id
			if w.has("discovered_areas"):
				state_node.discovered_areas = Array(w["discovered_areas"], TYPE_STRING, &"", null)
			if w.has("season"):
				state_node.season = int(w["season"])
			if w.has("season_day"):
				state_node.season_day = int(w["season_day"])
			if w.has("year"):
				state_node.year = int(w["year"])
			if w.has("weather"):
				state_node.weather = str(w["weather"])
			if w.has("temperature"):
				state_node.temperature = float(w["temperature"])
		if dict.has("game_day"):
			state_node.game_day = int(dict["game_day"])
		if dict.has("game_time"):
			state_node.game_time = str(dict["game_time"])
		if dict.has("play_time"):
			state_node.play_time = float(dict["play_time"])
		if dict.has("player") and dict["player"] is Dictionary:
			state_node.pending_player_restore = dict["player"].duplicate(true)
		if dict.has("settings") and dict["settings"] is Dictionary:
			state_node.settings = dict["settings"].duplicate(true)

	game_loaded.emit(slot_id)
	print("[SaveManager] Loaded game from %s" % slot_id)
	return dict

func delete_save(slot_id: String) -> bool:
	var file_path := get_slot_path(slot_id)
	if FileAccess.file_exists(file_path):
		var err := DirAccess.remove_absolute(file_path)
		if err == OK:
			save_deleted.emit(slot_id)
			print("[SaveManager] Deleted save %s" % slot_id)
			return true
	return false

func get_save_metadata(slot_id: String) -> Dictionary:
	var file_path := get_slot_path(slot_id)
	if not FileAccess.file_exists(file_path):
		return {"exists": false}

	var file := FileAccess.open(file_path, FileAccess.READ)
	if not file:
		return {"exists": false, "corrupted": true}

	var json_str := file.get_as_text()
	file.close()

	var data: Variant = JSON.parse_string(json_str)
	if not SaveData.validate_save_data(data):
		return {"exists": true, "corrupted": true}

	var dict := data as Dictionary
	var world_data: Dictionary = dict.get("world", {})
	return {
		"exists": true,
		"corrupted": false,
		"save_version": dict.get("save_version", 1),
		"timestamp": dict.get("timestamp", 0),
		"game_day": dict.get("game_day", 1),
		"play_time": dict.get("play_time", 0.0),
		"current_scene": world_data.get("current_scene", "Unknown"),
		"current_spawn_id": world_data.get("current_spawn_id", "spawn_home")
	}

func get_latest_save() -> String:
	var latest_slot: String = ""
	var latest_time: int = -1

	for slot_id in SLOTS:
		var meta := get_save_metadata(slot_id)
		if meta.get("exists", false) and not meta.get("corrupted", false):
			var ts: int = meta.get("timestamp", 0)
			if ts > latest_time:
				latest_time = ts
				latest_slot = slot_id

	return latest_slot

func validate_save(slot_id: String) -> bool:
	var meta := get_save_metadata(slot_id)
	return meta.get("exists", false) and not meta.get("corrupted", false)

func autosave(player: Player = null) -> bool:
	var state_node = _get_game_state()
	var slot_id: String = state_node.current_save_slot if state_node else "slot_1"
	return save_game(slot_id, player)

func _get_game_state() -> Node:
	if is_inside_tree():
		var node := get_node_or_null("/root/GameState")
		if node:
			return node
	if get_parent():
		var node := get_parent().get_node_or_null("GameState")
		if node:
			return node
	return null
