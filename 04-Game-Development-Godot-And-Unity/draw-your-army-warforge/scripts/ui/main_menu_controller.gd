class_name MainMenuController
extends Control

@onready var title_label: Label = $DecorPanel/MarginContainer/VBoxContainer/TitleLabel
@onready var subtitle_label: Label = $DecorPanel/MarginContainer/VBoxContainer/SubtitleLabel
@onready var btn_practice: Button = $DecorPanel/MarginContainer/VBoxContainer/BtnPractice
@onready var btn_workshop: Button = $DecorPanel/MarginContainer/VBoxContainer/BtnWorkshop
@onready var btn_creator: Button = $DecorPanel/MarginContainer/VBoxContainer/BtnCreator
@onready var btn_settings: Button = $DecorPanel/MarginContainer/VBoxContainer/BtnSettings
@onready var btn_exit: Button = $DecorPanel/MarginContainer/VBoxContainer/BtnExit

func _ready() -> void:
	title_label.text = GameManager.GAME_TITLE.to_upper()
	subtitle_label.text = "AUTONOMOUS TACTICAL COMBAT & ARMY BUILDER"
	
	btn_practice.pressed.connect(_on_practice_pressed)
	btn_workshop.pressed.connect(_on_workshop_pressed)
	btn_creator.pressed.connect(_on_creator_pressed)
	btn_settings.pressed.connect(_on_settings_pressed)
	btn_exit.pressed.connect(_on_exit_pressed)

func _on_practice_pressed() -> void:
	GameManager.current_mode = GameManager.GameMode.OFFLINE_PRACTICE
	GameManager.change_scene("res://scenes/battlefield/battlefield.tscn")

func _on_workshop_pressed() -> void:
	GameManager.current_mode = GameManager.GameMode.CREATIVE_WORKSHOP
	GameManager.change_scene("res://scenes/army_workshop/army_workshop.tscn")

func _on_creator_pressed() -> void:
	GameManager.change_scene("res://scenes/soldier_creator/soldier_creator.tscn")

func _on_settings_pressed() -> void:
	# Show notification or toggle settings modal
	pass

func _on_exit_pressed() -> void:
	get_tree().quit()
