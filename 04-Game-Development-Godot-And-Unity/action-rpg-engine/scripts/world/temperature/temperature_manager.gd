class_name TemperatureManager
extends Node

signal temperature_updated(celsius: float)

var current_temperature: float = 18.0

func update_temperature(season: int, hour: int, weather: String) -> float:
	var base := 18.0
	match season:
		0: base = 18.0 # Spring
		1: base = 28.0 # Summer
		2: base = 12.0 # Autumn
		3: base = 0.0  # Winter

	# Diurnal variation: peak at 14:00, coolest at 04:00
	var hour_diff: float = absf(float(hour) - 14.0)
	var diurnal_mod: float = 5.0 - (hour_diff / 10.0) * 10.0

	# Weather effect
	var weather_mod := 0.0
	if weather == "rain":
		weather_mod = -4.0
	elif weather == "fog":
		weather_mod = -2.5
	elif weather == "cloudy":
		weather_mod = -1.5

	current_temperature = snappedf(base + diurnal_mod + weather_mod, 0.1)
	temperature_updated.emit(current_temperature)
	return current_temperature