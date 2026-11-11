extends Node

# Evergreen: After the Fall - Quest & Story Campaign Service
# Manages multi-stage quest objectives, story act progression (Acts I-V), rewards, and narrative flags

signal quest_started(quest_id: String, quest_data: Dictionary)
signal quest_objective_updated(quest_id: String, objective_index: int)
signal quest_completed(quest_id: String, quest_data: Dictionary)
signal story_act_advanced(new_act: int, act_title: String)

var current_act: int = 1
const ACT_TITLES: Dictionary = {
	1: "Act I — A Place to Begin",
	2: "Act II — The Valley Remembers",
	3: "Act III — The Cost of Safety",
	4: "Act IV — Beneath Evergreen",
	5: "Act V — After the Fall"
}

# Quest Catalog based on the 120 GDD entries
var quest_database: Dictionary = {
	"ms01": {
		"id": "ms01",
		"title": "A Roof Before Rain",
		"category": "Main Story",
		"act": 1,
		"description": "Secure the perimeter of Evergreen Farm and inspect the homestead cabin.",
		"objectives": [
			{"desc": "Inspect the Farmhouse entrance", "required": 1, "current": 0},
			{"desc": "Draw fresh water from the well", "required": 1, "current": 0}
		],
		"rewards": {
			"xp": 50,
			"items": {"seed_turnip": 5, "mat_wood": 10}
		}
	},
	"ms02": {
		"id": "ms02",
		"title": "The First Morning",
		"category": "Main Story",
		"act": 1,
		"description": "Plant turnip seeds in the garden, water them, and harvest the first crop.",
		"objectives": [
			{"desc": "Plant and water turnip seeds", "required": 1, "current": 0},
			{"desc": "Harvest a mature turnip crop", "required": 1, "current": 0}
		],
		"rewards": {
			"xp": 75,
			"items": {"seed_carrot": 5, "seed_potato": 5}
		}
	},
	"ms04": {
		"id": "ms04",
		"title": "First Night",
		"category": "Main Story",
		"act": 1,
		"description": "Craft defensive barricades and survive the nocturnal infected attack.",
		"objectives": [
			{"desc": "Craft a Wooden Barricade at the workbench", "required": 1, "current": 0},
			{"desc": "Defeat the night perimeter horde", "required": 3, "current": 0}
		],
		"rewards": {
			"xp": 120,
			"items": {"mat_wood": 15, "mat_stone": 10}
		}
	},
	"ms05": {
		"id": "ms05",
		"title": "The Road to Evergreen",
		"category": "Main Story",
		"act": 2,
		"description": "Take the northern road to Evergreen Village and connect with local survivors.",
		"objectives": [
			{"desc": "Travel north to Evergreen Village", "required": 1, "current": 0},
			{"desc": "Speak with Shopkeeper Lily and Blacksmith Marcus", "required": 2, "current": 0}
		],
		"rewards": {
			"xp": 100,
			"items": {"food_bread": 3, "med_bandage": 2}
		}
	},
	"fc01": {
		"id": "fc01",
		"title": "Turn the Soil",
		"category": "Farming",
		"act": 1,
		"description": "Demonstrate your agricultural skill by cultivating the farm garden.",
		"objectives": [
			{"desc": "Till and water 3 crop plots", "required": 3, "current": 0}
		],
		"rewards": {
			"xp": 40,
			"items": {"seed_turnip": 8}
		}
	},
	"rl01": {
		"id": "rl01",
		"title": "Two Cups of Tea",
		"category": "Relationship",
		"act": 1,
		"description": "Take time to share a quiet meal with your partner on the porch.",
		"objectives": [
			{"desc": "Share a warm supper with your companion", "required": 1, "current": 0}
		],
		"rewards": {
			"xp": 50,
			"relationship_trust": 10,
			"relationship_closeness": 12
		}
	}
}

var active_quests: Dictionary = {} # quest_id -> {"current_obj_index": int, "objectives": Array}
var completed_quests: Array[String] = []
var story_flags: Dictionary = {
	"cured_infection": false,
	"railway_restored": false,
	"bunker_archive_unlocked": false,
	"research_data_secured": false
}

func _ready() -> void:
	# Automatically start initial quest on new game
	if active_quests.is_empty() and completed_quests.is_empty():
		start_quest("ms01")

func start_quest(quest_id: String) -> bool:
	if not quest_database.has(quest_id):
		return false
	if active_quests.has(quest_id) or completed_quests.has(quest_id):
		return false
	
	var q = quest_database[quest_id]
	active_quests[quest_id] = {
		"current_obj_index": 0,
		"objectives": q["objectives"].duplicate(true)
	}
	
	quest_started.emit(quest_id, q)
	EventBus.quest_started.emit(quest_id, q)
	EventBus.notification_requested.emit("New Quest: %s (%s)" % [q["title"], q["category"]], 3.0)
	print("[QuestService] Started quest: %s" % q["title"])
	return true

func update_progress(quest_id: String, objective_index: int, amount: int = 1) -> void:
	if not active_quests.has(quest_id):
		return
	
	var q_state = active_quests[quest_id]
	if objective_index < q_state["objectives"].size():
		var obj = q_state["objectives"][objective_index]
		obj["current"] = min(obj["required"], obj["current"] + amount)
		quest_objective_updated.emit(quest_id, objective_index)
		
		# Check if all objectives complete
		var all_done = true
		for o in q_state["objectives"]:
			if o["current"] < o["required"]:
				all_done = false
				break
		
		if all_done:
			complete_quest(quest_id)

func complete_quest(quest_id: String) -> bool:
	if not active_quests.has(quest_id):
		return false
	if completed_quests.has(quest_id):
		return false # Never grant rewards twice!
	
	var q_def = quest_database[quest_id]
	active_quests.erase(quest_id)
	completed_quests.append(quest_id)
	
	# Dispatch rewards
	if q_def.has("rewards"):
		var rew = q_def["rewards"]
		if rew.has("items"):
			for item_id in rew["items"].keys():
				InventoryService.add_item(item_id, rew["items"][item_id])
		if rew.has("relationship_trust"):
			RelationshipService.add_trust(rew["relationship_trust"])
		if rew.has("relationship_closeness"):
			RelationshipService.add_closeness(rew["relationship_closeness"])
	
	# Chain next quest in sequence
	match quest_id:
		"ms01":
			start_quest("ms02")
		"ms02":
			start_quest("ms04")
		"ms04":
			advance_act(2)
			start_quest("ms05")
	
	quest_completed.emit(quest_id, q_def)
	EventBus.quest_completed.emit(quest_id, q_def)
	EventBus.notification_requested.emit("Quest Completed: %s! Rewards collected." % q_def["title"], 3.5)
	print("[QuestService] Completed quest: %s" % q_def["title"])
	return true

func advance_act(new_act: int) -> void:
	if new_act > current_act and ACT_TITLES.has(new_act):
		current_act = new_act
		var title = ACT_TITLES[current_act]
		story_act_advanced.emit(current_act, title)
		EventBus.notification_requested.emit("STORY MILESTONE: %s" % title, 4.0)

func evaluate_ending() -> String:
	# Six endings based on GDD
	if story_flags.get("research_data_secured", false):
		return "Ending A — The Green Dawn (True Cure Ending)"
	elif RelationshipService.trust >= 80 and RelationshipService.closeness >= 80:
		return "Ending B — Home Is Us (Relationship Ending)"
	elif story_flags.get("railway_restored", false):
		return "Ending C — Beyond the Valley (Evacuation Ending)"
	elif story_flags.get("bunker_archive_unlocked", false):
		return "Ending F — The Hidden Record (Secret Post-Game Ending)"
	elif completed_quests.size() >= 5:
		return "Ending E — Evergreen Reborn (Community Settlement Ending)"
	else:
		return "Ending D — The Last Light (Survival Ending)"

func is_quest_completed(quest_id: String) -> bool:
	return completed_quests.has(quest_id)

func serialize() -> Dictionary:
	return {
		"current_act": current_act,
		"active_quests": active_quests.duplicate(true),
		"completed_quests": completed_quests.duplicate(),
		"story_flags": story_flags.duplicate()
	}

func deserialize(data: Dictionary) -> void:
	current_act = int(data.get("current_act", current_act))
	if data.has("active_quests"):
		active_quests = data["active_quests"].duplicate(true)
	if data.has("completed_quests"):
		completed_quests.clear()
		for q in data["completed_quests"]:
			completed_quests.append(str(q))
	if data.has("story_flags"):
		story_flags = data["story_flags"].duplicate()
