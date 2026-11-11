class_name SettingsMenu
extends CanvasLayer

signal back_pressed

@onready var volume_slider: HSlider = $ColorRect/CenterContainer/VBoxContainer/VolumeRow/VolumeSlider
@onready var fullscreen_checkbox: CheckBox = $ColorRect/CenterContainer/VBoxContainer/FullscreenRow/FullscreenCheck
@onready var back_button: Button = $ColorRect/CenterContainer/VBoxContainer/BackButton

func _ready() -> void:
	visible = false
	if back_button and not back_button.pressed.is_connected(_on_back_pressed):
		back_button.pressed.connect(_on_back_pressed)
	if volume_slider and not volume_slider.value_changed.is_connected(_on_volume_changed):
		volume_slider.value_changed.connect(_on_volume_changed)
	if fullscreen_checkbox and not fullscreen_checkbox.toggled.is_connected(_on_fullscreen_toggled):
		fullscreen_checkbox.toggled.connect(_on_fullscreen_toggled)

func open() -> void:
	visible = true
	_load_current_settings()

func close() -> void:
	visible = false

func _load_current_settings() -> void:
	var state = get_node_or_null("/root/GameState")
	if state:
		if volume_slider:
			volume_slider.value = state.settings.get("master_volume", 1.0) * 100.0
		if fullscreen_checkbox:
			fullscreen_checkbox.button_pressed = state.settings.get("fullscreen", false)

func _on_volume_changed(val: float) -> void:
	var norm := val / 100.0
	var state = get_node_or_null("/root/GameState")
	if state:
		state.settings["master_volume"] = norm
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index("Master"), linear_to_db(norm))

func _on_fullscreen_toggled(toggled: bool) -> void:
	var state = get_node_or_null("/root/GameState")
	if state:
		state.settings["fullscreen"] = toggled
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if toggled else DisplayServer.WINDOW_MODE_WINDOWED)

func _on_back_pressed() -> void:
	close()
	back_pressed.emit()
