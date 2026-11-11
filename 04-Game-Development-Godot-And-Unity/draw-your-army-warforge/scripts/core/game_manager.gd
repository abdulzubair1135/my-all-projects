class_name GameManagerNode
extends Node

const GAME_TITLE = "Draw Your Army: WarForge"
const GAME_VERSION = "0.1.0"
const RANKED_BUDGET_LIMIT = 1000
const MAX_UNITS_LIMIT = 300

enum GameMode {
	CREATIVE_WORKSHOP,
	OFFLINE_PRACTICE,
	CASUAL_ONLINE,
	RANKED_ONLINE
}

var current_mode: GameMode = GameMode.CREATIVE_WORKSHOP
var active_army_loadout: Dictionary = {}
var active_opponent_loadout: Dictionary = {}
var selected_soldier_design: Dictionary = {}
var last_battle_summary: Dictionary = {}

func _ready() -> void:
	print_rich("[color=gold][b]" + GAME_TITLE + " v" + GAME_VERSION + " initialized.[/b][/color]")
	var bus = get_node_or_null("/root/EventBus")
	if bus:
		bus.scene_change_requested.connect(_on_scene_change_requested)

func change_scene(scene_path: String) -> void:
	if ResourceLoader.exists(scene_path):
		get_tree().change_scene_to_file(scene_path)
	else:
		push_error("Scene file does not exist: " + scene_path)

func _on_scene_change_requested(scene_path: String) -> void:
	change_scene(scene_path)
