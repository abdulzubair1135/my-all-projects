class_name SaveSlotsMenu
extends CanvasLayer

signal slot_selected(slot_id: String)
signal back_pressed

enum Mode {
	LOAD,
	SAVE
}

var current_mode: Mode = Mode.LOAD
var pending_delete_slot: String = ""

@onready var title_label: Label = $ColorRect/CenterContainer/VBoxContainer/Title
@onready var slots_container: VBoxContainer = $ColorRect/CenterContainer/VBoxContainer/SlotsContainer
@onready var back_button: Button = $ColorRect/CenterContainer/VBoxContainer/BackButton

@onready var confirm_dialog: Control = $ConfirmDialog
@onready var confirm_label: Label = $ConfirmDialog/Panel/VBoxContainer/Label
@onready var confirm_delete_btn: Button = $ConfirmDialog/Panel/VBoxContainer/HBox/DeleteBtn
@onready var cancel_delete_btn: Button = $ConfirmDialog/Panel/VBoxContainer/HBox/CancelBtn

func _ready() -> void:
	visible = false
	if confirm_dialog:
		confirm_dialog.visible = false
	if back_button and not back_button.pressed.is_connected(_on_back_pressed):
		back_button.pressed.connect(_on_back_pressed)
	if confirm_delete_btn and not confirm_delete_btn.pressed.is_connected(_on_confirm_delete):
		confirm_delete_btn.pressed.connect(_on_confirm_delete)
	if cancel_delete_btn and not cancel_delete_btn.pressed.is_connected(_on_cancel_delete):
		cancel_delete_btn.pressed.connect(_on_cancel_delete)

func open(mode: Mode = Mode.LOAD) -> void:
	current_mode = mode
	visible = true
	if confirm_dialog:
		confirm_dialog.visible = false
	title_label.text = "SELECT SAVE SLOT" if current_mode == Mode.SAVE else "LOAD SAVED GAME"
	refresh_slots()

func close() -> void:
	visible = false

func refresh_slots() -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if not sm:
		return

	for i in range(1, 4):
		var slot_id := "slot_%d" % i
		var card: PanelContainer = slots_container.get_node_or_null("Slot%d" % i) as PanelContainer
		if not card:
			continue

		var meta: Dictionary = sm.get_save_metadata(slot_id)
		var info_label: Label = card.get_node("Margin/HBox/InfoBox/InfoLabel")
		var title_sub: Label = card.get_node("Margin/HBox/InfoBox/SlotTitle")
		var action_btn: Button = card.get_node("Margin/HBox/Buttons/ActionBtn")
		var delete_btn: Button = card.get_node("Margin/HBox/Buttons/DeleteBtn")

		title_sub.text = "SLOT %d" % i

		# Disconnect old calls
		if action_btn.pressed.is_connected(_on_slot_action):
			action_btn.pressed.disconnect(_on_slot_action)
		if delete_btn.pressed.is_connected(_on_slot_delete):
			delete_btn.pressed.disconnect(_on_slot_delete)

		action_btn.pressed.connect(_on_slot_action.bind(slot_id))
		delete_btn.pressed.connect(_on_slot_delete.bind(slot_id))

		if not meta.get("exists", false):
			info_label.text = "EMPTY SLOT"
			delete_btn.visible = false
			if current_mode == Mode.LOAD:
				action_btn.text = "[ EMPTY ]"
				action_btn.disabled = true
			else:
				action_btn.text = "[ SAVE ]"
				action_btn.disabled = false
		else:
			var day: int = meta.get("game_day", 1)
			var scene_str: String = meta.get("current_scene", "Shelter")
			var loc: String = "Ruined Shelter" if "shelter" in scene_str.to_lower() else "Ruined Courtyard"
			var time_sec: int = meta.get("timestamp", 0)
			var time_dict := Time.get_datetime_dict_from_unix_time(time_sec)
			var time_str := "%04d-%02d-%02d %02d:%02d" % [time_dict.year, time_dict.month, time_dict.day, time_dict.hour, time_dict.minute]

			info_label.text = "Day %d — %s\nSaved: %s" % [day, loc, time_str]
			delete_btn.visible = true
			action_btn.disabled = false
			action_btn.text = "[ OVERWRITE ]" if current_mode == Mode.SAVE else "[ LOAD ]"

func _on_slot_action(slot_id: String) -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if not sm:
		return

	if current_mode == Mode.SAVE:
		sm.save_game(slot_id)
		refresh_slots()
		slot_selected.emit(slot_id)
		close()
	else:
		# Mode.LOAD
		if sm.has_save(slot_id):
			var data: Dictionary = sm.load_game(slot_id)
			if data.size() > 0:
				var world_data: Dictionary = data.get("world", {})
				var target_scene: String = world_data.get("current_scene", "res://scenes/world/home/shelter.tscn")
				var target_spawn: String = world_data.get("current_spawn_id", "spawn_home")
				close()
				var st = get_node_or_null("/root/SceneTransition")
				if st and st.has_method("change_scene"):
					st.change_scene(target_scene, target_spawn, false)
				else:
					get_tree().change_scene_to_file(target_scene)
				slot_selected.emit(slot_id)

func _on_slot_delete(slot_id: String) -> void:
	pending_delete_slot = slot_id
	if confirm_dialog:
		confirm_dialog.visible = true
		confirm_label.text = "Delete save data in %s?" % slot_id.to_upper().replace("_", " ")

func _on_confirm_delete() -> void:
	var sm = get_node_or_null("/root/SaveManager")
	if pending_delete_slot != "" and sm:
		sm.delete_save(pending_delete_slot)
		pending_delete_slot = ""
	if confirm_dialog:
		confirm_dialog.visible = false
	refresh_slots()

func _on_cancel_delete() -> void:
	pending_delete_slot = ""
	if confirm_dialog:
		confirm_dialog.visible = false

func _on_back_pressed() -> void:
	close()
	back_pressed.emit()
