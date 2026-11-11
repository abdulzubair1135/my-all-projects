class_name EquipmentCatalog
extends RefCounted

# Modular slot categories
const SLOT_WEAPON = "weapon"
const SLOT_HELMET = "helmet"
const SLOT_ARMOR = "armor"
const SLOT_SHIELD = "shield"

# Master data catalog of equipment items
const ITEMS: Dictionary = {
	# Weapons
	"wpn_sword_iron": {
		"id": "wpn_sword_iron",
		"name": "Iron Broadsword",
		"slot": SLOT_WEAPON,
		"cost": 5,
		"category": "melee",
		"damage_modifier": 10.0,
		"range": 1.8,
		"attack_interval": 1.0,
		"color": Color(0.8, 0.8, 0.85)
	},
	"wpn_spear_oak": {
		"id": "wpn_spear_oak",
		"name": "Pike Spear",
		"slot": SLOT_WEAPON,
		"cost": 8,
		"category": "melee",
		"damage_modifier": 12.0,
		"range": 2.8,
		"attack_interval": 1.25,
		"color": Color(0.7, 0.5, 0.3)
	},
	"wpn_bow_composite": {
		"id": "wpn_bow_composite",
		"name": "Recurve Bow",
		"slot": SLOT_WEAPON,
		"cost": 12,
		"category": "ranged",
		"damage_modifier": 8.0,
		"range": 18.0,
		"attack_interval": 1.5,
		"projectile_speed": 24.0,
		"color": Color(0.6, 0.4, 0.2)
	},
	"wpn_axe_battle": {
		"id": "wpn_axe_battle",
		"name": "Heavy Battleaxe",
		"slot": SLOT_WEAPON,
		"cost": 15,
		"category": "melee",
		"damage_modifier": 22.0,
		"range": 2.0,
		"attack_interval": 1.6,
		"color": Color(0.4, 0.4, 0.45)
	},
	"wpn_excalibur_gold": {
		"id": "wpn_excalibur_gold",
		"name": "Royal Excalibur",
		"slot": SLOT_WEAPON,
		"cost": 30,
		"category": "melee",
		"damage_modifier": 45.0,
		"range": 2.2,
		"attack_interval": 0.9,
		"color": Color(1.0, 0.85, 0.25)
	},
	"wpn_staff_arcane": {
		"id": "wpn_staff_arcane",
		"name": "Archmage Staff",
		"slot": SLOT_WEAPON,
		"cost": 25,
		"category": "ranged",
		"damage_modifier": 35.0,
		"range": 22.0,
		"attack_interval": 1.2,
		"projectile_speed": 30.0,
		"color": Color(0.4, 0.7, 1.0)
	},
	
	# Helmets
	"hlm_crown_gold": {
		"id": "hlm_crown_gold",
		"name": "Golden Royal Crown",
		"slot": SLOT_HELMET,
		"cost": 25,
		"armor_modifier": 18.0,
		"health_modifier": 80.0,
		"color": Color(1.0, 0.82, 0.2)
	},
	"hlm_none": {
		"id": "hlm_none",
		"name": "Bare Head",
		"slot": SLOT_HELMET,
		"cost": 0,
		"armor_modifier": 0.0,
		"health_modifier": 0.0,
		"color": Color(0.9, 0.75, 0.6)
	},
	"hlm_leather_cap": {
		"id": "hlm_leather_cap",
		"name": "Reinforced Cap",
		"slot": SLOT_HELMET,
		"cost": 2,
		"armor_modifier": 2.0,
		"health_modifier": 5.0,
		"color": Color(0.45, 0.3, 0.15)
	},
	"hlm_iron_sallet": {
		"id": "hlm_iron_sallet",
		"name": "Iron Sallet",
		"slot": SLOT_HELMET,
		"cost": 6,
		"armor_modifier": 6.0,
		"health_modifier": 15.0,
		"color": Color(0.65, 0.65, 0.7)
	},
	"hlm_knight_visored": {
		"id": "hlm_knight_visored",
		"name": "Visored Barbute",
		"slot": SLOT_HELMET,
		"cost": 12,
		"armor_modifier": 12.0,
		"health_modifier": 30.0,
		"color": Color(0.85, 0.85, 0.9)
	},
	
	# Armor
	"arm_cloth_tunic": {
		"id": "arm_cloth_tunic",
		"name": "Linen Tunic",
		"slot": SLOT_ARMOR,
		"cost": 0,
		"armor_modifier": 0.0,
		"speed_modifier": 0.0,
		"health_modifier": 0.0,
		"color": Color(0.2, 0.35, 0.5)
	},
	"arm_leather_vest": {
		"id": "arm_leather_vest",
		"name": "Studded Leather",
		"slot": SLOT_ARMOR,
		"cost": 5,
		"armor_modifier": 5.0,
		"speed_modifier": -0.1,
		"health_modifier": 20.0,
		"color": Color(0.35, 0.22, 0.12)
	},
	"arm_chainmail": {
		"id": "arm_chainmail",
		"name": "Riveted Chainmail",
		"slot": SLOT_ARMOR,
		"cost": 12,
		"armor_modifier": 14.0,
		"speed_modifier": -0.3,
		"health_modifier": 45.0,
		"color": Color(0.55, 0.55, 0.6)
	},
	"arm_plate_harness": {
		"id": "arm_plate_harness",
		"name": "Full Plate Cuirass",
		"slot": SLOT_ARMOR,
		"cost": 24,
		"armor_modifier": 28.0,
		"speed_modifier": -0.6,
		"health_modifier": 90.0,
		"color": Color(0.75, 0.75, 0.8)
	},
	"arm_royal_regalia": {
		"id": "arm_royal_regalia",
		"name": "Imperial Gold Regalia",
		"slot": SLOT_ARMOR,
		"cost": 40,
		"armor_modifier": 42.0,
		"speed_modifier": -0.3,
		"health_modifier": 150.0,
		"color": Color(0.95, 0.8, 0.2)
	},
	
	# Shield
	"shd_none": {
		"id": "shd_none",
		"name": "No Shield",
		"slot": SLOT_SHIELD,
		"cost": 0,
		"block_chance": 0.0,
		"armor_modifier": 0.0,
		"color": Color(0,0,0,0)
	},
	"shd_round_buckler": {
		"id": "shd_round_buckler",
		"name": "Wooden Buckler",
		"slot": SLOT_SHIELD,
		"cost": 4,
		"block_chance": 0.20,
		"armor_modifier": 3.0,
		"color": Color(0.6, 0.35, 0.15)
	},
	"shd_heater_shield": {
		"id": "shd_heater_shield",
		"name": "Heraldic Heater Shield",
		"slot": SLOT_SHIELD,
		"cost": 10,
		"block_chance": 0.40,
		"armor_modifier": 8.0,
		"color": Color(0.7, 0.2, 0.2)
	},
	"shd_tower_pavise": {
		"id": "shd_tower_pavise",
		"name": "Tower Pavise",
		"slot": SLOT_SHIELD,
		"cost": 18,
		"block_chance": 0.60,
		"armor_modifier": 15.0,
		"speed_modifier": -0.3,
		"color": Color(0.2, 0.4, 0.6)
	},
	"shd_royal_aegis": {
		"id": "shd_royal_aegis",
		"name": "Royal Aegis of Valor",
		"slot": SLOT_SHIELD,
		"cost": 28,
		"block_chance": 0.70,
		"armor_modifier": 24.0,
		"speed_modifier": -0.1,
		"color": Color(1.0, 0.85, 0.2)
	}
}

static func get_item(item_id: String) -> Dictionary:
	if ITEMS.has(item_id):
		return ITEMS[item_id]
	return {}

static func get_items_by_slot(slot: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for item_id in ITEMS:
		var item = ITEMS[item_id]
		if item.slot == slot:
			result.append(item)
	return result
