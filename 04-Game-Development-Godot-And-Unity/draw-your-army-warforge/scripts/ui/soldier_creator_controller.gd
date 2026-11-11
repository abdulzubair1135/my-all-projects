class_name SoldierCreatorController
extends Node3D

@onready var preview_root: Node3D = $PreviewRoot
@onready var archetype_option: OptionButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/ArchetypeOption
@onready var name_edit: LineEdit = $UI/PanelContainer/ScrollContainer/VBoxContainer/NameEdit
@onready var stats_label: Label = $UI/PanelContainer/ScrollContainer/VBoxContainer/StatsLabel
@onready var cost_label: Label = $UI/PanelContainer/ScrollContainer/VBoxContainer/CostLabel
@onready var weapon_option: OptionButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/WeaponOption
@onready var armor_option: OptionButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/ArmorOption
@onready var helmet_option: OptionButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/HelmetOption
@onready var shield_option: OptionButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/ShieldOption
@onready var primary_color_picker: ColorPickerButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/ColorGrid/PrimaryColor
@onready var secondary_color_picker: ColorPickerButton = $UI/PanelContainer/ScrollContainer/VBoxContainer/ColorGrid/SecondaryColor
@onready var status_label: Label = $UI/PanelContainer/ScrollContainer/VBoxContainer/StatusLabel

var current_design: SoldierDesign
var preview_unit: Unit3D
var weapon_items: Array[Dictionary] = []
var armor_items: Array[Dictionary] = []
var helmet_items: Array[Dictionary] = []
var shield_items: Array[Dictionary] = []

const ARCHETYPE_CONFIGS: Array[Dictionary] = [
	{
		"id": "infantry",
		"name": "Foot Soldier",
		"weapon": "wpn_sword_iron",
		"armor": "arm_leather_vest",
		"helmet": "hlm_iron_sallet",
		"shield": "shd_round_buckler",
		"pri_color": Color(0.2, 0.45, 0.85),
		"sec_color": Color(0.85, 0.7, 0.2)
	},
	{
		"id": "spearman",
		"name": "Royal Spearman",
		"weapon": "wpn_spear_steel",
		"armor": "arm_leather_vest",
		"helmet": "hlm_iron_sallet",
		"shield": "shd_round_buckler",
		"pri_color": Color(0.15, 0.6, 0.7),
		"sec_color": Color(0.9, 0.8, 0.3)
	},
	{
		"id": "archer",
		"name": "Elite Archer",
		"weapon": "wpn_bow_composite",
		"armor": "arm_leather_vest",
		"helmet": "hlm_none",
		"shield": "shd_none",
		"pri_color": Color(0.2, 0.65, 0.3),
		"sec_color": Color(0.7, 0.5, 0.2)
	},
	{
		"id": "knight",
		"name": "Heavy Knight",
		"weapon": "wpn_greatsword",
		"armor": "arm_iron_plate",
		"helmet": "hlm_great_helm",
		"shield": "shd_tower_iron",
		"pri_color": Color(0.3, 0.35, 0.55),
		"sec_color": Color(0.95, 0.85, 0.3)
	},
	{
		"id": "paladin",
		"name": "Holy Paladin",
		"weapon": "wpn_excalibur_gold",
		"armor": "arm_iron_plate",
		"helmet": "hlm_great_helm",
		"shield": "shd_royal_aegis",
		"pri_color": Color(0.85, 0.85, 0.95),
		"sec_color": Color(1.0, 0.8, 0.2)
	},
	{
		"id": "berserker",
		"name": "Savage Berserker",
		"weapon": "wpn_axe_war",
		"armor": "arm_none",
		"helmet": "hlm_none",
		"shield": "shd_none",
		"pri_color": Color(0.75, 0.2, 0.15),
		"sec_color": Color(0.2, 0.2, 0.2)
	},
	{
		"id": "wizard",
		"name": "Archmage Wizard",
		"weapon": "wpn_staff_arcane",
		"armor": "arm_leather_vest",
		"helmet": "hlm_none",
		"shield": "shd_none",
		"pri_color": Color(0.4, 0.15, 0.7),
		"sec_color": Color(0.2, 0.8, 0.9)
	},
	{
		"id": "king",
		"name": "High King",
		"weapon": "wpn_excalibur_gold",
		"armor": "arm_royal_regalia",
		"helmet": "hlm_crown_gold",
		"shield": "shd_royal_aegis",
		"pri_color": Color(0.7, 0.1, 0.15),
		"sec_color": Color(1.0, 0.85, 0.2)
	}
]

func _ready() -> void:
	current_design = SoldierDesign.new("player_champion", "Foot Soldier")
	_populate_options()
	_update_preview()
	_update_stats_ui()

func _populate_options() -> void:
	# 1. Archetype
	archetype_option.clear()
	for i in range(ARCHETYPE_CONFIGS.size()):
		var arch = ARCHETYPE_CONFIGS[i]
		archetype_option.add_item(arch.name, i)
		if arch.id == current_design.archetype_id:
			archetype_option.selected = i
	archetype_option.item_selected.connect(_on_archetype_selected)

	# 2. Weapons
	weapon_items = EquipmentCatalog.get_items_by_slot(EquipmentCatalog.SLOT_WEAPON)
	weapon_option.clear()
	for i in range(weapon_items.size()):
		var item = weapon_items[i]
		weapon_option.add_item("%s (%d pts)" % [item.name, item.cost], i)
		if item.id == current_design.weapon_id:
			weapon_option.selected = i
	weapon_option.item_selected.connect(_on_weapon_selected)
	
	# 3. Armor
	armor_items = EquipmentCatalog.get_items_by_slot(EquipmentCatalog.SLOT_ARMOR)
	armor_option.clear()
	for i in range(armor_items.size()):
		var item = armor_items[i]
		armor_option.add_item("%s (%d pts)" % [item.name, item.cost], i)
		if item.id == current_design.armor_id:
			armor_option.selected = i
	armor_option.item_selected.connect(_on_armor_selected)
	
	# 4. Helmets
	helmet_items = EquipmentCatalog.get_items_by_slot(EquipmentCatalog.SLOT_HELMET)
	helmet_option.clear()
	for i in range(helmet_items.size()):
		var item = helmet_items[i]
		helmet_option.add_item("%s (%d pts)" % [item.name, item.cost], i)
		if item.id == current_design.helmet_id:
			helmet_option.selected = i
	helmet_option.item_selected.connect(_on_helmet_selected)
	
	# 5. Shields
	shield_items = EquipmentCatalog.get_items_by_slot(EquipmentCatalog.SLOT_SHIELD)
	shield_option.clear()
	for i in range(shield_items.size()):
		var item = shield_items[i]
		shield_option.add_item("%s (%d pts)" % [item.name, item.cost], i)
		if item.id == current_design.shield_id:
			shield_option.selected = i
	shield_option.item_selected.connect(_on_shield_selected)
	
	# Colors & Name
	primary_color_picker.color = current_design.primary_color
	primary_color_picker.color_changed.connect(_on_primary_color_changed)
	
	secondary_color_picker.color = current_design.secondary_color
	secondary_color_picker.color_changed.connect(_on_secondary_color_changed)
	
	name_edit.text = current_design.name
	name_edit.text_changed.connect(func(new_text): current_design.name = new_text)

func _on_archetype_selected(index: int) -> void:
	if index < 0 or index >= ARCHETYPE_CONFIGS.size():
		return
	var cfg = ARCHETYPE_CONFIGS[index]
	current_design.archetype_id = cfg.id
	current_design.name = cfg.name
	name_edit.text = cfg.name
	
	current_design.weapon_id = cfg.weapon
	current_design.armor_id = cfg.armor
	current_design.helmet_id = cfg.helmet
	current_design.shield_id = cfg.shield
	current_design.primary_color = cfg.pri_color
	current_design.secondary_color = cfg.sec_color
	
	primary_color_picker.color = cfg.pri_color
	secondary_color_picker.color = cfg.sec_color
	
	_sync_dropdowns_to_design()
	_update_preview()
	_update_stats_ui()

func _sync_dropdowns_to_design() -> void:
	for i in range(weapon_items.size()):
		if weapon_items[i].id == current_design.weapon_id:
			weapon_option.selected = i
			break
	for i in range(armor_items.size()):
		if armor_items[i].id == current_design.armor_id:
			armor_option.selected = i
			break
	for i in range(helmet_items.size()):
		if helmet_items[i].id == current_design.helmet_id:
			helmet_option.selected = i
			break
	for i in range(shield_items.size()):
		if shield_items[i].id == current_design.shield_id:
			shield_option.selected = i
			break

func _on_weapon_selected(index: int) -> void:
	current_design.weapon_id = weapon_items[index].id
	_update_preview()
	_update_stats_ui()

func _on_armor_selected(index: int) -> void:
	current_design.armor_id = armor_items[index].id
	_update_preview()
	_update_stats_ui()

func _on_helmet_selected(index: int) -> void:
	current_design.helmet_id = helmet_items[index].id
	_update_preview()
	_update_stats_ui()

func _on_shield_selected(index: int) -> void:
	current_design.shield_id = shield_items[index].id
	_update_preview()
	_update_stats_ui()

func _on_primary_color_changed(col: Color) -> void:
	current_design.primary_color = col
	_update_preview()

func _on_secondary_color_changed(col: Color) -> void:
	current_design.secondary_color = col
	_update_preview()

func _update_preview() -> void:
	for child in preview_root.get_children():
		child.queue_free()
		
	preview_unit = Unit3D.new()
	preview_unit.setup_from_design(current_design, 0, "preview_sol")
	preview_root.add_child(preview_unit)

func _update_stats_ui() -> void:
	var stats = current_design.calculate_derived_stats()
	cost_label.text = "Unit Cost: %d Points" % stats.total_cost
	
	var text = "Health: %0.0f\n" % stats.max_health
	text += "Speed: %0.1f\n" % stats.move_speed
	text += "Armor: %0.0f\n" % stats.armor
	text += "Damage: %0.0f\n" % stats.damage
	text += "Range: %0.1f m\n" % stats.attack_range
	text += "Block Chance: %0.0f%%\n" % (stats.block_chance * 100.0)
	stats_label.text = text

func _process(delta: float) -> void:
	# Subtle 3D preview turntable rotation
	if is_instance_valid(preview_root):
		preview_root.rotate_y(delta * 0.5)

func save_soldier() -> void:
	current_design.name = name_edit.text if not name_edit.text.is_empty() else "Custom Legionary"
	# Save active soldier in GameManager for immediate use in workshop
	GameManager.selected_soldier_design = current_design.serialize()
	
	var db = get_node_or_null("/root/DatabaseManager")
	if db:
		var file_name = "soldiers/" + current_design.id + ".json"
		var success = db.save_json_file(file_name, current_design.serialize())
		if success:
			status_label.text = "✅ Soldier saved! Ready for Army Workshop."
			status_label.add_theme_color_override("font_color", Color(0.3, 1.0, 0.4))
		else:
			status_label.text = "Failed to save soldier."

func return_to_menu() -> void:
	GameManager.change_scene("res://scenes/main_menu/main_menu.tscn")
