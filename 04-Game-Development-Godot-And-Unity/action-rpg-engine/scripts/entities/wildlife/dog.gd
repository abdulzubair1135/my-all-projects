class_name Dog
extends WildlifeBase

func _ready() -> void:
	wander_speed = 35.0
	flee_speed = 95.0
	detection_radius = 90.0
	super._ready()
	if sprite:
		sprite.texture = preload("res://assets/environment/wildlife_sprites.png")
		sprite.region_enabled = true
		sprite.region_rect = Rect2(64, 64, 48, 48)

func _update_state(delta: float) -> void:
	super._update_state(delta)
	if sprite:
		sprite.region_rect = Rect2(64, 64, 48, 48)
