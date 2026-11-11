class_name SettingsManagerNode
extends Node

const SETTINGS_FILE = "settings.json"

var master_volume: float = 0.8
var music_volume: float = 0.7
var sfx_volume: float = 0.8
var fullscreen: bool = false
var vsync: bool = true
var msaa_quality: int = 2
var camera_sensitivity: float = 1.0

func _ready() -> void:
	load_settings()

func load_settings() -> void:
	var db = get_node_or_null("/root/DatabaseManager")
	var data = {}
	if db:
		data = db.load_json_file(SETTINGS_FILE)
	
	if not data.is_empty():
		master_volume = data.get("master_volume", master_volume)
		music_volume = data.get("music_volume", music_volume)
		sfx_volume = data.get("sfx_volume", sfx_volume)
		fullscreen = data.get("fullscreen", fullscreen)
		vsync = data.get("vsync", vsync)
		msaa_quality = data.get("msaa_quality", msaa_quality)
		camera_sensitivity = data.get("camera_sensitivity", camera_sensitivity)
	
	apply_settings()

func save_settings() -> void:
	var data = {
		"master_volume": master_volume,
		"music_volume": music_volume,
		"sfx_volume": sfx_volume,
		"fullscreen": fullscreen,
		"vsync": vsync,
		"msaa_quality": msaa_quality,
		"camera_sensitivity": camera_sensitivity,
		"version": "1.0.0"
	}
	var db = get_node_or_null("/root/DatabaseManager")
	if db:
		db.save_json_file(SETTINGS_FILE, data)

func apply_settings() -> void:
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN and fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
	elif DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED and not fullscreen:
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	
	if vsync:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED)
	else:
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
