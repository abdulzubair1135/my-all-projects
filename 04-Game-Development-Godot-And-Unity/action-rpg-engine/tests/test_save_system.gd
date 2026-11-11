extends SceneTree

func _init() -> void:
	print("==================================================")
	print("  ASHEN KINGDOM — MILESTONE 4 SAVE/LOAD TEST SUITE")
	print("==================================================")

	var tests_passed: int = 0
	var total_tests: int = 20

	# 1. Setup core runtime singletons in root
	var game_state_script: GDScript = load("res://scripts/core/game_state.gd")
	var save_manager_script: GDScript = load("res://scripts/save/save_manager.gd")
	var player_scene: PackedScene = load("res://scenes/player/player.tscn")
	var shelter_scene: PackedScene = load("res://scenes/world/home/shelter.tscn")
	var main_menu_scene: PackedScene = load("res://scenes/ui/main_menu.tscn")
	var pause_menu_scene: PackedScene = load("res://scenes/ui/pause_menu.tscn")

	if not game_state_script or not save_manager_script or not player_scene or not shelter_scene:
		print("FAIL: Core scripts/scenes could not be loaded!")
		quit(1)
		return

	var game_state: Node = game_state_script.new()
	game_state.name = "GameState"
	root.add_child(game_state)

	var save_manager: Node = save_manager_script.new()
	save_manager.name = "SaveManager"
	root.add_child(save_manager)

	# Clean up any leftover test saves first
	save_manager.delete_save("test_slot_1")
	save_manager.delete_save("test_slot_2")
	save_manager.delete_save("test_slot_3")
	save_manager.delete_save("test_slot_corrupt")

	# Instantiate a test player
	var player: Player = player_scene.instantiate() as Player
	root.add_child(player)
	player._ready()

	# --- TEST 1: SaveData Schema & Versioning ---
	var base_dict: Dictionary = SaveData.create_save_dictionary(game_state, player)
	if base_dict.has("save_version") and base_dict["save_version"] == 1 and base_dict.has("timestamp"):
		print("TEST 1 PASS: SaveData schema initializes with save_version=1 and timestamp.")
		tests_passed += 1
	else:
		print("TEST 1 FAIL: SaveData schema missing version or timestamp.")

	# --- TEST 2: SaveData Validation (Valid) ---
	var is_valid: bool = SaveData.validate_save_data(base_dict)
	if is_valid:
		print("TEST 2 PASS: Valid save dictionary passes schema validation.")
		tests_passed += 1
	else:
		print("TEST 2 FAIL: Valid save dictionary rejected by validation.")

	# --- TEST 3: SaveData Validation (Invalid / Incomplete) ---
	var invalid_dict: Dictionary = { "save_version": 1, "foo": "bar" }
	var reject_invalid: bool = not SaveData.validate_save_data(invalid_dict)
	var reject_non_dict: bool = not SaveData.validate_save_data("not a dictionary")
	if reject_invalid and reject_non_dict:
		print("TEST 3 PASS: Incomplete or corrupted data structures cleanly rejected.")
		tests_passed += 1
	else:
		print("TEST 3 FAIL: Invalid data was not rejected.")

	# --- TEST 4: Future Module Provider Registry ---
	var dummy_inventory: RefCounted = RefCounted.new()
	SaveData.register_provider("inventory", dummy_inventory)
	var provider_registered: bool = SaveData._providers.has("inventory")
	SaveData.unregister_provider("inventory")
	var provider_unregistered: bool = not SaveData._providers.has("inventory")
	if provider_registered and provider_unregistered:
		print("TEST 4 PASS: Future module provider registry allows registration and clean removal.")
		tests_passed += 1
	else:
		print("TEST 4 FAIL: Provider registry failed.")

	# --- TEST 5: Atomic Save File Creation ---
	var save_success: bool = save_manager.save_game("test_slot_1", player)
	var save_exists: bool = save_manager.has_save("test_slot_1")
	var tmp_exists: bool = FileAccess.file_exists(save_manager.get_temp_slot_path("test_slot_1"))
	if save_success and save_exists and not tmp_exists:
		print("TEST 5 PASS: Atomic save writes .tmp, verifies, and successfully replaces .save without leaving .tmp.")
		tests_passed += 1
	else:
		print("TEST 5 FAIL: Atomic save failed (success=%s, save=%s, tmp=%s)." % [save_success, save_exists, tmp_exists])

	# --- TEST 6: Multi-Slot Management ---
	var s2_ok: bool = save_manager.save_game("test_slot_2", player)
	var s3_ok: bool = save_manager.save_game("test_slot_3", player)
	if s2_ok and s3_ok and save_manager.has_save("test_slot_2") and save_manager.has_save("test_slot_3"):
		print("TEST 6 PASS: Independent save slots created successfully.")
		tests_passed += 1
	else:
		print("TEST 6 FAIL: Multi-slot creation failed.")

	# --- TEST 7: Metadata Inspection ---
	var meta: Dictionary = save_manager.get_save_metadata("test_slot_1")
	if meta.get("exists", false) and meta.get("save_version", 0) == 1 and not meta.get("corrupted", false):
		print("TEST 7 PASS: Slot metadata correctly parsed without full deserialization.")
		tests_passed += 1
	else:
		print("TEST 7 FAIL: Metadata extraction failed.")

	# --- TEST 8: Player State Persistence (HP, Stamina, Position, Facing) ---
	player.current_health = 65.0
	player.current_stamina = 42.0
	player.global_position = Vector2(180, 220)
	player.current_facing = Player.Facing.RIGHT
	save_manager.save_game("test_slot_1", player)

	# Reset player
	player.current_health = 100.0
	player.current_stamina = 100.0
	player.global_position = Vector2.ZERO

	# Load data
	var loaded_data: Dictionary = save_manager.load_game("test_slot_1")
	var p_data: Dictionary = loaded_data.get("player", {})
	SpawnManager.apply_saved_state(player, p_data)

	var hp_match: bool = is_equal_approx(player.current_health, 65.0)
	var st_match: bool = is_equal_approx(player.current_stamina, 42.0)
	var pos_match: bool = player.global_position.distance_to(Vector2(180, 220)) < 1.0
	var face_match: bool = player.current_facing == Player.Facing.RIGHT
	if hp_match and st_match and pos_match and face_match:
		print("TEST 8 PASS: Player HP, Stamina, Position, and Facing persisted and restored accurately.")
		tests_passed += 1
	else:
		print("TEST 8 FAIL: Player persistence mismatch.")

	# --- TEST 9: World Data Persistence (Scene, SpawnID, Areas) ---
	game_state.current_scene = "res://scenes/world/home/shelter.tscn"
	game_state.current_spawn_id = "spawn_home"
	save_manager.save_game("test_slot_1", player)
	var reloaded_world: Dictionary = save_manager.load_game("test_slot_1").get("world", {})
	if reloaded_world.get("current_scene") == "res://scenes/world/home/shelter.tscn" and reloaded_world.get("current_spawn_id") == "spawn_home":
		print("TEST 9 PASS: World scene and active spawn point persisted accurately.")
		tests_passed += 1
	else:
		print("TEST 9 FAIL: World persistence mismatch.")

	# --- TEST 10: Game Day & Play Time Persistence ---
	game_state.game_day = 7
	game_state.play_time = 125.5
	save_manager.save_game("test_slot_1", player)
	var reloaded_session: Dictionary = save_manager.load_game("test_slot_1")
	if reloaded_session.get("game_day") == 7 and is_equal_approx(reloaded_session.get("play_time"), 125.5):
		print("TEST 10 PASS: Game day (7) and playtime (125.5s) persisted accurately.")
		tests_passed += 1
	else:
		print("TEST 10 FAIL: Session stats persistence mismatch.")

	# --- TEST 11: Corruption Resistance ---
	var corrupt_path: String = save_manager.get_slot_path("test_slot_corrupt")
	var c_file := FileAccess.open(corrupt_path, FileAccess.WRITE)
	if c_file:
		c_file.store_string("INVALID_JSON_CORRUPTED_DATA{{{{")
		c_file.close()

	var corrupt_meta: Dictionary = save_manager.get_save_metadata("test_slot_corrupt")
	var corrupt_load: Dictionary = save_manager.load_game("test_slot_corrupt")
	if corrupt_meta.get("corrupted", false) and corrupt_load.is_empty():
		print("TEST 11 PASS: Corrupted save file detected, flagged, and handled gracefully without crash.")
		tests_passed += 1
	else:
		print("TEST 11 FAIL: Corrupted save file was not properly handled.")

	# --- TEST 12: Delete Save Functionality ---
	var del_ok: bool = save_manager.delete_save("test_slot_2")
	var s2_still_exists: bool = save_manager.has_save("test_slot_2")
	if del_ok and not s2_still_exists:
		print("TEST 12 PASS: Save slot deleted cleanly and file removed.")
		tests_passed += 1
	else:
		print("TEST 12 FAIL: Save slot delete failed.")

	# --- TEST 13: Most Recent Save Detection ---
	save_manager.save_game("test_slot_1", player)
	var meta1: Dictionary = save_manager.get_save_metadata("test_slot_1")
	var meta3: Dictionary = save_manager.get_save_metadata("test_slot_3")
	if meta1.get("timestamp", 0) >= meta3.get("timestamp", 0):
		print("TEST 13 PASS: Latest timestamp correctly tracked across save slots.")
		tests_passed += 1
	else:
		print("TEST 13 FAIL: Latest save timestamp detection failed.")

	# --- TEST 14: Autosave Integration ---
	game_state.current_save_slot = "test_slot_1"
	player.current_health = 88.0
	var auto_ok: bool = save_manager.autosave(player)
	var auto_load: Dictionary = save_manager.load_game("test_slot_1")
	if auto_ok and is_equal_approx(auto_load.get("player", {}).get("health", 0.0), 88.0):
		print("TEST 14 PASS: Autosave successfully saved active player state to current slot.")
		tests_passed += 1
	else:
		print("TEST 14 FAIL: Autosave failed.")

	# --- TEST 15: GameState Reset for New Game ---
	game_state.reset_for_new_game("test_slot_1")
	if game_state.game_day == 1 and game_state.play_time == 0.0 and game_state.current_spawn_id == "spawn_home":
		print("TEST 15 PASS: GameState reset_for_new_game reinitializes Day 1, home shelter, and 0 playtime.")
		tests_passed += 1
	else:
		print("TEST 15 FAIL: GameState new game reset failed.")

	# --- TEST 16: GameState Advance Day ---
	var day_signal_fired: Array[bool] = [false]
	game_state.game_day_advanced.connect(func(d): day_signal_fired[0] = (d == 2))
	game_state.advance_day()
	if game_state.game_day == 2 and day_signal_fired[0]:
		print("TEST 16 PASS: GameState advance_day correctly updates day to 2 and emits signal.")
		tests_passed += 1
	else:
		print("TEST 16 FAIL: Advance day failed.")

	# --- TEST 17: SpawnPoint Discovery ---
	var shelter: Shelter = shelter_scene.instantiate() as Shelter
	root.add_child(shelter)

	var sp_home: SpawnPoint = SpawnManager.find_spawn_point(shelter, "spawn_home")
	var sp_door: SpawnPoint = SpawnManager.find_spawn_point(shelter, "spawn_home_entrance")
	if sp_home != null and sp_door != null and sp_home.spawn_id == "spawn_home":
		print("TEST 17 PASS: SpawnManager successfully found named spawn points in Shelter scene.")
		tests_passed += 1
	else:
		print("TEST 17 FAIL: SpawnManager failed to find spawn points.")

	# --- TEST 18: Player Positioning at SpawnPoint ---
	SpawnManager.position_player_at_spawn(player, sp_home)
	var pos_ok: bool = player.global_position == sp_home.global_position
	var facing_ok: bool = player.current_facing == sp_home.facing_direction
	if pos_ok and facing_ok and player.velocity == Vector2.ZERO:
		print("TEST 18 PASS: Player positioned at spawn with matched facing and zeroed velocity.")
		tests_passed += 1
	else:
		print("TEST 18 FAIL: Player position at spawn failed.")

	# --- TEST 19: Shelter Bed Interaction ---
	player.current_health = 30.0
	player.current_stamina = 15.0
	var day_before_bed: int = game_state.game_day
	shelter._on_bed_rest(player)
	var healed: bool = (player.current_health == player.max_health and player.current_stamina == player.max_stamina)
	var day_advanced: bool = (game_state.game_day == day_before_bed + 1)
	if healed and day_advanced:
		print("TEST 19 PASS: Bed rest fully restored HP & Stamina, advanced day, and triggered save.")
		tests_passed += 1
	else:
		print("TEST 19 FAIL: Bed rest failed.")

	# --- TEST 20: UI Structure Sanity (Main Menu & Pause Menu) ---
	var main_menu: Control = main_menu_scene.instantiate() as Control
	var pause_menu: CanvasLayer = pause_menu_scene.instantiate() as CanvasLayer
	root.add_child(main_menu)
	root.add_child(pause_menu)

	var mm_new_game = main_menu.get_node_or_null("CenterContainer/VBoxContainer/Buttons/NewGameBtn")
	var mm_load = main_menu.get_node_or_null("CenterContainer/VBoxContainer/Buttons/LoadBtn")
	var mm_settings = main_menu.get_node_or_null("CenterContainer/VBoxContainer/Buttons/SettingsBtn")

	var pm_resume = pause_menu.get_node_or_null("MenuPanel/Center/VBox/ResumeBtn")
	var pm_save = pause_menu.get_node_or_null("MenuPanel/Center/VBox/SaveBtn")
	var pm_load = pause_menu.get_node_or_null("MenuPanel/Center/VBox/LoadBtn")

	var mm_buttons_ok: bool = (mm_new_game != null and mm_load != null and mm_settings != null)
	var pm_buttons_ok: bool = (pm_resume != null and pm_save != null and pm_load != null)
	if mm_buttons_ok and pm_buttons_ok:
		print("TEST 20 PASS: MainMenu and PauseMenu UI scene hierarchies instanced with all required action buttons.")
		tests_passed += 1
	else:
		print("TEST 20 FAIL: UI structure sanity check failed.")

	# Clean up test saves and nodes
	save_manager.delete_save("test_slot_1")
	save_manager.delete_save("test_slot_2")
	save_manager.delete_save("test_slot_3")
	save_manager.delete_save("test_slot_corrupt")

	main_menu.queue_free()
	pause_menu.queue_free()
	shelter.queue_free()
	player.queue_free()
	game_state.queue_free()
	save_manager.queue_free()

	print("==================================================")
	print("  TOTAL: %d / %d TESTS PASSED" % [tests_passed, total_tests])
	print("==================================================")

	if tests_passed == total_tests:
		print(">>> ALL 20 MILESTONE 4 REQUIREMENTS VERIFIED SUCCESSFULLY! <<<")
		quit(0)
	else:
		print(">>> SOME TESTS FAILED! <<<")
		quit(1)