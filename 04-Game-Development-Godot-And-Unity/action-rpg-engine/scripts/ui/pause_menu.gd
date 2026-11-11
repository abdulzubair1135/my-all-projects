class_name PauseMenu
extends CanvasLayer

signal game_resumed

@onready var menu_panel: Control = $MenuPanel
@onready var resume_btn: Button = $MenuPanel/Center/VBox/ResumeBtn
@onready var save_btn: Button = $MenuPanel/Center/VBox/SaveBtn
@onready var load_btn: Button = $MenuPanel/Center/VBox/LoadBtn
@onready var settings_btn: Button = $MenuPanel/Center/VBox/SettingsBtn
@onready var main_menu_btn: Button = $MenuPanel/Center/VBox/MainMenuBtn

@onready var notify_label: Label = $MenuPanel/Center/VBox/NotificationLabel
@onready var confirm_dialog: Control = $ConfirmDialog
@onready var cancel_exit_btn: Button = $ConfirmDialog/Panel/VBox/HBox/CancelBtn
@onready var save_exit_btn: Button = $ConfirmDialog/Panel/VBox/HBox/SaveExitBtn
@onready var no_save_exit_btn: Button = $ConfirmDialog/Panel/VBox/HBox/NoSaveExitBtn

@onready var save_slots_menu: SaveSlotsMenu = $SaveSlotsMenu
@onready var settings_menu: SettingsMenu = $SettingsMenu

var is_paused: bool = false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	if confirm_dialog:
		confirm_dialog.visible = false
	if notify_label:
		notify_label.visible = false

	if resume_btn and not resume_btn.pressed.is_connected(resume_game):
		resume_btn.pressed.connect(resume_game)
	if save_btn and not save_btn.pressed.is_connected(_on_save_pressed):
		save_btn.pressed.connect(_on_save_pressed)
	if load_btn and not load_btn.pressed.is_connected(_on_load_pressed):
		load_btn.pressed.connect(_on_load_pressed)
	if settings_btn and not settings_btn.pressed.is_connected(_on_settings_pressed):
		settings_btn.pressed.connect(_on_settings_pressed)
	if main_menu_btn and not main_menu_btn.pressed.is_connected(_on_main_menu_pressed):
		main_menu_btn.pressed.connect(_on_main_menu_pressed)

	if cancel_exit_btn and not cancel_exit_btn.pressed.is_connected(_on_cancel_exit):
		cancel_exit_btn.pressed.connect(_on_cancel_exit)
	if save_exit_btn and not save_exit_btn.pressed.is_connected(_on_save_and_exit):
		save_exit_btn.pressed.connect(_on_save_and_exit)
	if no_save_exit_btn and not no_save_exit_btn.pressed.is_connected(_on_exit_without_saving):
		no_save_exit_btn.pressed.connect(_on_exit_without_saving)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") or (event is InputEventKey and event.pressed and not event.echo and event.physical_keycode == KEY_ESCAPE):
		# If sub-dialogs are open, close them first
		if save_slots_menu and save_slots_menu.visible:
			save_slots_menu.close()
			get_viewport().set_input_as_handled()
			return
		if settings_menu and settings_menu.visible:
			settings_menu.close()
			get_viewport().set_input_as_handled()
			return
		if confirm_dialog and confirm_dialog.visible:
			confirm_dialog.visible = false
			get_viewport().set_input_as_handled()
			return

		if is_paused:
			resume_game()
		else:
			pause_game()
		get_viewport().set_input_as_handled()

func pause_game() -> void:
	is_paused = true
	visible = true
	get_tree().paused = true
	if confirm_dialog:
		confirm_dialog.visible = false
	if notify_label:
		notify_label.visible = false

func resume_game() -> void:
	is_paused = false
	visible = false
	get_tree().paused = false
	game_resumed.emit()

func _on_save_pressed() -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if sm:
		var success: bool = sm.autosave()
		if success:
			_show_save_notification("GAME SAVED")
		else:
			_show_save_notification("SAVE FAILED")

func _on_load_pressed() -> void:
	if save_slots_menu:
		save_slots_menu.open(SaveSlotsMenu.Mode.LOAD)

func _on_settings_pressed() -> void:
	if settings_menu:
		settings_menu.open()

func _on_main_menu_pressed() -> void:
	if confirm_dialog:
		confirm_dialog.visible = true

func _on_cancel_exit() -> void:
	if confirm_dialog:
		confirm_dialog.visible = false

func _on_save_and_exit() -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if sm:
		sm.autosave()
	_return_to_main_menu()

func _on_exit_without_saving() -> void:
	_return_to_main_menu()

func _return_to_main_menu() -> void:
	resume_game()
	var st = get_node_or_null("/root/SceneTransition")
	if st and st.has_method("change_scene"):
		st.change_scene("res://scenes/ui/main_menu.tscn", "", false)
	else:
		get_tree().change_scene_to_file("res://scenes/ui/main_menu.tscn")

func _show_save_notification(text: String) -> void:
	if notify_label:
		notify_label.text = text
		notify_label.visible = true
		notify_label.modulate.a = 1.0
		var tween := create_tween()
		tween.tween_interval(1.5)
		tween.tween_property(notify_label, "modulate:a", 0.0, 0.4)
		tween.tween_callback(func(): notify_label.visible = false)
