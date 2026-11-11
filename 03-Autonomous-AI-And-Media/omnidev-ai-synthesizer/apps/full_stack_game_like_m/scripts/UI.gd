extends CanvasLayer

# UI Elements
@export var health_bar: ProgressBar
@export var hunger_bar: ProgressBar
@export var exp_bar: ProgressBar
@export var level_label: Label
@export var block_counter: Label
@export var title_label: Label
@export var version_label: Label
@export var quit_timer_label: Label
@export var camera_view_label: Label
@export var character_preview: ColorRect
@export var character_name_label: Label

# Hotbar
@export var hotbar_container: HBoxContainer
var hotbar_slots = []

# Menus
@export var start_menu: Panel
@export var pause_menu: Panel
@export var quit_menu: Panel
@export var character_menu: Panel

# Inventory and Chest panels (created dynamically)
var inventory_panel: Panel
var chest_panel: Panel
var inventory_grid: GridContainer
var chest_grid: GridContainer
var inventory_slots = []
var chest_slots = []
var player_inventory_ref: Array = []
var chest_inventory_ref: Array = []

# Dark theme colors
const DARK_BG = Color(0.04, 0.04, 0.08, 0.96)
const DARK_PANEL = Color(0.08, 0.08, 0.14, 0.98)
const ACCENT_COLOR = Color(0.3, 0.6, 0.9)
const TEXT_COLOR = Color(0.85, 0.85, 0.92)
const DANGER_COLOR = Color(0.9, 0.2, 0.2)

# Quit timer
var quit_timer: float = 0.0
var quit_confirm_delay: float = 2.0
var quit_confirm_active: bool = false

# Character selection
var current_color_index: int = 0
var color_options: Array = ["default", "light", "dark", "red", "blue", "green"]
var color_display_names: Array = ["Default", "Light", "Dark", "Red", "Blue", "Green"]

func _ready():
	apply_dark_theme()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	setup_hotbar()
	setup_character_menu()
	setup_inventory_panel()
	setup_chest_panel()

	if start_menu:
		start_menu.visible = true
		if title_label:
			title_label.text = "🌑 VOXEL WORLD"
		if version_label:
			version_label.text = "v3.0.0"
	if pause_menu:
		pause_menu.visible = false
	if quit_menu:
		quit_menu.visible = false
	if character_menu:
		character_menu.visible = false

	if camera_view_label:
		camera_view_label.text = "F1: Cycle | F2: 1st | F3: 3rd Back | F4: 3rd Front"
		camera_view_label.add_theme_color_override("font_color", Color(0.4, 0.4, 0.5))

	connect_ui_signals()

func set_camera_view_label(view_name: String):
	if camera_view_label:
		camera_view_label.text = "View: " + view_name

func setup_character_menu():
	if character_menu:
		var color_btn = character_menu.get_node_or_null("VBoxContainer/ColorButton")
		if color_btn and !color_btn.is_connected("pressed", Callable(self, "_on_cycle_color")):
			color_btn.pressed.connect(_on_cycle_color)
		
		var name_input = character_menu.get_node_or_null("VBoxContainer/NameInput")
		if name_input:
			name_input.text_submitted.connect(_on_name_submitted)
		
		var apply_btn = character_menu.get_node_or_null("VBoxContainer/ApplyButton")
		if apply_btn and !apply_btn.is_connected("pressed", Callable(self, "_on_apply_character")):
			apply_btn.pressed.connect(_on_apply_character)
		
		var close_btn = character_menu.get_node_or_null("VBoxContainer/CloseButton")
		if close_btn and !close_btn.is_connected("pressed", Callable(self, "_on_close_character_menu")):
			close_btn.pressed.connect(_on_close_character_menu)
		
		update_character_preview()

func update_character_preview():
	if character_preview:
		var current_player = get_tree().get_first_node_in_group("player")
		if current_player and current_player.has_method("character_color"):
			var color_map = {
				"default": Color(0.08, 0.08, 0.12),
				"light": Color(0.6, 0.5, 0.4),
				"dark": Color(0.02, 0.02, 0.04),
				"red": Color(0.3, 0.05, 0.05),
				"blue": Color(0.05, 0.05, 0.3),
				"green": Color(0.05, 0.2, 0.05)
			}
			var current_color = color_map.get(color_options[current_color_index], Color(0.08, 0.08, 0.12))
			character_preview.color = current_color
		
		if character_name_label:
			if current_player and current_player.has_method("character_name"):
				character_name_label.text = "Name: " + current_player.character_name

func _on_cycle_color():
	current_color_index = (current_color_index + 1) % color_options.size()
	if character_menu:
		var color_btn = character_menu.get_node_or_null("VBoxContainer/ColorButton")
		if color_btn:
			color_btn.text = "Color: " + color_display_names[current_color_index]
	update_character_preview()

func _on_name_submitted(new_name: String):
	var current_player = get_tree().get_first_node_in_group("player")
	if current_player and current_player.has_method("character_name"):
		current_player.character_name = new_name
	if character_name_label:
		character_name_label.text = "Name: " + new_name

func _on_apply_character():
	var current_player = get_tree().get_first_node_in_group("player")
	if current_player and current_player.has_method("set_character_color"):
		current_player.set_character_color(color_options[current_color_index])
	if character_menu:
		character_menu.visible = false
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _on_close_character_menu():
	if character_menu:
		character_menu.visible = false
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func apply_dark_theme():
	var panels = [start_menu, pause_menu, quit_menu, character_menu]
	for panel in panels:
		if panel:
			var style = StyleBoxFlat.new()
			style.bg_color = DARK_BG
			style.corner_radius_top_left = 16
			style.corner_radius_top_right = 16
			style.corner_radius_bottom_left = 16
			style.corner_radius_bottom_right = 16
			style.border_width_left = 1
			style.border_width_right = 1
			style.border_width_top = 1
			style.border_width_bottom = 1
			style.border_color = Color(0.12, 0.15, 0.25)
			panel.add_theme_stylebox_override("panel", style)
	
	var buttons = get_tree().get_nodes_in_group("ui_button")
	for btn in buttons:
		var style = StyleBoxFlat.new()
		style.bg_color = Color(0.12, 0.16, 0.25)
		style.corner_radius_top_left = 8
		style.corner_radius_top_right = 8
		style.corner_radius_bottom_left = 8
		style.corner_radius_bottom_right = 8
		style.border_width_left = 1
		style.border_width_right = 1
		style.border_width_top = 1
		style.border_width_bottom = 1
		style.border_color = Color(0.2, 0.25, 0.35)
		btn.add_theme_stylebox_override("normal", style)
		
		var hover_style = StyleBoxFlat.new()
		hover_style.bg_color = Color(0.2, 0.25, 0.38)
		hover_style.corner_radius_top_left = 8
		hover_style.corner_radius_top_right = 8
		hover_style.corner_radius_bottom_left = 8
		hover_style.corner_radius_bottom_right = 8
		hover_style.border_color = ACCENT_COLOR
		btn.add_theme_stylebox_override("hover", hover_style)

func setup_hotbar():
	if !hotbar_container:
		hotbar_container = get_node_or_null("HUD/HotbarContainer")
	if !hotbar_container:
		return

	hotbar_slots.clear()
	for child in hotbar_container.get_children():
		child.queue_free()

	for i in range(9):
		var slot = Panel.new()
		slot.custom_minimum_size = Vector2(52, 52)
		slot.size = Vector2(52, 52)
		
		var style = StyleBoxFlat.new()
		style.bg_color = Color(0.04, 0.04, 0.08, 0.85)
		style.border_width_bottom = 2
		style.border_color = Color(0.12, 0.12, 0.20)
		style.corner_radius_top_left = 4
		style.corner_radius_top_right = 4
		style.corner_radius_bottom_left = 4
		style.corner_radius_bottom_right = 4
		slot.add_theme_stylebox_override("panel", style)

		var label = Label.new()
		label.text = str(i + 1)
		label.position = Vector2(4, 2)
		label.add_theme_color_override("font_color", Color(0.35, 0.35, 0.45))
		slot.add_child(label)

		var bg = ColorRect.new()
		bg.color = Color(0.03, 0.03, 0.06, 0.9)
		bg.size = Vector2(52, 52)
		slot.add_child(bg)

		var item_display = ColorRect.new()
		item_display.size = Vector2(30, 30)
		item_display.position = Vector2(11, 11)
		item_display.color = get_block_color(i + 1)
		slot.add_child(item_display)

		var count_label = Label.new()
		count_label.text = "64"
		count_label.position = Vector2(26, 30)
		count_label.add_theme_color_override("font_color", Color(0.65, 0.65, 0.75))
		slot.add_child(count_label)

		hotbar_container.add_child(slot)
		hotbar_slots.append({
			"slot": slot,
			"bg": bg,
			"item": item_display,
			"count": count_label,
			"style": style
		})

	update_hotbar([], 0)

func get_block_color(block_type: int) -> Color:
	match block_type:
		1: return Color(0.32, 0.20, 0.10)
		2: return Color(0.15, 0.38, 0.08)
		3: return Color(0.32, 0.32, 0.35)
		4: return Color(0.22, 0.12, 0.05)
		5: return Color(0.05, 0.30, 0.05)
		6: return Color(0.55, 0.45, 0.28)
		7: return Color(0.55, 0.70, 0.80, 0.35)
		8: return Color(0.45, 0.28, 0.10)
		9: return Color(0.20, 0.20, 0.22)
		10: return Color(0.70, 0.65, 0.48)
		11: return Color(0.18, 0.35, 0.65, 0.45)
		12: return Color(0.80, 0.82, 0.88)
		13: return Color(0.40, 0.18, 0.10)
		_: return Color(0.6, 0.6, 0.6)

func update_stats(health: int, max_health: int, hunger: int, max_hunger: int, level: int, xp: int, xp_to_next: int):
	if health_bar:
		health_bar.value = (float(health) / float(max(1, max_health))) * 100.0
		var health_color = Color(0.20, 0.60, 0.20) if health > max_health * 0.3 else DANGER_COLOR
		health_bar.add_theme_color_override("fill", health_color)
	if hunger_bar:
		hunger_bar.value = (float(hunger) / float(max(1, max_hunger))) * 100.0
		var hunger_color = Color(0.60, 0.45, 0.15) if hunger > max_hunger * 0.3 else DANGER_COLOR
		hunger_bar.add_theme_color_override("fill", hunger_color)
	if exp_bar:
		exp_bar.value = (float(xp) / float(max(1, xp_to_next))) * 100.0
		exp_bar.add_theme_color_override("fill", ACCENT_COLOR)
	if level_label:
		level_label.text = "⚔ Lv." + str(level)
		level_label.add_theme_color_override("font_color", TEXT_COLOR)
	if block_counter:
		var health_icon = "❤" if health > max_health * 0.3 else "💀"
		block_counter.text = health_icon + " " + str(health) + "/" + str(max_health) + "  |  [B] House  [T] Tree  [E] Inventory"

func update_hotbar(inventory: Array, selected_slot: int):
	for i in range(hotbar_slots.size()):
		var slot_data = hotbar_slots[i]
		var is_selected = (i == selected_slot)

		if slot_data.style:
			if is_selected:
				slot_data.style.border_color = ACCENT_COLOR
				slot_data.style.border_width_bottom = 3
				slot_data.style.bg_color = Color(0.08, 0.08, 0.14, 0.9)
			else:
				slot_data.style.border_color = Color(0.12, 0.12, 0.20)
				slot_data.style.border_width_bottom = 2
				slot_data.style.bg_color = Color(0.04, 0.04, 0.08, 0.85)

		if i < inventory.size():
			var item = inventory[i]
			if slot_data.item:
				slot_data.item.color = get_block_color(item.get("block", 0))
			if slot_data.count:
				slot_data.count.text = str(item.get("count", 0)) if item.get("block", 0) != 0 else ""
		else:
			if slot_data.item:
				slot_data.item.color = get_block_color(0)
			if slot_data.count:
				slot_data.count.text = ""

# Inventory Panel
func setup_inventory_panel():
	inventory_panel = Panel.new()
	inventory_panel.name = "InventoryPanel"
	inventory_panel.visible = false
	inventory_panel.anchors_preset = 15
	inventory_panel.anchor_right = 1.0
	inventory_panel.anchor_bottom = 1.0
	inventory_panel.size = Vector2(400, 500)
	var style = StyleBoxFlat.new()
	style.bg_color = DARK_BG
	style.corner_radius = 12
	style.border_width = 2
	style.border_color = Color(0.12, 0.15, 0.25)
	inventory_panel.add_theme_stylebox_override("panel", style)
	add_child(inventory_panel)

	var main_vbox = VBoxContainer.new()
	main_vbox.anchors_preset = 15
	main_vbox.anchor_right = 1.0
	main_vbox.anchor_bottom = 1.0
	main_vbox.size = Vector2(400, 500)
	inventory_panel.add_child(main_vbox)

	var title = Label.new()
	title.text = "INVENTORY"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_color_override("font_color", TEXT_COLOR)
	main_vbox.add_child(title)

	inventory_grid = GridContainer.new()
	inventory_grid.columns = 9
	inventory_grid.size = Vector2(360, 400)
	main_vbox.add_child(inventory_grid)

	# Create 36 slots
	for i in range(36):
		var slot = Panel.new()
		slot.custom_minimum_size = Vector2(40, 40)
		slot.size = Vector2(40, 40)
		var slot_style = StyleBoxFlat.new()
		slot_style.bg_color = Color(0.04, 0.04, 0.08, 0.8)
		slot_style.border_width = 1
		slot_style.border_color = Color(0.12, 0.12, 0.20)
		slot.add_theme_stylebox_override("panel", slot_style)
		
		var item_display = ColorRect.new()
		item_display.size = Vector2(28, 28)
		item_display.position = Vector2(6, 6)
		slot.add_child(item_display)
		
		var count_label = Label.new()
		count_label.position = Vector2(20, 20)
		count_label.add_theme_color_override("font_color", Color(0.7, 0.7, 0.8))
		slot.add_child(count_label)
		
		# Click to transfer to chest if chest open
		slot.gui_input.connect(_on_inventory_slot_click.bind(i))
		inventory_grid.add_child(slot)
		inventory_slots.append({"slot": slot, "item": item_display, "count": count_label})

func _on_inventory_slot_click(event: InputEvent, slot_index: int):
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		var player = get_tree().get_first_node_in_group("player")
		if player and player.has_method("transfer_item") and chest_panel and chest_panel.visible:
			# Transfer from player inventory to chest
			# Find a free slot in chest or stack
			var chest_inv = chest_inventory_ref
			var moved = false
			for i in range(chest_inv.size()):
				if player.transfer_item(slot_index, chest_inv, i):
					moved = true
					break
			if moved:
				update_inventory_panel(player.inventory)
				update_chest_panel(chest_inv)

func toggle_inventory_panel(open: bool):
	inventory_panel.visible = open
	if open:
		update_inventory_panel(get_tree().get_first_node_in_group("player").inventory)
	else:
		inventory_panel.visible = false

func update_inventory_panel(inventory: Array):
	player_inventory_ref = inventory
	for i in range(inventory_slots.size()):
		var slot_data = inventory_slots[i]
		if i < inventory.size():
			var item = inventory[i]
			if item["block"] != 0:
				slot_data.item.color = get_block_color(item["block"])
				slot_data.count.text = str(item["count"])
			else:
				slot_data.item.color = Color(0,0,0,0)
				slot_data.count.text = ""
		else:
			slot_data.item.color = Color(0,0,0,0)
			slot_data.count.text = ""

# Chest Panel
func setup_chest