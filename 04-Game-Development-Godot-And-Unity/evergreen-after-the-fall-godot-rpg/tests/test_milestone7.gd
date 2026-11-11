extends Node

# Evergreen: After the Fall - Milestone 7 Automated Test Suite
# Tests Quest tracking, reward idempotency, story act advancement, boss combat & phases, endings, and persistence

const BossBaseScript = preload("res://scripts/combat/boss_base.gd")

func _ready() -> void:
	print("\n=======================================================")
	print("--- EVERGREEN: MILESTONE 7 VERIFICATION TEST SUITE ---")
	print("=======================================================")
	
	await get_tree().process_frame
	
	test_quest_progression_and_rewards()
	test_story_act_advancement()
	await test_boss_encounter_phases_and_defeat()
	test_multi_ending_evaluations()
	test_quest_persistence()
	
	print("\n=======================================================")
	print(">>> ALL MILESTONE 7 TESTS PASSED SUCCESSFULLY! (100%) <<<")
	print("=======================================================\n")
	get_tree().quit(0)

func test_quest_progression_and_rewards() -> void:
	print("[Test M7] 1. Testing Quest Progression & Reward Idempotency...")
	
	# Verify ms01 active initially
	assert(QuestService.active_quests.has("ms01"), "ms01 should be active by default")
	var initial_wood = InventoryService.get_item_count("mat_wood")
	var initial_seeds = InventoryService.get_item_count("seed_turnip")
	
	# Progress objectives
	QuestService.update_progress("ms01", 0, 1)
	assert(QuestService.active_quests["ms01"]["objectives"][0]["current"] == 1, "Objective 0 should be 1")
	
	# Complete final objective
	QuestService.update_progress("ms01", 1, 1)
	
	# ms01 should be completed and ms02 automatically started
	assert(QuestService.is_quest_completed("ms01"), "ms01 should be completed")
	assert(not QuestService.active_quests.has("ms01"), "ms01 should no longer be active")
	assert(QuestService.active_quests.has("ms02"), "ms02 should now be active")
	
	# Verify rewards received
	assert(InventoryService.get_item_count("mat_wood") == initial_wood + 10, "Should have received 10 wood")
	assert(InventoryService.get_item_count("seed_turnip") == initial_seeds + 5, "Should have received 5 turnip seeds")
	
	# Verify cannot complete quest twice (reward idempotency)
	var wood_after_complete = InventoryService.get_item_count("mat_wood")
	var second_attempt = QuestService.complete_quest("ms01")
	assert(second_attempt == false, "Attempting to complete ms01 twice must return false")
	assert(InventoryService.get_item_count("mat_wood") == wood_after_complete, "Rewards must not be duplicated")
	print(" -> PASS: Quest progression and reward idempotency verified.")

func test_story_act_advancement() -> void:
	print("[Test M7] 2. Testing Story Act Transitions...")
	
	assert(QuestService.current_act == 1, "Should be in Act 1")
	
	# Complete ms02
	QuestService.update_progress("ms02", 0, 1)
	QuestService.update_progress("ms02", 1, 1)
	assert(QuestService.is_quest_completed("ms02"), "ms02 should be completed")
	assert(QuestService.active_quests.has("ms04"), "ms04 should be active")
	
	# Complete ms04 -> triggers Act II transition
	QuestService.update_progress("ms04", 0, 1)
	QuestService.update_progress("ms04", 1, 3)
	assert(QuestService.is_quest_completed("ms04"), "ms04 should be completed")
	assert(QuestService.current_act == 2, "Current act should now be 2")
	assert(QuestService.active_quests.has("ms05"), "ms05 should be active in Act 2")
	print(" -> PASS: Act progression (Act I -> Act II) verified.")

func test_boss_encounter_phases_and_defeat() -> void:
	print("[Test M7] 3. Testing Boss Encounter ('The Warden')...")
	
	var boss_scene = load("res://scenes/enemies/BossWarden.tscn")
	var boss = boss_scene.instantiate()
	add_child(boss)
	await get_tree().process_frame
	
	assert(boss.current_health == 250.0, "Boss starting HP should be 250")
	assert(boss.current_phase == 1, "Boss starting phase should be 1")
	
	# Deal damage to push boss into Phase 2 (< 50% HP = < 125 HP)
	boss.hurtbox.take_hit(130.0, Vector2.RIGHT, null)
	assert(boss.current_health == 120.0, "Boss HP should be 120")
	assert(boss.current_phase == 2, "Boss should transition to Phase 2 (Enraged)")
	
	# Test ground slam telegraph
	boss._start_ground_slam()
	assert(boss.current_state == BossBaseScript.BossState.TELEGRAPH_SLAM, "Boss should enter telegraph state")
	
	# Deal lethal strike to defeat boss
	boss.hurtbox.can_take_damage = true
	var had_key_before = InventoryService.get_item_count("quest_item_research_key")
	boss.hurtbox.take_hit(150.0, Vector2.ZERO, null)
	assert(boss.current_health <= 0.0, "Boss HP should be <= 0")
	assert(boss.current_state == BossBaseScript.BossState.DEAD, "Boss should be DEAD")
	
	# Check key drop and story flag
	assert(InventoryService.get_item_count("quest_item_research_key") == had_key_before + 1, "Player should have received E.V.E.R. Research Keycard")
	assert(QuestService.story_flags["research_data_secured"] == true, "Story flag research_data_secured should be true")
	print(" -> PASS: Boss phases, telegraphs, and defeat rewards verified.")

func test_multi_ending_evaluations() -> void:
	print("[Test M7] 4. Testing Multi-Ending Branching System...")
	
	# 1. Ending A: True Cure (research_data_secured is true)
	QuestService.story_flags["research_data_secured"] = true
	var ending_a = QuestService.evaluate_ending()
	assert("The Green Dawn" in ending_a, "Ending A should trigger when research secured")
	
	# 2. Ending B: Romance (high trust & closeness)
	QuestService.story_flags["research_data_secured"] = false
	RelationshipService.trust = 85.0
	RelationshipService.closeness = 90.0
	var ending_b = QuestService.evaluate_ending()
	assert("Home Is Us" in ending_b, "Ending B should trigger when trust/closeness >= 80")
	
	# 3. Ending C: Evacuation (railway_restored)
	RelationshipService.trust = 50.0
	RelationshipService.closeness = 50.0
	QuestService.story_flags["railway_restored"] = true
	var ending_c = QuestService.evaluate_ending()
	assert("Beyond the Valley" in ending_c, "Ending C should trigger when railway restored")
	
	# 4. Ending F: Secret Post-game (bunker archive unlocked)
	QuestService.story_flags["railway_restored"] = false
	QuestService.story_flags["bunker_archive_unlocked"] = true
	var ending_f = QuestService.evaluate_ending()
	assert("The Hidden Record" in ending_f, "Ending F should trigger when bunker unlocked")
	
	# 5. Ending D: Survival
	QuestService.story_flags["bunker_archive_unlocked"] = false
	QuestService.completed_quests.clear()
	var ending_d = QuestService.evaluate_ending()
	assert("The Last Light" in ending_d, "Ending D should trigger when baseline survival")
	print(" -> PASS: Multi-ending branching rules verified.")

func test_quest_persistence() -> void:
	print("[Test M7] 5. Testing Quest & Narrative Persistence (Save/Load)...")
	
	# Setup specific quest state
	QuestService.current_act = 2
	QuestService.story_flags["railway_restored"] = true
	QuestService.completed_quests = ["ms01", "ms02", "ms04"]
	
	# Save to test slot 7
	var saved = SaveService.save_game(7)
	assert(saved, "SaveService should succeed saving slot 7")
	
	# Corrupt local state
	QuestService.current_act = 1
	QuestService.story_flags["railway_restored"] = false
	QuestService.completed_quests.clear()
	
	# Load from test slot 7
	var loaded = SaveService.load_game(7)
	assert(loaded, "SaveService should succeed loading slot 7")
	
	assert(QuestService.current_act == 2, "Current act should be restored to 2")
	assert(QuestService.story_flags["railway_restored"] == true, "railway_restored should be restored to true")
	assert(QuestService.completed_quests.size() == 3, "Completed quests count should be 3")
	assert(QuestService.is_quest_completed("ms04"), "ms04 should be completed after reload")
	print(" -> PASS: Quest and story persistence verified.")
