class_name SoldierDesign
extends RefCounted

const SCHEMA_VERSION = "1.0.0"

var id: String = ""
var name: String = "Foot Soldier"
var archetype_id: String = "infantry"
var weapon_id: String = "wpn_sword_iron"
var helmet_id: String = "hlm_iron_sallet"
var armor_id: String = "arm_leather_vest"
var shield_id: String = "shd_round_buckler"
var primary_color: Color = Color(0.2, 0.45, 0.85) # Blue team default
var secondary_color: Color = Color(0.85, 0.7, 0.2) # Gold trim default
var scale_multiplier: float = 1.0

# Base archetype definitions
const ARCHETYPES = {
	"infantry": {
		"base_cost": 10,
		"max_health": 100.0,
		"move_speed": 3.8,
		"armor": 5.0,
		"base_damage": 12.0
	},
	"spearman": {
		"base_cost": 15,
		"max_health": 115.0,
		"move_speed": 3.4,
		"armor": 8.0,
		"base_damage": 15.0
	},
	"archer": {
		"base_cost": 20,
		"max_health": 80.0,
		"move_speed": 4.2,
		"armor": 2.0,
		"base_damage": 8.0
	},
	"knight": {
		"base_cost": 45,
		"max_health": 220.0,
		"move_speed": 3.2,
		"armor": 22.0,
		"base_damage": 25.0
	},
	"paladin": {
		"base_cost": 65,
		"max_health": 280.0,
		"move_speed": 3.0,
		"armor": 35.0,
		"base_damage": 30.0
	},
	"berserker": {
		"base_cost": 40,
		"max_health": 170.0,
		"move_speed": 4.6,
		"armor": 10.0,
		"base_damage": 38.0
	},
	"wizard": {
		"base_cost": 55,
		"max_health": 90.0,
		"move_speed": 3.6,
		"armor": 4.0,
		"base_damage": 45.0
	},
	"commander": {
		"base_cost": 90,
		"max_health": 350.0,
		"move_speed": 3.6,
		"armor": 25.0,
		"base_damage": 35.0
	},
	"king": {
		"base_cost": 150,
		"max_health": 600.0,
		"move_speed": 3.2,
		"armor": 45.0,
		"base_damage": 55.0
	}
}

func _init(p_id: String = "", p_name: String = "Foot Soldier") -> void:
	if p_id.is_empty():
		id = "soldier_" + str(Time.get_unix_time_from_system()).sha1_text().substr(0, 8)
	else:
		id = p_id
	name = p_name

func calculate_derived_stats() -> Dictionary:
	var arch = ARCHETYPES.get(archetype_id, ARCHETYPES["infantry"])
	var total_cost: int = arch.base_cost
	var health: float = arch.max_health
	var speed: float = arch.move_speed
	var armor: float = arch.armor
	var damage: float = arch.base_damage
	var attack_range: float = 1.8
	var attack_interval: float = 1.0
	var projectile_speed: float = 0.0
	var block_chance: float = 0.0
	var is_ranged: bool = false
	
	# Apply equipment
	var wpn = EquipmentCatalog.get_item(weapon_id)
	if not wpn.is_empty():
		total_cost += int(wpn.get("cost", 0))
		damage += float(wpn.get("damage_modifier", 0.0))
		attack_range = float(wpn.get("range", attack_range))
		attack_interval = float(wpn.get("attack_interval", attack_interval))
		if wpn.get("category", "") == "ranged":
			is_ranged = true
			projectile_speed = float(wpn.get("projectile_speed", 20.0))
			
	var hlm = EquipmentCatalog.get_item(helmet_id)
	if not hlm.is_empty():
		total_cost += int(hlm.get("cost", 0))
		armor += float(hlm.get("armor_modifier", 0.0))
		health += float(hlm.get("health_modifier", 0.0))
		
	var arm = EquipmentCatalog.get_item(armor_id)
	if not arm.is_empty():
		total_cost += int(arm.get("cost", 0))
		armor += float(arm.get("armor_modifier", 0.0))
		health += float(arm.get("health_modifier", 0.0))
		speed += float(arm.get("speed_modifier", 0.0))
		
	var shd = EquipmentCatalog.get_item(shield_id)
	if not shd.is_empty():
		total_cost += int(shd.get("cost", 0))
		armor += float(shd.get("armor_modifier", 0.0))
		block_chance += float(shd.get("block_chance", 0.0))
		speed += float(shd.get("speed_modifier", 0.0))
		
	return {
		"total_cost": total_cost,
		"max_health": max(20.0, health),
		"move_speed": max(1.5, speed),
		"armor": max(0.0, armor),
		"damage": max(1.0, damage),
		"attack_range": attack_range,
		"attack_interval": attack_interval,
		"projectile_speed": projectile_speed,
		"block_chance": clampf(block_chance, 0.0, 0.75),
		"is_ranged": is_ranged
	}

func serialize() -> Dictionary:
	return {
		"schema_version": SCHEMA_VERSION,
		"id": id,
		"name": name,
		"archetype_id": archetype_id,
		"weapon_id": weapon_id,
		"helmet_id": helmet_id,
		"armor_id": armor_id,
		"shield_id": shield_id,
		"primary_color": primary_color.to_html(false),
		"secondary_color": secondary_color.to_html(false),
		"scale_multiplier": scale_multiplier
	}

static func deserialize(data: Dictionary) -> SoldierDesign:
	var design = SoldierDesign.new(data.get("id", ""), data.get("name", "Foot Soldier"))
	design.archetype_id = data.get("archetype_id", "infantry")
	design.weapon_id = data.get("weapon_id", "wpn_sword_iron")
	design.helmet_id = data.get("helmet_id", "hlm_iron_sallet")
	design.armor_id = data.get("armor_id", "arm_leather_vest")
	design.shield_id = data.get("shield_id", "shd_round_buckler")
	if data.has("primary_color"):
		design.primary_color = Color.from_string(data["primary_color"], Color(0.2, 0.45, 0.85))
	if data.has("secondary_color"):
		design.secondary_color = Color.from_string(data["secondary_color"], Color(0.85, 0.7, 0.2))
	design.scale_multiplier = float(data.get("scale_multiplier", 1.0))
	return design
