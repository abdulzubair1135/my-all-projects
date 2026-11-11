extends Control

# Evergreen: After the Fall - Main Menu Controller
# Handles New Game configuration (difficulty, protagonist, relationship), Settings, Credits, and Session Launch

@onready var main_button_container: VBoxContainer = $CenterContainer/MainPanel/ButtonContainer
@onready var new_game_panel: PanelContainer = $NewGameModal
@onready var settings_panel: PanelContainer = $SettingsModal
@onready var credits_panel: PanelContainer = $CreditsModal

# New Game controls
@onready var farm_name_edit: LineEdit = $NewGameModal/Margin/VBox/FarmNameContainer/FarmNameEdit
@onready var difficulty_option: OptionButton = $NewGameModal/Margin/VBox/DifficultyContainer/DifficultyOption
@onready var relationship_option: OptionButton = $NewGameModal/Margin/VBox/RelationContainer/RelationOption
@onready var archi_button: Button = $NewGameModal/Margin/VBox/ProtagonistSelection/HBox/ArchiCard
@onready var danish_button: Button = $NewGameModal/Margin/VBox/ProtagonistSelection/HBox/DanishCard
@onready var selected_protagonist_desc: Label = $NewGameModal/Margin/VBox/SelectedCharDesc

var chosen_protagonist: String = GameState.PROTAGONIST_ARCHI

func _ready() -> void:
	_setup_options()
	_update_character_selection_ui()
	
	new_game_panel.visible = false
	settings_panel.visible = false
	credits_panel.visible = false

func _setup_options() -> void:
	if difficulty_option:
		difficulty_option.clear()
		difficulty_option.add_item("Story Mode (Forgiving survival, rich resources)")
		difficulty_option.add_item("Normal Mode (Balanced intended experience)")
		difficulty_option.add_item("Survivor Mode (Scarce supplies, severe threats)")
		difficulty_option.add_item("Nightmare Mode (Maximum horde intensity)")
		difficulty_option.select(1)
	
	if relationship_option:
		relationship_option.clear()
		relationship_option.add_item("Established Partners (Close trust from the start)")
		relationship_option.add_item("Developing Bonds (Build trust through shared hardship)")
		relationship_option.select(0)

func _on_new_game_pressed() -> void:
	new_game_panel.visible = true
	settings_panel.visible = false
	credits_panel.visible = false

func _on_select_archi_pressed() -> void:
	chosen_protagonist = GameState.PROTAGONIST_ARCHI
	_update_character_selection_ui()

func _on_select_danish_pressed() -> void:
	chosen_protagonist = GameState.PROTAGONIST_DANISH
	_update_character_selection_ui()

func _update_character_selection_ui() -> void:
	if chosen_protagonist == GameState.PROTAGONIST_ARCHI:
		archi_button.button_pressed = true
		danish_button.button_pressed = false
		selected_protagonist_desc.text = "ARCHI: Farming & Medical specialist. Agile combat style. Starts with 'Green Thumb' crop efficiency bonus."
	else:
		archi_button.button_pressed = false
		danish_button.button_pressed = true
		selected_protagonist_desc.text = "DANISH: Combat & Construction specialist. Heavy weapons and repairs. Starts with 'Field Engineer' defense bonus."

func _on_start_game_confirmed() -> void:
	GameState.current_protagonist = chosen_protagonist
	if farm_name_edit and farm_name_edit.text.strip_edges() != "":
		GameState.farm_name = farm_name_edit.text.strip_edges()
	
	var diff_map = ["Story", "Normal", "Survivor", "Nightmare"]
	if difficulty_option:
		GameState.difficulty = diff_map[difficulty_option.selected]
	
	print("[MainMenu] Starting game as %s on %s mode at '%s'" % [GameState.current_protagonist, GameState.difficulty, GameState.farm_name])
	get_tree().change_scene_to_file.call_deferred("res://scenes/world/EvergreenFarm.tscn")

func _on_continue_pressed() -> void:
	if SaveService.has_save(1):
		print("[MainMenu] Continuing from Save Slot 1...")
		SaveService.load_game(1)
	get_tree().change_scene_to_file.call_deferred("res://scenes/world/EvergreenFarm.tscn")

func _on_settings_pressed() -> void:
	settings_panel.visible = true
	new_game_panel.visible = false
	credits_panel.visible = false

func _on_credits_pressed() -> void:
	credits_panel.visible = true
	new_game_panel.visible = false
	settings_panel.visible = false

func _on_close_modal_pressed() -> void:
	new_game_panel.visible = false
	settings_panel.visible = false
	credits_panel.visible = false

func _on_exit_pressed() -> void:
	get_tree().quit()
