class_name Interactable
extends Area2D

signal interacted(player: Player)
signal player_entered(player: Player)
signal player_exited(player: Player)

@export var prompt_text: String = "E — Interact"
@export var enabled: bool = true
@export var prompt_offset: Vector2 = Vector2(0, -22)

var current_player: Player = null
var label_node: Label = null

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2 # Player body layer
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_setup_prompt_label()

func _setup_prompt_label() -> void:
	label_node = Label.new()
	label_node.text = prompt_text
	label_node.position = prompt_offset - Vector2(40, 6)
	label_node.custom_minimum_size = Vector2(80, 14)
	label_node.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label_node.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label_node.visible = false

	var settings := LabelSettings.new()
	settings.font_size = 7
	settings.outline_size = 2
	settings.outline_color = Color(0.08, 0.08, 0.1, 1.0)
	settings.font_color = Color(1.0, 0.9, 0.6, 1.0)
	label_node.label_settings = settings

	add_child(label_node)

func _unhandled_input(event: InputEvent) -> void:
	if not enabled or not current_player:
		return
	if event.is_action_pressed("interact"):
		trigger_interaction(current_player)
		get_viewport().set_input_as_handled()

func trigger_interaction(player: Player) -> void:
	if not enabled or not player:
		return
	interacted.emit(player)
	print("[Interactable] Interacted with: %s" % prompt_text)

func update_prompt(new_text: String) -> void:
	prompt_text = new_text
	if label_node:
		label_node.text = new_text

func _on_body_entered(body: Node2D) -> void:
	if body is Player and enabled:
		current_player = body as Player
		if label_node:
			label_node.text = prompt_text
			label_node.visible = true
		player_entered.emit(current_player)

func _on_body_exited(body: Node2D) -> void:
	if body == current_player:
		current_player = null
		if label_node:
			label_node.visible = false
		player_exited.emit(body as Player)
