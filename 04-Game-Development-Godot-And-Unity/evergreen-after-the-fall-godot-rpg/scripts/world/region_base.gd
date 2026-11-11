extends Node2D
class_name RegionBase

# Evergreen: After the Fall - Reusable Region Controller
# Handles day/night lighting, camera boundaries, player spawn handoffs, and ambient notification

const GroundGenerator = preload("res://scripts/world/ground_generator.gd")

@export var region_id: String = "evergreen_farm"
@export var is_safe_zone: bool = true
@export var region_title: String = "Evergreen Region"
@export var map_width: int = 960
@export var map_height: int = 540

@onready var player: CharacterBody2D = $Player
@onready var time_modulate: CanvasModulate = $DayNightModulate

func _ready() -> void:
	GameState.is_in_safe_zone = is_safe_zone
	EventBus.time_updated.connect(_on_time_updated)
	_update_lighting(GameState.current_hour, GameState.current_minute)
	
	GroundGenerator.generate_region_ground(self, region_id, map_width, map_height)
	
	if player and player.camera:
		player.camera.limit_left = 0
		player.camera.limit_top = 0
		player.camera.limit_right = map_width
		player.camera.limit_bottom = map_height
	
	WorldManager.apply_player_spawn(player)
	EventBus.notification_requested.emit(region_title, 3.0)

func _on_time_updated(hour: int, minute: int, _day: int, _season: String) -> void:
	_update_lighting(hour, minute)

func _update_lighting(hour: int, minute: int) -> void:
	if not time_modulate:
		return
	
	var total_minutes = hour * 60 + minute
	var target_color = Color.WHITE
	
	if total_minutes < 300: # Night
		target_color = Color(0.25, 0.28, 0.45)
	elif total_minutes < 420: # Dawn
		var t = float(total_minutes - 300) / 120.0
		target_color = Color(0.25, 0.28, 0.45).lerp(Color(0.92, 0.85, 0.75), t)
	elif total_minutes < 1020: # Day
		target_color = Color(1.0, 1.0, 0.98)
	elif total_minutes < 1200: # Dusk
		var t = float(total_minutes - 1020) / 180.0
		target_color = Color(1.0, 1.0, 0.98).lerp(Color(0.85, 0.65, 0.55), t)
	else: # Returning to Night
		var t = float(total_minutes - 1200) / 240.0
		target_color = Color(0.85, 0.65, 0.55).lerp(Color(0.25, 0.28, 0.45), t)
	
	time_modulate.color = target_color
