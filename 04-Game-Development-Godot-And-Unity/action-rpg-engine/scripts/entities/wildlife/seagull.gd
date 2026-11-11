class_name Seagull
extends WildlifeBase

var is_flying: bool = false

func _ready() -> void:
	wander_speed = 22.0
	flee_speed = 80.0
	detection_radius = 85.0
	super._ready()
	if sprite:
		sprite.texture = preload("res://assets/environment/wildlife_sprites.png")
		sprite.region_enabled = true
		sprite.region_rect = Rect2(0, 0, 16, 16)

func _update_state(delta: float) -> void:
	super._update_state(delta)
	if sprite:
		if current_state == State.FLEE:
			# Flying frame
			sprite.region_rect = Rect2(32, 0, 24, 24)
		else:
			sprite.region_rect = Rect2(0, 0, 16, 16)