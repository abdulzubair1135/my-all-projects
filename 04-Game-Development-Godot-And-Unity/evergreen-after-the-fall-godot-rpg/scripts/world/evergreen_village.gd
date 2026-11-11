extends Node2D

# Evergreen: After the Fall - Evergreen Village Region
# Commercial & community hub: town square, Lily's general store, Marcus's smithy, clinic annex, and survivor notice board

const GroundGenerator = preload("res://scripts/world/ground_generator.gd")

@onready var player: CharacterBody2D = $Player
@onready var time_modulate: CanvasModulate = $DayNightModulate

func _ready() -> void:
	GameState.is_in_safe_zone = true
	EventBus.time_updated.connect(_on_time_updated)
	_update_lighting(GameState.current_hour, GameState.current_minute)
	
	GroundGenerator.generate_region_ground(self, "evergreen_village", 960, 540)
	
	if player and player.camera:
		player.camera.limit_left = 0
		player.camera.limit_top = 0
		player.camera.limit_right = 960
		player.camera.limit_bottom = 540
	
	WorldManager.apply_player_spawn(player)
	EventBus.notification_requested.emit("Evergreen Village - Safe Community Settlement", 3.0)

func _on_time_updated(hour: int, minute: int, _day: int, _season: String) -> void:
	_update_lighting(hour, minute)

func _update_lighting(hour: int, minute: int) -> void:
	if not time_modulate:
		return
	
	var total_minutes = hour * 60 + minute
	var target_color = Color.WHITE
	
	if total_minutes < 300:
		target_color = Color(0.28, 0.32, 0.48)
	elif total_minutes < 420:
		var t = float(total_minutes - 300) / 120.0
		target_color = Color(0.28, 0.32, 0.48).lerp(Color(0.95, 0.85, 0.72), t)
	elif total_minutes < 1020:
		target_color = Color(1.0, 1.0, 1.0)
	elif total_minutes < 1200:
		var t = float(total_minutes - 1020) / 180.0
		target_color = Color(1.0, 1.0, 1.0).lerp(Color(0.88, 0.62, 0.52), t)
	else:
		var t = float(total_minutes - 1200) / 240.0
		target_color = Color(0.88, 0.62, 0.52).lerp(Color(0.28, 0.32, 0.48), t)
	
	time_modulate.color = target_color
