class_name WorldTime
extends Node

signal time_tick(hour: int, minute: int)
signal hour_passed(hour: int)
signal day_passed(day: int)
signal phase_changed(phase: String)

enum Phase {
	DAWN,      # 05:00 - 06:00
	MORNING,   # 06:00 - 12:00
	NOON,      # 12:00 - 17:00
	EVENING,   # 17:00 - 20:00
	NIGHT,     # 20:00 - 00:00
	MIDNIGHT   # 00:00 - 05:00
}

@export var day_length_seconds: float = 720.0 # 12 real minutes per in-game day
@export var is_paused: bool = false

var time_seconds: float = 28800.0 # Starts at 08:00 (8 * 3600)
var hour: int = 8
var minute: int = 0
var game_day: int = 1
var is_night: bool = false
var current_phase: Phase = Phase.MORNING

const SECONDS_IN_DAY: float = 86400.0

func _ready() -> void:
	_update_derived_time()

func _process(delta: float) -> void:
	if is_paused or get_tree().paused:
		return
	var simulated_speed: float = SECONDS_IN_DAY / max(1.0, day_length_seconds)
	advance_time(delta * simulated_speed)

func advance_time(delta_simulated_seconds: float) -> void:
	var prev_hour: int = hour
	time_seconds += delta_simulated_seconds

	if time_seconds >= SECONDS_IN_DAY:
		time_seconds = fmod(time_seconds, SECONDS_IN_DAY)
		game_day += 1
		day_passed.emit(game_day)

	_update_derived_time()

	if hour != prev_hour:
		hour_passed.emit(hour)

func set_time(target_hour: int, target_minute: int) -> void:
	time_seconds = target_hour * 3600.0 + target_minute * 60.0
	_update_derived_time()

func skip_to_morning(target_hour: int = 6) -> void:
	if hour >= target_hour:
		game_day += 1
		day_passed.emit(game_day)
	set_time(target_hour, 0)

func _update_derived_time() -> void:
	hour = int(time_seconds / 3600.0) % 24
	minute = int(fmod(time_seconds, 3600.0) / 60.0) % 60
	is_night = (hour >= 20 or hour < 5)

	var prev_p := current_phase
	if hour >= 5 and hour < 6:
		current_phase = Phase.DAWN
	elif hour >= 6 and hour < 12:
		current_phase = Phase.MORNING
	elif hour >= 12 and hour < 17:
		current_phase = Phase.NOON
	elif hour >= 17 and hour < 20:
		current_phase = Phase.EVENING
	elif hour >= 20 and hour < 24:
		current_phase = Phase.NIGHT
	else:
		current_phase = Phase.MIDNIGHT

	if current_phase != prev_p:
		phase_changed.emit(get_phase_name())

	time_tick.emit(hour, minute)

func get_time_string() -> String:
	return "%02d:%02d" % [hour, minute]

func get_phase_name() -> String:
	match current_phase:
		Phase.DAWN: return "dawn"
		Phase.MORNING: return "morning"
		Phase.NOON: return "noon"
		Phase.EVENING: return "evening"
		Phase.NIGHT: return "night"
		Phase.MIDNIGHT: return "midnight"
	return "morning"

func get_day_progress() -> float:
	return time_seconds / SECONDS_IN_DAY