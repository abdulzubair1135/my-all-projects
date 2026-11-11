class_name Crab
extends WildlifeBase

func _ready() -> void:
	wander_speed = 18.0
	flee_speed = 45.0
	detection_radius = 65.0
	super._ready()
	if sprite:
		sprite.texture = preload("res://assets/environment/wildlife_sprites.png")
		sprite.region_enabled = true
		sprite.region_rect = Rect2(0, 32, 16, 16)