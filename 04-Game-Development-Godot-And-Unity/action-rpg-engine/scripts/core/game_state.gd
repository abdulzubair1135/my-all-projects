extends Node

signal game_day_advanced(new_day: int)
signal spawn_point_changed(new_spawn_id: String)

var current_save_slot: String = "slot_1"
var current_scene: String = "res://scenes/world/home/shelter.tscn"
var current_spawn_id: String = "spawn_home"
var game_day: int = 1
var game_time: String = "08:00"
var play_time: float = 0.0
var discovered_areas: Array[String] = ["home", "courtyard", "shore"]
var season: int = 0 # 0=Spring, 1=Summer, 2=Autumn, 3=Winter
var season_day: int = 1
var year: int = 1
var weather: String = "clear"
var temperature: float = 18.0
var current_objective: String = "Find Shelter Before Nightfall"

var settings: Dictionary = {
	"master_volume": 1.0,
	"fullscreen": false
}

# Temporary pending state passed during scene load / respawn
var pending_player_restore: Dictionary = {}
var pending_spawn_id: String = ""

func _process(delta: float) -> void:
	if not get_tree().paused:
		play_time += delta

func reset_for_new_game(slot_id: String = "slot_1") -> void:
	current_save_slot = slot_id
	current_scene = "res://scenes/world/home/shelter.tscn"
	current_spawn_id = "spawn_home"
	game_day = 1
	game_time = "08:00"
	play_time = 0.0
	season = 0
	season_day = 1
	year = 1
	weather = "clear"
	temperature = 18.0
	current_objective = "Find Shelter Before Nightfall"
	discovered_areas = ["home", "courtyard", "shore"]
	pending_player_restore.clear()
	pending_spawn_id = "spawn_home"

func set_current_spawn(spawn_id: String) -> void:
	if current_spawn_id != spawn_id:
		current_spawn_id = spawn_id
		spawn_point_changed.emit(spawn_id)

func advance_day() -> void:
	game_day += 1
	game_time = "08:00"
	game_day_advanced.emit(game_day)
	print("[GameState] Advanced to Day %d" % game_day)
