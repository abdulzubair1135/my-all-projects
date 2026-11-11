class_name WeatherManager
extends Node

signal weather_changed(new_weather: String)

const WEATHER_CLEAR: String = "clear"
const WEATHER_CLOUDY: String = "cloudy"
const WEATHER_RAIN: String = "rain"
const WEATHER_FOG: String = "fog"

var current_weather: String = WEATHER_CLEAR
var weather_timer: float = 300.0 # seconds remaining
var transition_blend: float = 0.0

@export var weather_change_interval: float = 300.0

func _process(delta: float) -> void:
	if get_tree().paused:
		return
	weather_timer -= delta
	if weather_timer <= 0.0:
		weather_timer = weather_change_interval
		_pick_next_weather()

func set_weather(weather_name: String, duration: float = 300.0) -> void:
	if current_weather != weather_name:
		current_weather = weather_name
		weather_timer = duration
		weather_changed.emit(current_weather)

func _pick_next_weather() -> void:
	# Probability: 60% clear, 20% cloudy, 15% rain, 5% fog
	var roll := randf()
	if roll < 0.60:
		set_weather(WEATHER_CLEAR)
	elif roll < 0.80:
		set_weather(WEATHER_CLOUDY)
	elif roll < 0.95:
		set_weather(WEATHER_RAIN)
	else:
		set_weather(WEATHER_FOG)

func get_weather_dimming() -> float:
	match current_weather:
		WEATHER_CLEAR: return 1.0
		WEATHER_CLOUDY: return 0.82
		WEATHER_RAIN: return 0.72
		WEATHER_FOG: return 0.78
	return 1.0