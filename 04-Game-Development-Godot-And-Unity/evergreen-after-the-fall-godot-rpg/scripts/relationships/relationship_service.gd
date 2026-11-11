extends Node

# Evergreen: After the Fall - Relationship & Romance Service
# Multi-dimensional relationship tracking for Archi & Danish (Trust, Closeness, Respect, Shared Memories)

signal relationship_updated(dimensions: Dictionary)
signal milestone_unlocked(milestone_id: String, title: String)

var trust: int = 30 # 0 to 100
var closeness: int = 25 # 0 to 100
var respect: int = 35 # 0 to 100

var memories: Array[Dictionary] = [
	{
		"id": "mem_arrival",
		"title": "Arrived at Evergreen",
		"description": "Together we reached the abandoned homestead at dawn, weary from the road but determined to build a sanctuary.",
		"day": 1
	}
]

var unlocked_milestones: Array[String] = []

func _ready() -> void:
	# Synchronize starting relationship from GameState
	if GameState.relationship.has("trust"):
		trust = GameState.relationship["trust"]
		closeness = GameState.relationship["closeness"]
		respect = GameState.relationship["respect"]

func add_trust(amount: int, reason: String = "") -> void:
	trust = clamp(trust + amount, 0, 100)
	GameState.relationship["trust"] = trust
	_check_milestones()
	relationship_updated.emit(get_summary())
	if reason != "":
		EventBus.notification_requested.emit("Trust Increased (+%d): %s" % [amount, reason], 2.5)

func add_closeness(amount: int, reason: String = "") -> void:
	closeness = clamp(closeness + amount, 0, 100)
	GameState.relationship["closeness"] = closeness
	_check_milestones()
	relationship_updated.emit(get_summary())
	if reason != "":
		EventBus.notification_requested.emit("Closeness Increased (+%d): %s" % [amount, reason], 2.5)

func add_respect(amount: int, reason: String = "") -> void:
	respect = clamp(respect + amount, 0, 100)
	GameState.relationship["respect"] = respect
	_check_milestones()
	relationship_updated.emit(get_summary())
	if reason != "":
		EventBus.notification_requested.emit("Respect Increased (+%d): %s" % [amount, reason], 2.5)

func record_memory(id: String, title: String, description: String) -> void:
	for mem in memories:
		if mem["id"] == id:
			return # Already recorded
	
	memories.append({
		"id": id,
		"title": title,
		"description": description,
		"day": GameState.current_day
	})
	EventBus.notification_requested.emit("New Shared Memory: '%s'" % title, 3.5)

func _check_milestones() -> void:
	if trust >= 50 and not unlocked_milestones.has("trust_1"):
		unlocked_milestones.append("trust_1")
		record_memory("mem_trust_1", "Shared Truth", "We confessed our deepest doubts about the valley's future and promised to face whatever comes together.")
		milestone_unlocked.emit("trust_1", "Shared Truth")
		
	if closeness >= 50 and not unlocked_milestones.has("closeness_1"):
		unlocked_milestones.append("closeness_1")
		record_memory("mem_closeness_1", "Tea on the Porch", "A quiet storm passed over the valley while we sat side-by-side on the farmhouse steps.")
		milestone_unlocked.emit("closeness_1", "Tea on the Porch")
		
	if trust >= 80 and respect >= 75 and not unlocked_milestones.has("commitment"):
		unlocked_milestones.append("commitment")
		record_memory("mem_commitment", "Unbreakable Bond", "Neither infected hordes nor faction threats will ever break what we've forged in Evergreen.")
		milestone_unlocked.emit("commitment", "Unbreakable Bond")

func get_companion_support_buff() -> Dictionary:
	# Passive buffs derived from relationship strength
	return {
		"stamina_regen_bonus": 0.15 if trust >= 50 else 0.0,
		"damage_resistance_bonus": 0.10 if closeness >= 50 else 0.0
	}

func share_meal() -> bool:
	if InventoryService.has_item("food_bread", 1):
		InventoryService.remove_item("food_bread", 1)
	elif InventoryService.has_item("produce_turnip", 1):
		InventoryService.remove_item("produce_turnip", 1)
	else:
		EventBus.notification_requested.emit("Need bread or fresh vegetables to share a meal!", 2.5)
		return false
	
	add_trust(6, "Shared a warm meal together")
	add_closeness(8, "Quiet time around the kitchen table")
	
	# Heal both protagonists
	for p_key in GameState.character_data.keys():
		var stats = GameState.character_data[p_key]
		stats["health"] = min(stats["max_health"], stats["health"] + 25.0)
	
	var cur_stats = GameState.get_current_stats()
	EventBus.health_changed.emit(cur_stats["health"], cur_stats["max_health"])
	record_memory("mem_meal_" + str(GameState.current_day), "Supper in the Cabin", "Shared fresh food from the farm and found a brief moment of peace.")
	return true

func give_companion_gift(item_id: String) -> bool:
	if not InventoryService.has_item(item_id, 1):
		return false
	
	var is_archi_receiving = (GameState.current_protagonist == GameState.PROTAGONIST_DANISH)
	var loved = false
	
	if is_archi_receiving:
		# Archi loves fresh flowers, seeds, and medicinal herbs
		if item_id in ["seed_turnip", "produce_turnip", "med_bandage"]:
			loved = true
	else:
		# Danish loves mechanical parts, building materials, and tools
		if item_id in ["mat_wood", "mat_stone", "crafted_barricade"]:
			loved = true
	
	InventoryService.remove_item(item_id, 1)
	var t_gain = 8 if loved else 4
	var c_gain = 10 if loved else 5
	var r_gain = 6 if loved else 3
	
	add_trust(t_gain)
	add_closeness(c_gain)
	add_respect(r_gain)
	
	var recipient_name = "Archi" if is_archi_receiving else "Danish"
	var text = "%s loved your gift!" % recipient_name if loved else "%s appreciated the thoughtful gesture." % recipient_name
	EventBus.notification_requested.emit("%s (+%d Closeness, +%d Trust)" % [text, c_gain, t_gain], 3.0)
	return true

func get_summary() -> Dictionary:
	return {
		"trust": trust,
		"closeness": closeness,
		"respect": respect,
		"memories_count": memories.size(),
		"milestones": unlocked_milestones.duplicate()
	}

func serialize() -> Dictionary:
	return {
		"trust": trust,
		"closeness": closeness,
		"respect": respect,
		"memories": memories.duplicate(true),
		"unlocked_milestones": unlocked_milestones.duplicate()
	}

func deserialize(data: Dictionary) -> void:
	trust = int(data.get("trust", trust))
	closeness = int(data.get("closeness", closeness))
	respect = int(data.get("respect", respect))
	if data.has("memories"):
		memories.clear()
		for m in data["memories"]:
			if m is Dictionary:
				memories.append(m)
	if data.has("unlocked_milestones"):
		unlocked_milestones.clear()
		for u in data["unlocked_milestones"]:
			unlocked_milestones.append(str(u))
	_check_milestones()
	relationship_updated.emit(get_summary())
