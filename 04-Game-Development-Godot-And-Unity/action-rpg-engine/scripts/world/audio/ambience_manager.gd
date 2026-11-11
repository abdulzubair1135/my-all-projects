class_name AmbienceManager
extends Node

var wave_player: AudioStreamPlayer = null
var wind_player: AudioStreamPlayer = null

func _ready() -> void:
	# Architectural placeholder for ocean surf and coastal wind
	pass

func set_zone(zone_name: String) -> void:
	# Future audio cross-fading
	print("[AmbienceManager] Zone active: ", zone_name)