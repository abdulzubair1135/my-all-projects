class_name SaveData
extends RefCounted

const CURRENT_SAVE_VERSION: int = 1

# Registry for future modules (inventory, quests, farming, etc.)
static var _providers: Dictionary = {}

static func register_provider(provider_name: String, provider_instance: Object) -> void:
	_providers[provider_name] = provider_instance

static func unregister_provider(provider_name: String) -> void:
	_providers.erase(provider_name)

static func create_save_dictionary(game_state: Variant = null, player: Player = null) -> Dictionary:
	var save_dict: Dictionary = {
		"save_version": CURRENT_SAVE_VERSION,
		"timestamp": int(Time.get_unix_time_from_system()),
		"game_day": game_state.game_day if game_state else 1,
		"game_time": game_state.game_time if game_state else "08:00",
		"play_time": game_state.play_time if game_state else 0.0,
		"player": {},
		"world": {},
		"progression": {},
		"settings": game_state.settings.duplicate(true) if (game_state and game_state.settings) else {}
	}

	# Player Data
	if player and is_instance_valid(player):
		save_dict["player"] = {
			"health": player.current_health,
			"max_health": player.max_health,
			"stamina": player.current_stamina,
			"max_stamina": player.max_stamina,
			"position": [player.global_position.x, player.global_position.y],
			"facing": int(player.current_facing)
		}
	elif game_state and game_state.pending_player_restore.size() > 0:
		save_dict["player"] = game_state.pending_player_restore.duplicate(true)
	else:
		save_dict["player"] = {
			"health": 100.0,
			"max_health": 100.0,
			"stamina": 100.0,
			"max_stamina": 100.0,
			"position": [416.0, 288.0],
			"facing": int(Player.Facing.DOWN)
		}

	# World Data
	save_dict["world"] = {
		"current_scene": game_state.current_scene if game_state else "res://scenes/world/home/shelter.tscn",
		"current_spawn_id": game_state.current_spawn_id if game_state else "spawn_home",
		"discovered_areas": game_state.discovered_areas.duplicate() if game_state else ["home", "courtyard", "shore"],
		"season": game_state.season if (game_state and "season" in game_state) else 0,
		"season_day": game_state.season_day if (game_state and "season_day" in game_state) else 1,
		"year": game_state.year if (game_state and "year" in game_state) else 1,
		"weather": game_state.weather if (game_state and "weather" in game_state) else "clear",
		"temperature": game_state.temperature if (game_state and "temperature" in game_state) else 18.0
	}

	# Collect from any registered future providers
	for provider_name: String in _providers:
		var provider: Object = _providers[provider_name]
		if is_instance_valid(provider) and provider.has_method("save_data"):
			save_dict[provider_name] = provider.call("save_data")

	return save_dict

static func validate_save_data(data: Variant) -> bool:
	if typeof(data) != TYPE_DICTIONARY:
		return false
	var dict := data as Dictionary
	if not dict.has("save_version") or typeof(dict["save_version"]) != TYPE_INT and typeof(dict["save_version"]) != TYPE_FLOAT:
		return false
	if not dict.has("player") or typeof(dict["player"]) != TYPE_DICTIONARY:
		return false
	if not dict.has("world") or typeof(dict["world"]) != TYPE_DICTIONARY:
		return false
	return true
