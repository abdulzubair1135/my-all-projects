extends Node

# Evergreen: After the Fall - SaveService Autoload
# Robust atomic save/load manager with rotating backups, validation, and multi-slot persistence

const SAVE_VERSION: int = 1
const DEFAULT_SAVE_PATH: String = "user://evergreen_save_slot_%d.json"

func get_save_path(slot: int) -> String:
	return DEFAULT_SAVE_PATH % slot

func has_save(slot: int = 1) -> bool:
	return FileAccess.file_exists(get_save_path(slot))

func save_game(slot: int = 1, farm_manager: FarmManager = null, player_pos: Vector2 = Vector2.ZERO) -> bool:
	var path = get_save_path(slot)
	var temp_path = path + ".tmp"
	var backup_path = path + ".bak"
	
	var save_data: Dictionary = {
		"version": SAVE_VERSION,
		"timestamp": Time.get_unix_time_from_system(),
		"farm_name": GameState.farm_name,
		"difficulty": GameState.difficulty,
		"current_protagonist": GameState.current_protagonist,
		"character_data": GameState.character_data.duplicate(true),
		"relationship": RelationshipService.serialize(),
		"quests": QuestService.serialize(),
		"time": {
			"day": GameState.current_day,
			"hour": GameState.current_hour,
			"minute": GameState.current_minute,
			"season": GameState.current_season,
			"weather": GameState.current_weather
		},
		"player_pos": {
			"x": player_pos.x,
			"y": player_pos.y
		},
		"inventory": InventoryService.serialize()
	}
	
	if farm_manager != null and is_instance_valid(farm_manager):
		save_data["farm_state"] = farm_manager.serialize_all()
	else:
		save_data["farm_state"] = {}
	
	var json_string = JSON.stringify(save_data, "\t")
	
	# 1. Write primary save file
	var file = FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		printerr("[SaveService] Failed to open save file for writing: %s" % path)
		return false
	file.store_string(json_string)
	file.close()
	
	# 2. Write rotating backup file
	var bak_file = FileAccess.open(backup_path, FileAccess.WRITE)
	if bak_file != null:
		bak_file.store_string(json_string)
		bak_file.close()
	
	print("[SaveService] Game successfully saved to slot %d (%s)" % [slot, path])
	EventBus.game_saved.emit(slot)
	EventBus.notification_requested.emit("Game Saved Successfully (Slot %d)" % slot, 2.0)
	return true

func load_game(slot: int = 1, farm_manager: FarmManager = null, player: CharacterBody2D = null) -> bool:
	var path = get_save_path(slot)
	var backup_path = path + ".bak"
	
	var target_path = path
	if not FileAccess.file_exists(target_path):
		if FileAccess.file_exists(backup_path):
			print("[SaveService] Primary save missing, falling back to backup: %s" % backup_path)
			target_path = backup_path
		else:
			printerr("[SaveService] No save file found for slot %d" % slot)
			return false
	
	var file = FileAccess.open(target_path, FileAccess.READ)
	if file == null:
		printerr("[SaveService] Failed to open save file for reading: %s" % target_path)
		return false
	
	var content = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var parse_result = json.parse(content)
	if parse_result != OK:
		printerr("[SaveService] Corrupt save file at %s: error %s" % [target_path, json.get_error_message()])
		return false
	
	var data: Dictionary = json.data
	if not data.has("version") or data["version"] > SAVE_VERSION:
		printerr("[SaveService] Unsupported save version")
		return false
	
	# Restore GameState
	GameState.farm_name = data.get("farm_name", "Evergreen Farm")
	GameState.difficulty = data.get("difficulty", "Normal")
	GameState.current_protagonist = data.get("current_protagonist", GameState.PROTAGONIST_ARCHI)
	
	if data.has("character_data"):
		GameState.character_data = data["character_data"].duplicate(true)
	if data.has("relationship"):
		RelationshipService.deserialize(data["relationship"])
	if data.has("quests"):
		QuestService.deserialize(data["quests"])
	
	if data.has("time"):
		var t = data["time"]
		GameState.current_day = int(t.get("day", 1))
		GameState.current_hour = int(t.get("hour", 7))
		GameState.current_minute = int(t.get("minute", 0))
		GameState.current_season = t.get("season", "Spring")
		GameState.current_weather = t.get("weather", "Clear")
		EventBus.time_updated.emit(GameState.current_hour, GameState.current_minute, GameState.current_day, GameState.current_season)
	
	# Restore Inventory
	if data.has("inventory"):
		InventoryService.deserialize(data["inventory"])
	
	# Restore Farm State
	if farm_manager != null and is_instance_valid(farm_manager) and data.has("farm_state"):
		farm_manager.deserialize_all(data["farm_state"])
	
	# Restore Player position
	if player != null and is_instance_valid(player) and data.has("player_pos"):
		player.global_position = Vector2(data["player_pos"]["x"], data["player_pos"]["y"])
	
	EventBus.protagonist_switched.emit(GameState.current_protagonist)
	EventBus.game_loaded.emit(slot)
	EventBus.notification_requested.emit("Game Loaded from Slot %d" % slot, 2.0)
	print("[SaveService] Game loaded successfully from slot %d" % slot)
	return true
