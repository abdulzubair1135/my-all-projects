extends Area2D
class_name Interactable

# Evergreen: After the Fall - Generic Interactable Area
# Connects world objects (doors, wells, chests, NPCs) to player interaction

@export var interactable_id: String = "generic_prop"
@export var display_name: String = "Object"
@export var prompt_text: String = "Interact"
@export var action_type: String = "dialog"
@export var dialog_lines: Array[String] = ["It's a quiet morning in Evergreen."]

func _ready() -> void:
	add_to_group("interactables")
	# Interaction areas reside on collision layer 2
	collision_layer = 2
	collision_mask = 0

func get_interaction_info() -> Dictionary:
	return {
		"id": interactable_id,
		"name": display_name,
		"prompt": prompt_text
	}

func interact(player: Node2D) -> void:
	print("[Interactable] Player interacted with: %s (%s)" % [display_name, action_type])
	
	match action_type:
		"water_well":
			GameState.restore_stamina(40.0)
			EventBus.notification_requested.emit("Drank cool, fresh water from the well. Stamina restored!", 2.5)
		"storage_chest":
			var count = InventoryService.get_item_count("seed_turnip")
			EventBus.notification_requested.emit("Farm Supply Chest: Wood, Stone, and Seeds stored. (Turnip seeds in inventory: %d)" % count, 2.5)
		"farmhouse_door":
			var farm = player.get_tree().current_scene
			if farm and farm.has_method("trigger_sleep"):
				farm.trigger_sleep()
			else:
				EventBus.notification_requested.emit("Farmhouse Interior: Safe resting point. Press TAB to switch protagonist.", 3.0)
		"companion_talk":
			_trigger_companion_dialogue()
		"signpost":
			EventBus.notification_requested.emit("Signpost: 'Evergreen Farm - Est. 1994. North: Village. East: Greenwood Forest.'", 3.5)
		_:
			if not dialog_lines.is_empty():
				EventBus.dialog_started.emit(interactable_id, dialog_lines)

func _trigger_companion_dialogue() -> void:
	var active = InventoryService.get_active_item()
	if not active.is_empty():
		if active.get("category") == "Food":
			if RelationshipService.share_meal():
				return
		elif active.get("category") in ["Produce", "Material", "Medical", "Defense"]:
			if RelationshipService.give_companion_gift(active["id"]):
				return
	
	var current = GameState.current_protagonist
	var lines: Array[String] = []
	var summary = RelationshipService.get_summary()
	
	if current == GameState.PROTAGONIST_ARCHI:
		lines = [
			"Danish: 'Hey Archi. The perimeter is holding. Watching your back out here gives me purpose.'",
			"Danish: 'If you want to rest or switch tasks, just step inside the farmhouse (Press TAB).'",
			"Danish: '(Trust: %d • Closeness: %d • Respect: %d)'" % [summary["trust"], summary["closeness"], summary["respect"]]
		]
	else:
		lines = [
			"Archi: 'Danish... I know how much you carry to keep us safe. Don't forget you don't have to carry it alone.'",
			"Archi: 'The farm is coming together. A real home, after everything we survived.'",
			"Archi: '(Trust: %d • Closeness: %d • Respect: %d)'" % [summary["trust"], summary["closeness"], summary["respect"]]
		]
	
	RelationshipService.add_closeness(2)
	EventBus.dialog_started.emit("companion", lines)
