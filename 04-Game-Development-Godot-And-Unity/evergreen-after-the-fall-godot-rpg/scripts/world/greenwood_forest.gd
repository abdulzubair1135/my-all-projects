extends Node2D

# Evergreen: After the Fall - Greenwood Forest Region
# Wilderness gathering trails, logging camp, ranger hut, wild flora, and roaming infected

const GroundGenerator = preload("res://scripts/world/ground_generator.gd")

@onready var player: CharacterBody2D = $Player
@onready var time_modulate: CanvasModulate = $DayNightModulate

func _ready() -> void:
	GameState.is_in_safe_zone = false # Danger zone: infected roam here!
	EventBus.time_updated.connect(_on_time_updated)
	_update_lighting(GameState.current_hour, GameState.current_minute)
	
	GroundGenerator.generate_region_ground(self, "greenwood_forest", 960, 540)
	
	if player and player.camera:
		player.camera.limit_left = 0
		player.camera.limit_top = 0
		player.camera.limit_right = 960
		player.camera.limit_bottom = 540
	
	WorldManager.apply_player_spawn(player)
	EventBus.notification_requested.emit("Greenwood Forest - Danger Zone. Sound attracts infected!", 3.5)

func _on_time_updated(hour: int, minute: int, _day: int, _season: String) -> void:
	_update_lighting(hour, minute)

func _update_lighting(hour: int, minute: int) -> void:
	if not time_modulate:
		return
	
	var total_minutes = hour * 60 + minute
	var target_color = Color.WHITE
	
	# Deeper, moodier forest canopy shadow
	if total_minutes < 300:
		target_color = Color(0.20, 0.25, 0.40)
	elif total_minutes < 420:
		var t = float(total_minutes - 300) / 120.0
		target_color = Color(0.20, 0.25, 0.40).lerp(Color(0.85, 0.78, 0.65), t)
	elif total_minutes < 1020:
		target_color = Color(0.92, 0.95, 0.92) # Forest canopy filtered light
	elif total_minutes < 1200:
		var t = float(total_minutes - 1020) / 180.0
		target_color = Color(0.92, 0.95, 0.92).lerp(Color(0.78, 0.55, 0.45), t)
	else:
		var t = float(total_minutes - 1200) / 240.0
		target_color = Color(0.78, 0.55, 0.45).lerp(Color(0.20, 0.25, 0.40), t)
	
	time_modulate.color = target_color
