extends Node

# Evergreen: After the Fall - InventoryService Autoload
# Central authority for player inventory, quickbar slots, item metadata, and container storage

const MAX_PLAYER_SLOTS: int = 24
const QUICKBAR_SLOTS: int = 5

# Comprehensive item registry
var item_database: Dictionary = {
	"tool_hoe": {
		"id": "tool_hoe",
		"name": "Field Hoe",
		"category": "Tool",
		"description": "Used to till dry grassy soil into fertile farm plots.",
		"max_stack": 1,
		"use_type": "till",
		"sell_value": 40
	},
	"tool_can": {
		"id": "tool_can",
		"name": "Watering Can",
		"category": "Tool",
		"description": "Holds fresh water from the well to hydrate dry tilled soil.",
		"max_stack": 1,
		"use_type": "water",
		"sell_value": 40
	},
	"weapon_machete": {
		"id": "weapon_machete",
		"name": "Sturdy Machete",
		"category": "Weapon",
		"description": "A sharp salvage blade for clearing brush and self-defense.",
		"max_stack": 1,
		"use_type": "melee",
		"sell_value": 75
	},
	"seed_turnip": {
		"id": "seed_turnip",
		"name": "Turnip Seeds",
		"category": "Seed",
		"description": "Fast-growing spring root seed. Matures in 2 days when watered.",
		"max_stack": 99,
		"use_type": "plant",
		"crop_id": "crop_turnip",
		"sell_value": 10
	},
	"seed_carrot": {
		"id": "seed_carrot",
		"name": "Carrot Seeds",
		"category": "Seed",
		"description": "Nutritious orange root seed. Matures in 3 days when watered.",
		"max_stack": 99,
		"use_type": "plant",
		"crop_id": "crop_carrot",
		"sell_value": 15
	},
	"seed_potato": {
		"id": "seed_potato",
		"name": "Potato Eyes",
		"category": "Seed",
		"description": "Hearty survival tuber. Matures in 3 days when watered.",
		"max_stack": 99,
		"use_type": "plant",
		"crop_id": "crop_potato",
		"sell_value": 20
	},
	"produce_turnip": {
		"id": "produce_turnip",
		"name": "Fresh Turnip",
		"category": "Produce",
		"description": "Crisp white-and-purple spring turnip. Restores hunger and stamina.",
		"max_stack": 99,
		"use_type": "consume",
		"nutrition": 20.0,
		"sell_value": 35
	},
	"produce_carrot": {
		"id": "produce_carrot",
		"name": "Sweet Carrot",
		"category": "Produce",
		"description": "Freshly harvested crunchy carrot rich in vitamins.",
		"max_stack": 99,
		"use_type": "consume",
		"nutrition": 25.0,
		"sell_value": 45
	},
	"produce_potato": {
		"id": "produce_potato",
		"name": "Hearty Potato",
		"category": "Produce",
		"description": "Starchy staple crop, essential for winter survival provisions.",
		"max_stack": 99,
		"use_type": "consume",
		"nutrition": 30.0,
		"sell_value": 50
	},
	"food_bread": {
		"id": "food_bread",
		"name": "Fresh Bread",
		"category": "Food",
		"description": "Baked from valley flour. Satisfies hunger and boosts morale.",
		"max_stack": 20,
		"use_type": "consume",
		"nutrition": 35.0,
		"sell_value": 25
	},
	"mat_wood": {
		"id": "mat_wood",
		"name": "Timber Lumber",
		"category": "Material",
		"description": "Sturdy pine and oak planks used for fence repair and building.",
		"max_stack": 99,
		"use_type": "build",
		"sell_value": 5
	},
	"mat_stone": {
		"id": "mat_stone",
		"name": "Quarried Stone",
		"category": "Material",
		"description": "Smooth foundation stones for masonry and barricades.",
		"max_stack": 99,
		"use_type": "build",
		"sell_value": 5
	},
	"produce_egg": {
		"id": "produce_egg",
		"name": "Farm Fresh Egg",
		"category": "Produce",
		"description": "Nutritious brown egg collected from the chicken coop.",
		"max_stack": 99,
		"use_type": "consume",
		"nutrition": 18.0,
		"sell_value": 20
	},
	"produce_milk": {
		"id": "produce_milk",
		"name": "Fresh Milk Bottle",
		"category": "Produce",
		"description": "Rich whole milk from pasture cows. Hydrates and restores energy.",
		"max_stack": 20,
		"use_type": "consume",
		"nutrition": 25.0,
		"sell_value": 35
	},
	"crafted_barricade": {
		"id": "crafted_barricade",
		"name": "Wooden Barricade",
		"category": "Defense",
		"description": "Reinforced timber barricade for blocking perimeter paths against zombies.",
		"max_stack": 20,
		"use_type": "build",
		"sell_value": 45
	},
	"crafted_trap": {
		"id": "crafted_trap",
		"name": "Spike Trap",
		"category": "Defense",
		"description": "Concealed wooden and stone spikes that puncture incoming infected.",
		"max_stack": 20,
		"use_type": "build",
		"sell_value": 55
	},
	"med_bandage": {
		"id": "med_bandage",
		"name": "Sterile Bandage",
		"category": "Medical",
		"description": "Clean dressing for treating bites, lacerations, and restoring 30 HP.",
		"max_stack": 20,
		"use_type": "heal",
		"heal_amount": 30.0,
		"sell_value": 30
	},
	"quest_item_research_key": {
		"id": "quest_item_research_key",
		"name": "E.V.E.R. Research Keycard",
		"category": "Quest",
		"description": "Cryptographic security key recovered from The Warden. Grants access to the underground laboratory cure research.",
		"max_stack": 1,
		"use_type": "quest",
		"sell_value": 0
	}
}

# Player inventory array: elements are {"item_id": String, "count": int} or empty {}
var slots: Array[Dictionary] = []
var active_slot_index: int = 0

# Shared farm chest storage
var chest_slots: Array[Dictionary] = []

func _ready() -> void:
	_initialize_default_inventory()

func _initialize_default_inventory() -> void:
	slots.clear()
	for i in range(MAX_PLAYER_SLOTS):
		slots.append({})
	
	# Initial starting loadout:
	# Slot 0: Field Hoe
	# Slot 1: Watering Can
	# Slot 2: Turnip Seeds (x10)
	# Slot 3: Carrot Seeds (x5)
	# Slot 4: Sturdy Machete
	# Slot 5: Fresh Bread (x3)
	slots[0] = {"item_id": "tool_hoe", "count": 1}
	slots[1] = {"item_id": "tool_can", "count": 1}
	slots[2] = {"item_id": "seed_turnip", "count": 10}
	slots[3] = {"item_id": "seed_carrot", "count": 5}
	slots[4] = {"item_id": "weapon_machete", "count": 1}
	slots[5] = {"item_id": "food_bread", "count": 3}
	
	# Initial Farm Storage Chest loadout
	chest_slots.clear()
	for i in range(16):
		chest_slots.append({})
	chest_slots[0] = {"item_id": "seed_potato", "count": 8}
	chest_slots[1] = {"item_id": "seed_turnip", "count": 10}
	chest_slots[2] = {"item_id": "mat_wood", "count": 25}
	chest_slots[3] = {"item_id": "mat_stone", "count": 15}

func get_active_item() -> Dictionary:
	if active_slot_index >= 0 and active_slot_index < slots.size():
		var slot = slots[active_slot_index]
		if not slot.is_empty() and slot.has("item_id"):
			var base = item_database.get(slot["item_id"], {})
			var item = base.duplicate()
			item["count"] = slot["count"]
			return item
	return {}

func select_slot(index: int) -> void:
	if index >= 0 and index < QUICKBAR_SLOTS:
		active_slot_index = index
		EventBus.inventory_updated.emit()
		var it = get_active_item()
		if not it.is_empty():
			EventBus.notification_requested.emit("Equipped: %s (x%d)" % [it["name"], it["count"]], 1.5)

func add_item(item_id: String, count: int = 1) -> bool:
	if not item_database.has(item_id) or count <= 0:
		return false
	
	var max_stack = item_database[item_id].get("max_stack", 99)
	var remaining: int = count
	
	# 1. First attempt to stack with existing slots
	for i in range(slots.size()):
		if not slots[i].is_empty() and slots[i]["item_id"] == item_id:
			var space = max_stack - slots[i]["count"]
			if space > 0:
				var to_add = min(space, remaining)
				slots[i]["count"] += to_add
				remaining -= to_add
				if remaining <= 0:
					EventBus.inventory_updated.emit()
					return true
	
	# 2. Add into empty slots
	for i in range(slots.size()):
		if slots[i].is_empty():
			var to_add = min(max_stack, remaining)
			slots[i] = {"item_id": item_id, "count": to_add}
			remaining -= to_add
			if remaining <= 0:
				EventBus.inventory_updated.emit()
				return true
	
	EventBus.inventory_updated.emit()
	return remaining == 0

func remove_item(item_id: String, count: int = 1) -> bool:
	if not has_item(item_id, count):
		return false
	
	var remaining = count
	for i in range(slots.size() - 1, -1, -1):
		if not slots[i].is_empty() and slots[i]["item_id"] == item_id:
			if slots[i]["count"] > remaining:
				slots[i]["count"] -= remaining
				remaining = 0
				break
			else:
				remaining -= slots[i]["count"]
				slots[i] = {}
				if remaining == 0:
					break
	
	EventBus.inventory_updated.emit()
	return true

func consume_active_item(count: int = 1) -> bool:
	if active_slot_index >= 0 and active_slot_index < slots.size():
		var slot = slots[active_slot_index]
		if not slot.is_empty() and slot.get("count", 0) >= count:
			slot["count"] -= count
			if slot["count"] <= 0:
				slots[active_slot_index] = {}
			EventBus.inventory_updated.emit()
			return true
	return false

func has_item(item_id: String, count: int = 1) -> bool:
	return get_item_count(item_id) >= count

func get_item_count(item_id: String) -> int:
	var total: int = 0
	for slot in slots:
		if not slot.is_empty() and slot.get("item_id", "") == item_id:
			total += int(slot.get("count", 0))
	return total

func serialize() -> Dictionary:
	return {
		"slots": slots.duplicate(true),
		"active_slot_index": active_slot_index,
		"chest_slots": chest_slots.duplicate(true)
	}

func deserialize(data: Dictionary) -> void:
	if data.has("slots"):
		slots.clear()
		for s in data["slots"]:
			if s is Dictionary and not s.is_empty():
				slots.append({"item_id": str(s.get("item_id", "")), "count": int(s.get("count", 0))})
			else:
				slots.append({})
	if data.has("active_slot_index"):
		active_slot_index = int(data["active_slot_index"])
	if data.has("chest_slots"):
		chest_slots.clear()
		for c in data["chest_slots"]:
			if c is Dictionary and not c.is_empty():
				chest_slots.append({"item_id": str(c.get("item_id", "")), "count": int(c.get("count", 0))})
			else:
				chest_slots.append({})
	EventBus.inventory_updated.emit()
