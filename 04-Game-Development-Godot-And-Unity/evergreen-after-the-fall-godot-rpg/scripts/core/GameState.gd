extends Node

# Evergreen: After the Fall - GameState Autoload
# Central authority for game session state, stats, time, and global configuration

const PROTAGONIST_ARCHI: String = "archi"
const PROTAGONIST_DANISH: String = "danish"

# Global session data
var farm_name: String = "Evergreen Farm"
var difficulty: String = "Normal"
var current_protagonist: String = PROTAGONIST_ARCHI
var is_in_safe_zone: bool = true
var is_game_paused: bool = false

# Accessibility and Settings
var screen_shake_enabled: bool = true
var damage_numbers_enabled: bool = true
var touch_controls_mode: String = "auto"
var text_scale: float = 1.0
var colorblind_mode: String = "none"

# Calendar and Time
var current_minute: int = 0
var current_hour: int = 7 # 07:00 AM start
var current_day: int = 1
var current_season: String = "Spring"
var current_weather: String = "Clear"
var time_scale: float = 1.0 # 1 sec real time = ~1 min game time

# Protagonist stats records
var character_data: Dictionary = {
	PROTAGONIST_ARCHI: {
		"name": "Archi",
		"title": "Field Specialist & Healer",
		"health": 100.0,
		"max_health": 100.0,
		"stamina": 120.0,
		"max_stamina": 120.0,
		"stamina_recovery": 18.0,
		"hunger": 100.0,
		"thirst": 100.0,
		"speed_walk": 125.0,
		"speed_sprint": 200.0,
		"dodge_speed": 270.0,
		"combat_style": "Agile / Precision",
		"portrait_path": "res://assets/ui/portrait_archi.png",
		"sprite_sheet": "res://assets/characters/archi/archi_spritesheet.png"
	},
	PROTAGONIST_DANISH: {
		"name": "Danish",
		"title": "Combat Specialist & Builder",
		"health": 130.0,
		"max_health": 130.0,
		"stamina": 100.0,
		"max_stamina": 100.0,
		"stamina_recovery": 14.0,
		"hunger": 100.0,
		"thirst": 100.0,
		"speed_walk": 115.0,
		"speed_sprint": 185.0,
		"dodge_speed": 240.0,
		"combat_style": "Heavy / Resilient",
		"portrait_path": "res://assets/ui/portrait_danish.png",
		"sprite_sheet": "res://assets/characters/danish/danish_spritesheet.png"
	}
}

# Relationship dimensions with Danish/Archi
var relationship: Dictionary = {
	"trust": 25,
	"closeness": 20,
	"respect": 30,
	"memories": ["Arrived together at Evergreen Farm."]
}

# Quick inventory items (slot -> item dict)
var quick_slots: Array = [
	{"id": "tool_hoe", "name": "Field Hoe", "count": 1, "icon_coord": Vector2i(1, 1)},
	{"id": "tool_can", "name": "Watering Can", "count": 1, "icon_coord": Vector2i(2, 1)},
	{"id": "seed_turnip", "name": "Turnip Seeds", "count": 15, "icon_coord": Vector2i(0, 1)},
	{"id": "food_bread", "name": "Fresh Bread", "count": 3, "icon_coord": Vector2i(0, 0)},
	{"id": "weapon_machete", "name": "Sturdy Machete", "count": 1, "icon_coord": Vector2i(3, 1)}
]
var active_slot_index: int = 0

func _enter_tree() -> void:
	_setup_input_actions()

func _ready() -> void:
	print("[GameState] Initialized Evergreen session. Active protagonist: %s" % current_protagonist)

func _process(delta: float) -> void:
	_tick_time(delta)

func _setup_input_actions() -> void:
	# Guarantee all standard input actions exist with primary and alternate mappings
	_add_key_action("move_up", [KEY_W, KEY_UP])
	_add_key_action("move_down", [KEY_S, KEY_DOWN])
	_add_key_action("move_left", [KEY_A, KEY_LEFT])
	_add_key_action("move_right", [KEY_D, KEY_RIGHT])
	_add_key_action("sprint", [KEY_SHIFT])
	_add_key_action("attack", [KEY_J])
	_add_key_action("heavy_attack", [KEY_K])
	_add_key_action("dodge", [KEY_SPACE])
	_add_key_action("interact", [KEY_E])
	_add_key_action("inventory", [KEY_I])
	_add_key_action("world_map", [KEY_M])
	_add_key_action("quick_item", [KEY_Q])
	_add_key_action("switch_protagonist", [KEY_TAB])
	_add_key_action("pause", [KEY_ESCAPE])

func _add_key_action(action_name: String, keycodes: Array) -> void:
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
	for kc in keycodes:
		var ev: InputEventKey = InputEventKey.new()
		ev.physical_keycode = kc
		# Avoid duplicate events
		var exists: bool = false
		for existing in InputMap.action_get_events(action_name):
			if existing is InputEventKey and existing.physical_keycode == kc:
				exists = true
				break
		if not exists:
			InputMap.action_add_event(action_name, ev)

func _tick_time(delta: float) -> void:
	if is_game_paused:
		return
	
	# ~1.5 real seconds = 1 in-game minute
	current_minute += int(delta * 40.0 * time_scale)
	if current_minute >= 60:
		current_minute = 0
		current_hour += 1
		if current_hour >= 24:
			current_hour = 0
			current_day += 1
			EventBus.day_started.emit(current_day)
		if current_hour == 20: # 8 PM night start
			EventBus.night_started.emit(current_day)
		EventBus.time_updated.emit(current_hour, current_minute, current_day, current_season)

func get_current_stats() -> Dictionary:
	return character_data[current_protagonist]

func switch_protagonist() -> bool:
	if not is_in_safe_zone:
		EventBus.notification_requested.emit("Can only switch protagonist in safe zones!", 2.5)
		return false
	
	var old_p: String = current_protagonist
	current_protagonist = PROTAGONIST_DANISH if current_protagonist == PROTAGONIST_ARCHI else PROTAGONIST_ARCHI
	var new_name: String = character_data[current_protagonist]["name"]
	print("[GameState] Switched protagonist from %s to %s" % [old_p, current_protagonist])
	EventBus.protagonist_switched.emit(current_protagonist)
	EventBus.notification_requested.emit("Now controlling: %s" % new_name, 2.0)
	return true

func consume_stamina(amount: float) -> bool:
	var stats = get_current_stats()
	if stats["stamina"] >= amount:
		stats["stamina"] = max(0.0, stats["stamina"] - amount)
		EventBus.stamina_changed.emit(stats["stamina"], stats["max_stamina"])
		return true
	return false

func restore_stamina(amount: float) -> void:
	var stats = get_current_stats()
	if stats["stamina"] < stats["max_stamina"]:
		stats["stamina"] = min(stats["max_stamina"], stats["stamina"] + amount)
		EventBus.stamina_changed.emit(stats["stamina"], stats["max_stamina"])

func take_damage(amount: float) -> void:
	var stats = get_current_stats()
	stats["health"] = max(0.0, stats["health"] - amount)
	EventBus.health_changed.emit(stats["health"], stats["max_health"])
	if stats["health"] <= 0.0:
		EventBus.player_died.emit()

func save_settings() -> void:
	var cfg = ConfigFile.new()
	cfg.set_value("accessibility", "screen_shake", screen_shake_enabled)
	cfg.set_value("accessibility", "damage_numbers", damage_numbers_enabled)
	cfg.set_value("accessibility", "touch_controls", touch_controls_mode)
	cfg.set_value("accessibility", "colorblind", colorblind_mode)
	cfg.set_value("accessibility", "text_scale", text_scale)
	if AudioService:
		cfg.set_value("audio", "master", AudioService.master_volume)
		cfg.set_value("audio", "music", AudioService.music_volume)
		cfg.set_value("audio", "sfx", AudioService.sfx_volume)
	cfg.save("user://settings.cfg")
	print("[GameState] Settings saved to user://settings.cfg")

func load_settings() -> void:
	var cfg = ConfigFile.new()
	var err = cfg.load("user://settings.cfg")
	if err != OK:
		return
	screen_shake_enabled = cfg.get_value("accessibility", "screen_shake", true)
	damage_numbers_enabled = cfg.get_value("accessibility", "damage_numbers", true)
	touch_controls_mode = cfg.get_value("accessibility", "touch_controls", "auto")
	colorblind_mode = cfg.get_value("accessibility", "colorblind", "none")
	text_scale = cfg.get_value("accessibility", "text_scale", 1.0)
	if AudioService:
		AudioService.set_master_volume(cfg.get_value("audio", "master", 1.0))
		AudioService.set_music_volume(cfg.get_value("audio", "music", 0.8))
		AudioService.set_sfx_volume(cfg.get_value("audio", "sfx", 0.85))
	print("[GameState] Settings loaded from user://settings.cfg")
