class_name WorldLighting
extends Node

@export var canvas_modulate: CanvasModulate
@export var world_time: WorldTime
@export var season_manager: SeasonManager
@export var weather_manager: WeatherManager

# Phase baseline colors
const COLOR_DAWN     := Color(0.62, 0.52, 0.68, 1.0)
const COLOR_MORNING  := Color(0.88, 0.86, 0.82, 1.0)
const COLOR_NOON     := Color(1.00, 0.99, 0.96, 1.0)
const COLOR_EVENING  := Color(0.96, 0.62, 0.44, 1.0)
const COLOR_NIGHT    := Color(0.24, 0.25, 0.38, 1.0)
const COLOR_MIDNIGHT := Color(0.16, 0.18, 0.28, 1.0)

func _process(_delta: float) -> void:
	if not canvas_modulate or not world_time:
		return
	update_lighting()

func update_lighting() -> void:
	var h := float(world_time.hour) + float(world_time.minute) / 60.0
	var target_color := get_color_for_hour(h)

	# Apply season tint if present
	if season_manager:
		var st := season_manager.get_season_tint()
		target_color = target_color * st

	# Apply weather dimming if present
	if weather_manager:
		var dim := weather_manager.get_weather_dimming()
		target_color = target_color * Color(dim, dim, dim, 1.0)

	canvas_modulate.color = target_color

func get_color_for_hour(h: float) -> Color:
	if h >= 0.0 and h < 5.0:
		# Midnight to Dawn
		var t := (h - 0.0) / 5.0
		return COLOR_MIDNIGHT.lerp(COLOR_DAWN, t)
	elif h >= 5.0 and h < 7.0:
		# Dawn to Morning
		var t := (h - 5.0) / 2.0
		return COLOR_DAWN.lerp(COLOR_MORNING, t)
	elif h >= 7.0 and h < 12.0:
		# Morning to Noon
		var t := (h - 7.0) / 5.0
		return COLOR_MORNING.lerp(COLOR_NOON, t)
	elif h >= 12.0 and h < 17.0:
		# Noon to Evening
		var t := (h - 12.0) / 5.0
		return COLOR_NOON.lerp(COLOR_EVENING, t)
	elif h >= 17.0 and h < 20.0:
		# Evening to Night
		var t := (h - 17.0) / 3.0
		return COLOR_EVENING.lerp(COLOR_NIGHT, t)
	else:
		# Night to Midnight
		var t := (h - 20.0) / 4.0
		return COLOR_NIGHT.lerp(COLOR_MIDNIGHT, t)