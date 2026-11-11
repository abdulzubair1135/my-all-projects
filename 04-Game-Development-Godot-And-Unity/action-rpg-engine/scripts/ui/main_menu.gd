class_name MainMenu
extends Control

@onready var new_game_btn: Button = $CenterContainer/VBoxContainer/Buttons/NewGameBtn
@onready var continue_btn: Button = $CenterContainer/VBoxContainer/Buttons/ContinueBtn
@onready var load_btn: Button = $CenterContainer/VBoxContainer/Buttons/LoadBtn
@onready var settings_btn: Button = $CenterContainer/VBoxContainer/Buttons/SettingsBtn
@onready var quit_btn: Button = $CenterContainer/VBoxContainer/Buttons/QuitBtn

@onready var intro_panel: Control = $IntroDialog
@onready var begin_btn: Button = $IntroDialog/Panel/VBox/BeginBtn
@onready var cancel_intro_btn: Button = $IntroDialog/Panel/VBox/CancelBtn

@onready var save_slots_menu: SaveSlotsMenu = $SaveSlotsMenu
@onready var settings_menu: SettingsMenu = $SettingsMenu

func _ready() -> void:
	if intro_panel:
		intro_panel.visible = false

	if new_game_btn and not new_game_btn.pressed.is_connected(_on_new_game_pressed):
		new_game_btn.pressed.connect(_on_new_game_pressed)
	if continue_btn and not continue_btn.pressed.is_connected(_on_continue_pressed):
		continue_btn.pressed.connect(_on_continue_pressed)
	if load_btn and not load_btn.pressed.is_connected(_on_load_pressed):
		load_btn.pressed.connect(_on_load_pressed)
	if settings_btn and not settings_btn.pressed.is_connected(_on_settings_pressed):
		settings_btn.pressed.connect(_on_settings_pressed)
	if quit_btn and not quit_btn.pressed.is_connected(_on_quit_pressed):
		quit_btn.pressed.connect(_on_quit_pressed)

	if begin_btn and not begin_btn.pressed.is_connected(_on_begin_new_game):
		begin_btn.pressed.connect(_on_begin_new_game)
	if cancel_intro_btn and not cancel_intro_btn.pressed.is_connected(_on_cancel_intro):
		cancel_intro_btn.pressed.connect(_on_cancel_intro)

	_update_continue_button()

func _update_continue_button() -> void:
	if not continue_btn:
		return
	var sm = get_node_or_null("/root/SaveManager")
	if sm:
		var latest_slot: String = sm.get_latest_save()
		continue_btn.disabled = (latest_slot == "")
	else:
		continue_btn.disabled = true

func _on_new_game_pressed() -> void:
	if intro_panel:
		intro_panel.visible = true

func _on_cancel_intro() -> void:
	if intro_panel:
		intro_panel.visible = false

func _on_begin_new_game() -> void:
	if intro_panel:
		intro_panel.visible = false

	var sm = get_node_or_null("/root/SaveManager")
	if sm:
		sm.create_new_game("slot_1")

	var gs = get_node_or_null("/root/GameState")
	if gs:
		gs.current_scene = "res://scenes/world/shore/the_shore.tscn"
		gs.current_spawn_id = "spawn_shore"

	var st = get_node_or_null("/root/SceneTransition")
	if st and st.has_method("change_scene"):
		st.change_scene("res://scenes/world/shore/the_shore.tscn", "spawn_shore", false)
	else:
		get_tree().change_scene_to_file("res://scenes/world/shore/the_shore.tscn")

func _on_continue_pressed() -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if not sm:
		return
	var latest_slot: String = sm.get_latest_save()
	if latest_slot != "":
		var data: Dictionary = sm.load_game(latest_slot)
		if data.size() > 0:
			var world_data: Dictionary = data.get("world", {})
			var target_scene: String = world_data.get("current_scene", "res://scenes/world/home/shelter.tscn")
			var target_spawn: String = world_data.get("current_spawn_id", "spawn_home")
			var st = get_node_or_null("/root/SceneTransition")
			if st and st.has_method("change_scene"):
				st.change_scene(target_scene, target_spawn, false)
			else:
				get_tree().change_scene_to_file(target_scene)

func _on_load_pressed() -> void:
	if save_slots_menu:
		save_slots_menu.open(SaveSlotsMenu.Mode.LOAD)

func _on_settings_pressed() -> void:
	if settings_menu:
		settings_menu.open()

func _on_quit_pressed() -> void:
	get_tree().quit()
