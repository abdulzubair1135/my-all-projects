class_name DeathScreen
extends CanvasLayer

@onready var color_rect: ColorRect = $ColorRect
@onready var restart_button: Button = $ColorRect/CenterContainer/VBoxContainer/RestartButton

func _ready() -> void:
	visible = false
	if restart_button and not restart_button.pressed.is_connected(_on_restart_pressed):
		restart_button.pressed.connect(_on_restart_pressed)

func show_death_screen() -> void:
	visible = true
	color_rect.modulate = Color(1, 1, 1, 0)
	var tween := create_tween()
	tween.tween_property(color_rect, "modulate", Color(1, 1, 1, 1), 0.8)

func _on_restart_pressed() -> void:
	visible = false
	var gs = get_node_or_null("/root/GameState")
	if gs:
		gs.pending_player_restore = {
			"health": 100.0,
			"max_health": 100.0,
			"stamina": 100.0,
			"max_stamina": 100.0
		}
		var target_scene: String = gs.current_scene if not gs.current_scene.is_empty() else "res://scenes/world/home/shelter.tscn"
		var target_spawn: String = gs.current_spawn_id if not gs.current_spawn_id.is_empty() else "spawn_home"
		var st = get_node_or_null("/root/SceneTransition")
		if st and st.has_method("change_scene"):
			st.change_scene(target_scene, target_spawn, true)
			return
		else:
			get_tree().change_scene_to_file(target_scene)
			return
	get_tree().reload_current_scene()
