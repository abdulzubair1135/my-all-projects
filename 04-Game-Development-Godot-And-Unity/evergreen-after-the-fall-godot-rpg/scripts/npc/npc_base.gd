extends CharacterBody2D
class_name NPCBase

# Evergreen: After the Fall - Named NPC Social & Schedule Simulation
# Features realistic daily schedules, waypoint transitions, friendship progression, dialogue, and gift reactions

@export var npc_id: String = "npc_thomas"
@export var npc_name: String = "Thomas"
@export var role: String = "Master Farmer & Mentor"
@export var portrait_path: String = "res://assets/characters/npcs/portrait_thomas.png"
@export var friendship: int = 15

# Daily Schedule: array of {"start_hour": int, "end_hour": int, "activity": String, "position": Vector2, "dialogue": Array}
var schedule: Array[Dictionary] = []
var current_schedule_entry: Dictionary = {}

@onready var sprite: Sprite2D = $Sprite2D
@onready var interact_area: Area2D = $InteractArea

func _ready() -> void:
	add_to_group("npcs")
	_setup_npc_data()
	EventBus.time_updated.connect(_on_time_updated)
	_evaluate_schedule(GameState.current_hour)

func _setup_npc_data() -> void:
	match npc_id:
		"npc_thomas":
			npc_name = "Thomas"
			role = "Master Farmer & Mentor"
			portrait_path = "res://assets/characters/npcs/portrait_thomas.png"
			schedule = [
				{
					"start": 6, "end": 12,
					"activity": "Inspecting Crops",
					"position": Vector2(260, 290),
					"dialogue": [
						"Thomas: 'Good morning! The soil here is fertile—it just needs consistent water and care.'",
						"Thomas: 'Turnips grow in just two days if you water them every morning. Don't let the frost catch them.'"
					]
				},
				{
					"start": 12, "end": 18,
					"activity": "Tending Farm Workshop",
					"position": Vector2(210, 160),
					"dialogue": [
						"Thomas: 'Before the outbreak, this valley supplied grain to the whole county.'",
						"Thomas: 'Keep the perimeter fences reinforced. If you have timber, build barricades at the workbench.'"
					]
				},
				{
					"start": 18, "end": 24,
					"activity": "Resting at Farmhouse",
					"position": Vector2(170, 160),
					"dialogue": [
						"Thomas: 'Dusk is here. Lock the gates, turn down the lamps, and stay close.'"
					]
				}
			]
		"npc_elena":
			npc_name = "Dr. Elena"
			role = "Valley Physician"
			portrait_path = "res://assets/characters/npcs/portrait_elena.png"
			schedule = [
				{
					"start": 7, "end": 17,
					"activity": "Field Triage & Medicine",
					"position": Vector2(340, 160),
					"dialogue": [
						"Elena: 'Keep your hands clean and bandages sterile. Even a minor infected scratch can turn septic.'",
						"Elena: 'I'm researching the E.V.E.R. biological records. If you salvage medical supplies, bring them to me.'"
					]
				},
				{
					"start": 17, "end": 24,
					"activity": "Medical Lab Review",
					"position": Vector2(180, 160),
					"dialogue": [
						"Elena: 'Stay cautious on your supply runs. We can't afford to lose either of you.'"
					]
				}
			]
		"npc_marcus":
			npc_name = "Marcus"
			role = "Blacksmith & Armorer"
			portrait_path = "res://assets/characters/npcs/portrait_marcus.png"
			schedule = [
				{
					"start": 6, "end": 18,
					"activity": "Forging Tools & Defenses",
					"position": Vector2(230, 160),
					"dialogue": [
						"Marcus: 'Need an edge on your blade? Bring me stone and lumber and we'll fortify this valley.'",
						"Marcus: 'Spike traps near the garden fence will buy you precious time during horde attacks.'"
					]
				}
			]

func _on_time_updated(hour: int, _minute: int, _day: int, _season: String) -> void:
	_evaluate_schedule(hour)

func _evaluate_schedule(hour: int) -> void:
	for entry in schedule:
		var start = entry["start"]
		var end = entry["end"]
		if hour >= start and hour < end:
			current_schedule_entry = entry
			# Smoothly move or snap to schedule position
			position = entry["position"]
			return

func get_interaction_info() -> Dictionary:
	return {
		"id": npc_id,
		"name": npc_name,
		"prompt": "Talk (%s)" % role
	}

func interact(_player: Node2D) -> void:
	var active = InventoryService.get_active_item()
	
	# Check Gift Giving
	if not active.is_empty() and active.get("category") in ["Produce", "Material", "Medical"]:
		_try_give_gift(active)
		return
	
	# Trigger Scheduled Dialogue
	var lines: Array[String] = []
	if current_schedule_entry.has("dialogue"):
		lines = current_schedule_entry["dialogue"].duplicate()
	else:
		lines = ["%s: 'Stay safe out there in Evergreen.'" % npc_name]
	
	lines.append("%s: '(Friendship: %d/100)'" % [npc_name, friendship])
	EventBus.dialog_started.emit(npc_id, lines)

func _try_give_gift(item: Dictionary) -> void:
	var item_id = item["id"]
	var item_name = item["name"]
	
	# Check NPC gift preferences
	var is_loved = false
	if npc_id == "npc_thomas" and item_id in ["produce_turnip", "produce_potato", "seed_turnip"]:
		is_loved = true
	elif npc_id == "npc_elena" and item_id in ["med_bandage", "produce_carrot"]:
		is_loved = true
	elif npc_id == "npc_marcus" and item_id in ["mat_wood", "mat_stone", "crafted_trap"]:
		is_loved = true
	
	if InventoryService.consume_active_item(1):
		var gain = 15 if is_loved else 6
		friendship = min(100, friendship + gain)
		var reaction = "loved this gift so much!" if is_loved else "appreciated your gift."
		EventBus.notification_requested.emit("Gave %s to %s. %s (+%d Trust, now %d/100)" % [item_name, npc_name, reaction, gain, friendship], 3.5)

func serialize() -> Dictionary:
	return {
		"npc_id": npc_id,
		"friendship": friendship,
		"pos_x": position.x,
		"pos_y": position.y
	}

func deserialize(data: Dictionary) -> void:
	npc_id = data.get("npc_id", npc_id)
	friendship = int(data.get("friendship", friendship))
	if data.has("pos_x") and data.has("pos_y"):
		position = Vector2(data["pos_x"], data["pos_y"])
	_setup_npc_data()
	_evaluate_schedule(GameState.current_hour)
