extends CanvasLayer
class_name HUDController

# Evergreen: After the Fall - HUD & Dialogue UI Controller
# Manages health/stamina meters, clock, notifications, dialogue box, and quickslots

@onready var portrait_rect: TextureRect = $TopLeft/HBox/PortraitFrame/Portrait
@onready var name_label: Label = $TopLeft/HBox/VBox/NameLabel
@onready var role_label: Label = $TopLeft/HBox/VBox/RoleLabel
@onready var health_bar: ProgressBar = $TopLeft/HBox/VBox/HealthBar
@onready var stamina_bar: ProgressBar = $TopLeft/HBox/VBox/StaminaBar

@onready var time_label: Label = $TopRight/TimePanel/VBox/TimeLabel
@onready var day_label: Label = $TopRight/TimePanel/VBox/DayLabel

@onready var notify_banner: PanelContainer = $NotificationBanner
@onready var notify_label: Label = $NotificationBanner/Margin/Label

@onready var dialog_box: PanelContainer = $DialogBox
@onready var dialog_speaker: Label = $DialogBox/Margin/VBox/Speaker
@onready var dialog_text: Label = $DialogBox/Margin/VBox/Text
@onready var dialog_prompt: Label = $DialogBox/Margin/VBox/Prompt
@onready var quickbar_slots: Array[Label] = [
	$QuickBar/HBox/Slot1,
	$QuickBar/HBox/Slot2,
	$QuickBar/HBox/Slot3,
	$QuickBar/HBox/Slot4,
	$QuickBar/HBox/Slot5
]

var notify_timer: float = 0.0
var active_dialog_lines: Array = []
var active_dialog_index: int = 0
var is_dialog_active: bool = false

func _ready() -> void:
	# Connect to EventBus
	EventBus.protagonist_switched.connect(_on_protagonist_switched)
	EventBus.health_changed.connect(_on_health_changed)
	EventBus.stamina_changed.connect(_on_stamina_changed)
	EventBus.time_updated.connect(_on_time_updated)
	EventBus.notification_requested.connect(show_notification)
	EventBus.dialog_started.connect(start_dialog)
	EventBus.inventory_updated.connect(_update_quickbar_ui)
	
	if notify_banner:
		notify_banner.visible = false
	if dialog_box:
		dialog_box.visible = false
	
	_refresh_protagonist_ui()
	_update_quickbar_ui()
	_update_clock_ui(GameState.current_hour, GameState.current_minute, GameState.current_day, GameState.current_season)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1:
				InventoryService.select_slot(0)
			KEY_2:
				InventoryService.select_slot(1)
			KEY_3:
				InventoryService.select_slot(2)
			KEY_4:
				InventoryService.select_slot(3)
			KEY_5:
				InventoryService.select_slot(4)
			KEY_Q:
				InventoryService.select_slot((InventoryService.active_slot_index + 1) % 5)

func _update_quickbar_ui() -> void:
	for i in range(quickbar_slots.size()):
		var slot_label = quickbar_slots[i]
		if not is_instance_valid(slot_label):
			continue
		
		var is_active = (i == InventoryService.active_slot_index)
		if i < InventoryService.slots.size() and not InventoryService.slots[i].is_empty():
			var slot_data = InventoryService.slots[i]
			var item_id = slot_data.get("item_id", "")
			var count = slot_data.get("count", 1)
			var item_name = InventoryService.item_database.get(item_id, {}).get("name", item_id)
			var short_name = item_name
			if item_name.begins_with("Field "):
				short_name = "Hoe"
			elif item_name.begins_with("Watering "):
				short_name = "Can"
			elif item_name.begins_with("Sturdy "):
				short_name = "Blade"
			elif item_name.begins_with("Hunting "):
				short_name = "Rifle"
			else:
				short_name = item_name.split(" ")[0]
				
			if count > 1:
				slot_label.text = "[%d] %s x%d" % [i + 1, short_name, count]
			else:
				slot_label.text = "[%d] %s" % [i + 1, short_name]
		else:
			slot_label.text = "[%d] --" % [i + 1]
		
		# Active slot highlight
		if is_active:
			slot_label.add_theme_color_override("font_color", Color(1.0, 0.9, 0.35))
		else:
			slot_label.add_theme_color_override("font_color", Color(0.75, 0.78, 0.82))

func _process(delta: float) -> void:
	if notify_banner and notify_banner.visible:
		notify_timer -= delta
		if notify_timer <= 0.0:
			notify_banner.visible = false
	
	if is_dialog_active and (Input.is_action_just_pressed("interact") or Input.is_action_just_pressed("ui_accept")):
		_advance_dialog()

func _refresh_protagonist_ui() -> void:
	var stats = GameState.get_current_stats()
	name_label.text = stats["name"]
	role_label.text = stats["title"]
	
	if ResourceLoader.exists(stats["portrait_path"]):
		portrait_rect.texture = load(stats["portrait_path"])
	
	health_bar.max_value = stats["max_health"]
	health_bar.value = stats["health"]
	
	stamina_bar.max_value = stats["max_stamina"]
	stamina_bar.value = stats["stamina"]

func _on_protagonist_switched(_protagonist: String) -> void:
	_refresh_protagonist_ui()

func _on_health_changed(current: float, max_h: float) -> void:
	health_bar.max_value = max_h
	health_bar.value = current

func _on_stamina_changed(current: float, max_s: float) -> void:
	stamina_bar.max_value = max_s
	stamina_bar.value = current

func _on_time_updated(hour: int, minute: int, day: int, season: String) -> void:
	_update_clock_ui(hour, minute, day, season)

func _update_clock_ui(hour: int, minute: int, day: int, season: String) -> void:
	var ampm = "AM" if hour < 12 else "PM"
	var display_hour = hour % 12
	if display_hour == 0:
		display_hour = 12
	time_label.text = "%02d:%02d %s" % [display_hour, minute, ampm]
	day_label.text = "Day %d  •  %s" % [day, season]

func show_notification(message: String, duration: float = 2.5) -> void:
	if notify_banner and notify_label:
		notify_label.text = message
		notify_banner.visible = true
		notify_timer = duration

func start_dialog(_speaker_id: String, lines: Array) -> void:
	active_dialog_lines = lines
	active_dialog_index = 0
	is_dialog_active = true
	dialog_box.visible = true
	_render_dialog_line()

func _render_dialog_line() -> void:
	if active_dialog_index < active_dialog_lines.size():
		var line: String = str(active_dialog_lines[active_dialog_index])
		if line.contains(":"):
			var parts = line.split(":", true, 1)
			dialog_speaker.text = parts[0].strip_edges()
			dialog_text.text = parts[1].strip_edges().trim_prefix("'").trim_suffix("'")
		else:
			dialog_speaker.text = "Evergreen"
			dialog_text.text = line
		dialog_prompt.text = "[E / Space] Next >>" if (active_dialog_index < active_dialog_lines.size() - 1) else "[E / Space] Close"
	else:
		_end_dialog()

func _advance_dialog() -> void:
	active_dialog_index += 1
	if active_dialog_index >= active_dialog_lines.size():
		_end_dialog()
	else:
		_render_dialog_line()

func _end_dialog() -> void:
	is_dialog_active = false
	if dialog_box:
		dialog_box.visible = false
	EventBus.dialog_ended.emit()
