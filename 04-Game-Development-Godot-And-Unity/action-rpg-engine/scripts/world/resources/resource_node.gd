class_name ResourceNode
extends Area2D

signal harvested(resource_id: String, amount: int)

@export var resource_id: String = "driftwood"
@export var display_name: String = "Driftwood Branch"
@export var amount: int = 1
@export var respawn_time: float = 120.0
@export var prompt_offset: Vector2 = Vector2(0, -16)

var is_depleted: bool = false
var player_in_range: Player = null
var label: Label = null

func _ready() -> void:
	collision_layer = 0
	collision_mask = 2 # Detect Player
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	_setup_prompt_label()

func _setup_prompt_label() -> void:
	label = Label.new()
	label.text = "E — Examine " + display_name
	label.visible = false
	label.position = prompt_offset + Vector2(-40, -10)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER

	var settings := LabelSettings.new()
	settings.font_size = 8
	settings.font_color = Color(1.0, 0.95, 0.75, 1.0)
	settings.outline_size = 2
	settings.outline_color = Color(0.1, 0.1, 0.14, 1.0)
	label.label_settings = settings
	add_child(label)

func _unhandled_input(event: InputEvent) -> void:
	if player_in_range and event.is_action_pressed("interact"):
		interact(player_in_range)
		get_viewport().set_input_as_handled()

func interact(p: Player) -> void:
	if is_depleted:
		return
	print("[ResourceNode] Examined: %s (Gathering coming soon)" % display_name)
	harvested.emit(resource_id, amount)
	if p.has_node("HUD/NotificationLabel"):
		var nl: Label = p.get_node("HUD/NotificationLabel") as Label
		nl.text = "%s — Gathering coming in next milestone." % display_name
		nl.visible = true

func _on_body_entered(body: Node2D) -> void:
	if body is Player:
		player_in_range = body as Player
		if label and not is_depleted:
			label.visible = true

func _on_body_exited(body: Node2D) -> void:
	if body is Player:
		player_in_range = null
		if label:
			label.visible = false