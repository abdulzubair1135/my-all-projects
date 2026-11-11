class_name BattlefieldController
extends Node3D

@onready var units_container: Node3D = $UnitsContainer
@onready var battle_hud: Control = $BattleHUD
@onready var timer_label: Label = $BattleHUD/TopBar/MarginContainer/HBoxContainer/TimerLabel
@onready var blue_count_label: Label = $BattleHUD/TopBar/MarginContainer/HBoxContainer/BlueCount
@onready var red_count_label: Label = $BattleHUD/TopBar/MarginContainer/HBoxContainer/RedCount
@onready var results_panel: PanelContainer = $BattleHUD/ResultsPanel
@onready var results_title: Label = $BattleHUD/ResultsPanel/VBoxContainer/TitleLabel
@onready var results_summary: Label = $BattleHUD/ResultsPanel/VBoxContainer/SummaryLabel

var engine: CombatSimulationEngine = CombatSimulationEngine.new()
var is_battle_active: bool = false
var blue_army_initial_count: int = 0
var red_army_initial_count: int = 0

func _ready() -> void:
	results_panel.visible = false
	_spawn_armies()
	_start_battle()

func _spawn_armies() -> void:
	# Load Player Army
	var player_army_dict = GameManager.active_army_loadout
	var player_army: ArmyLoadout
	if not player_army_dict.is_empty():
		player_army = ArmyLoadout.deserialize(player_army_dict)
	else:
		# Generate default player test brigade if launching directly
		player_army = ArmyLoadout.new()
		var design = SoldierDesign.new("player_default", "Royal Guard")
		player_army.custom_soldiers[design.id] = design.serialize()
		for x in range(-10, 11, 2):
			player_army.units.append({
				"unit_id": "u_blue_" + str(x),
				"design_id": design.id,
				"position": Vector3(x, 0, 15),
				"rotation_y": 0.0
			})

	# Spawn Blue Units (Player Team 0)
	for u_info in player_army.units:
		var d_id = u_info.get("design_id", "")
		var d_data = player_army.custom_soldiers.get(d_id, {})
		var design = SoldierDesign.deserialize(d_data) if not d_data.is_empty() else SoldierDesign.new()
		
		var unit = Unit3D.new()
		unit.position = u_info.get("position", Vector3.ZERO)
		unit.setup_from_design(design, 0, u_info.get("unit_id", "u_0"))
		units_container.add_child(unit)
		engine.register_unit(unit)
		blue_army_initial_count += 1
		
	# Spawn Red Units (AI Opponent Team 1)
	var enemy_design = SoldierDesign.new("ai_enemy", "Marauder")
	enemy_design.archetype_id = "infantry"
	enemy_design.weapon_id = "wpn_axe_battle"
	enemy_design.armor_id = "arm_chainmail"
	
	for x in range(-12, 13, 2):
		for z in range(-18, -12, 2):
			var unit = Unit3D.new()
			unit.position = Vector3(x + (randf() - 0.5) * 0.4, 0, z)
			unit.setup_from_design(enemy_design, 1, "enemy_" + str(x) + "_" + str(z))
			units_container.add_child(unit)
			engine.register_unit(unit)
			red_army_initial_count += 1

func _start_battle() -> void:
	engine.simulation_running = true
	is_battle_active = true

func _physics_process(delta: float) -> void:
	if not is_battle_active:
		return
		
	var result = engine.step(delta)
	
	# Update HUD counts
	var blue_alive = 0
	var red_alive = 0
	for u in engine.units:
		if is_instance_valid(u) and u.unit_data.is_alive:
			if u.unit_data.team_id == 0:
				blue_alive += 1
			else:
				red_alive += 1
				
	timer_label.text = "Time: %0.1fs" % engine.battle_time
	blue_count_label.text = "Blue: %d / %d" % [blue_alive, blue_army_initial_count]
	red_count_label.text = "Red: %d / %d" % [red_alive, red_army_initial_count]
	
	if result.finished:
		_on_battle_completed(result)

func _on_battle_completed(result: Dictionary) -> void:
	is_battle_active = false
	results_panel.visible = true
	
	var winner = result.get("winner_team", -1)
	if winner == 0:
		results_title.text = "VICTORY!"
		results_title.add_theme_color_override("font_color", Color(0.2, 0.8, 0.3))
	elif winner == 1:
		results_title.text = "DEFEAT"
		results_title.add_theme_color_override("font_color", Color(0.9, 0.2, 0.2))
	else:
		results_title.text = "DRAW"
		results_title.add_theme_color_override("font_color", Color(0.8, 0.8, 0.2))
		
	var summary_text = "Match Duration: %0.1f seconds\n" % result.get("duration", 0.0)
	summary_text += "Blue Survivors: %d\n" % result.get("team_0_survivors", 0)
	summary_text += "Red Survivors: %d\n" % result.get("team_1_survivors", 0)
	results_summary.text = summary_text
	
	GameManager.last_battle_summary = result

func restart_battle() -> void:
	GameManager.change_scene("res://scenes/battlefield/battlefield.tscn")

func return_to_workshop() -> void:
	GameManager.change_scene("res://scenes/army_workshop/army_workshop.tscn")

func return_to_menu() -> void:
	GameManager.change_scene("res://scenes/main_menu/main_menu.tscn")
