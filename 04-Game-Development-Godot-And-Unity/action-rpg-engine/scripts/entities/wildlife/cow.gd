class_name Cow
extends WildlifeBase

func _ready() -> void:
	wander_speed = 12.0
	flee_speed = 30.0
	detection_radius = 50.0
	super._ready()
	if sprite:
		sprite.texture = preload("res://assets/environment/wildlife_sprites.png")
		sprite.region_enabled = true
		sprite.region_rect = Rect2(0, 64, 48, 48)

func _update_state(delta: float) -> void:
	super._update_state(delta)
	if sprite:
		sprite.region_rect = Rect2(0, 64, 48, 48)
