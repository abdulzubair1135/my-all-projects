extends SceneTree

func _init() -> void:
	print("==================================================")
	print("  ASHEN KINGDOM — MILESTONE 5 WORLD SYSTEMS TEST SUITE")
	print("==================================================")

	var tests_passed: int = 0
	var total_tests: int = 20

	# 1. Setup core runtime singletons in root
	var game_state_script: GDScript = load("res://scripts/core/game_state.gd")
	var save_manager_script: GDScript = load("res://scripts/save/save_manager.gd")
	var shore_scene: PackedScene = load("res://scenes/world/shore/the_shore.tscn")
	var shelter_scene: PackedScene = load("res://scenes/world/home/shelter.tscn")

	if not game_state_script or not save_manager_script or not shore_scene or not shelter_scene:
		print("FAIL: Core scripts/scenes could not be loaded!")
		quit(1)
		return

	var game_state: Node = game_state_script.new()
	game_state.name = "GameState"
	root.add_child(game_state)

	var save_manager: Node = save_manager_script.new()
	save_manager.name = "SaveManager"
	root.add_child(save_manager)

	# Clean up any leftover test saves
	save_manager.delete_save("test_m5_slot")

	# Instantiate The Shore scene
	var shore: TheShore = shore_scene.instantiate() as TheShore
	root.add_child(shore)
	shore._ready()

	# --- TEST 1: Shore scene loads ---
	if shore != null and shore.ground_container != null and shore.obstacles_container != null:
		print("TEST 1 PASS: The Shore scene loads with terrain, obstacles, and manager hierarchies.")
		tests_passed += 1
	else:
		print("TEST 1 FAIL: Shore scene failed to load.")

	# --- TEST 2: Player spawn_shore exists and positions player ---
	var sp_shore: SpawnPoint = SpawnManager.find_spawn_point(shore, "spawn_shore")
	if sp_shore != null and sp_shore.spawn_id == "spawn_shore":
		SpawnManager.position_player_at_spawn(shore.player, sp_shore)
		var at_pos := shore.player.global_position == sp_shore.global_position
		if at_pos:
			print("TEST 2 PASS: spawn_shore exists and accurately positions player on the beach.")
			tests_passed += 1
		else:
			print("TEST 2 FAIL: Player position did not match spawn_shore.")
	else:
		print("TEST 2 FAIL: spawn_shore not found.")

	# --- TEST 3: Forest transition / spawn_shore_forest exists ---
	var sp_forest: SpawnPoint = SpawnManager.find_spawn_point(shore, "spawn_shore_forest")
	if sp_forest != null and sp_forest.spawn_id == "spawn_shore_forest":
		print("TEST 3 PASS: Forest entrance spawn (spawn_shore_forest) exists in The Shore.")
		tests_passed += 1
	else:
		print("TEST 3 FAIL: spawn_shore_forest not found.")

	# --- TEST 4: Shelter transition and Shore door connection ---
	var shelter: Shelter = shelter_scene.instantiate() as Shelter
	root.add_child(shelter)
	var shore_door = shelter.get_node_or_null("Interactables/ShoreDoorInteractable")
	if shore_door != null:
		print("TEST 4 PASS: Ruined Shelter contains ShoreDoorInteractable connecting back to The Shore.")
		tests_passed += 1
	else:
		print("TEST 4 FAIL: ShoreDoorInteractable missing in Shelter.")

	# --- TEST 5: World time initializes ---
	var wt := WorldTime.new()
	wt.is_paused = true
	wt.set_time(8, 0)
	if wt.hour == 8 and wt.minute == 0 and wt.get_time_string() == "08:00" and wt.current_phase == WorldTime.Phase.MORNING:
		print("TEST 5 PASS: WorldTime initializes with 24-hour clock and morning phase at 08:00.")
		tests_passed += 1
	else:
		print("TEST 5 FAIL: WorldTime initialization mismatch.")

	# --- TEST 6: Time advances ---
	var initial_sec := wt.time_seconds
	wt.advance_time(3600.0) # 1 hour
	if wt.hour == 9 and is_equal_approx(wt.time_seconds, initial_sec + 3600.0):
		print("TEST 6 PASS: WorldTime advances time monotonically (08:00 -> 09:00).")
		tests_passed += 1
	else:
		print("TEST 6 FAIL: Time advance failed.")

	# --- TEST 7: Day advances on 24-hour rollover ---
	var initial_day := wt.game_day
	wt.set_time(23, 59)
	wt.advance_time(120.0) # cross midnight
	if wt.game_day == initial_day + 1 and wt.hour == 0:
		print("TEST 7 PASS: Game day correctly increments when time rolls over midnight.")
		tests_passed += 1
	else:
		print("TEST 7 FAIL: Midnight day rollover failed.")

	# --- TEST 8: Night detection works ---
	wt.set_time(22, 0) # 22:00 -> Night
	var is_night_22: bool = wt.is_night
	wt.set_time(13, 0) # 13:00 -> Day
	var is_night_13: bool = wt.is_night
	if is_night_22 and not is_night_13:
		print("TEST 8 PASS: Night detection verified (22:00 = night, 13:00 = day).")
		tests_passed += 1
	else:
		print("TEST 8 FAIL: Night detection mismatch.")

	# --- TEST 9: Season initializes correctly ---
	var sm := SeasonManager.new()
	if sm.current_season == SeasonManager.Season.SPRING and sm.season_day == 1 and sm.year == 1:
		print("TEST 9 PASS: SeasonManager initializes at Spring Day 1 Year 1.")
		tests_passed += 1
	else:
		print("TEST 9 FAIL: SeasonManager initialization failed.")

	# --- TEST 10: Season advances correctly ---
	sm.set_season_state(0, 30, 1) # Spring Day 30
	sm.advance_day() # Should trigger Summer Day 1
	if sm.current_season == SeasonManager.Season.SUMMER and sm.season_day == 1:
		print("TEST 10 PASS: Season correctly advances from Spring to Summer.")
		tests_passed += 1
	else:
		print("TEST 10 FAIL: Season advance to Summer failed.")

	# --- TEST 11: Year rollover works ---
	sm.set_season_state(3, 30, 1) # Winter Day 30 Year 1
	sm.advance_day() # Should rollover to Spring Day 1 Year 2
	if sm.current_season == SeasonManager.Season.SPRING and sm.season_day == 1 and sm.year == 2:
		print("TEST 11 PASS: Year rollover verified (Winter Year 1 -> Spring Year 2).")
		tests_passed += 1
	else:
		print("TEST 11 FAIL: Year rollover failed.")

	# --- TEST 12: Weather state initializes ---
	var wm := WeatherManager.new()
	if wm.current_weather == "clear":
		print("TEST 12 PASS: WeatherManager initializes with clear weather.")
		tests_passed += 1
	else:
		print("TEST 12 FAIL: WeatherManager initial weather is not clear.")

	# --- TEST 13: Weather transitions work ---
	var weather_changed_signal: Array[String] = [""]
	wm.weather_changed.connect(func(w): weather_changed_signal[0] = w)
	wm.set_weather("rain", 150.0)
	var rain_ok: bool = (wm.current_weather == "rain" and weather_changed_signal[0] == "rain")
	wm.set_weather("fog", 100.0)
	var fog_ok: bool = (wm.current_weather == "fog" and weather_changed_signal[0] == "fog")
	if rain_ok and fog_ok:
		print("TEST 13 PASS: Weather transitions successfully between Clear, Rain, and Fog with signals.")
		tests_passed += 1
	else:
		print("TEST 13 FAIL: Weather transition failed.")

	# --- TEST 14: Temperature calculation works ---
	var tm := TemperatureManager.new()
	# Summer (idx 1) at 14:00 (peak) in clear weather: base 28 + diurnal 5 = 33.0
	var summer_noon: float = tm.update_temperature(1, 14, "clear")
	# Winter (idx 3) at 04:00 (coldest) in clear weather: base 0 + diurnal -5 = -5.0
	var winter_night: float = tm.update_temperature(3, 4, "clear")
	# Rain cools by -4.0
	var summer_rain: float = tm.update_temperature(1, 14, "rain")
	if summer_noon > 30.0 and winter_night < 0.0 and summer_rain < summer_noon:
		print("TEST 14 PASS: Temperature calculation accurately models season (Summer=%.1f°C, Winter=%.1f°C) and weather." % [summer_noon, winter_night])
		tests_passed += 1
	else:
		print("TEST 14 FAIL: Temperature calculation mismatch (Summer=%.1f, Winter=%.1f, Rain=%.1f)." % [summer_noon, winter_night, summer_rain])

	# --- TEST 15: GameState stores world time, season, year, weather, and temperature ---
	game_state.game_time = "14:30"
	game_state.season = 1
	game_state.season_day = 15
	game_state.year = 2
	game_state.weather = "rain"
	game_state.temperature = 24.5
	if game_state.season == 1 and game_state.year == 2 and game_state.weather == "rain" and is_equal_approx(game_state.temperature, 24.5):
		print("TEST 15 PASS: GameState stores all Milestone 5 world time and environmental attributes.")
		tests_passed += 1
	else:
		print("TEST 15 FAIL: GameState attribute storage mismatch.")

	# --- TEST 16: SaveManager persists world time ---
	save_manager.save_game("test_m5_slot", shore.player)
	var loaded_data: Dictionary = save_manager.load_game("test_m5_slot")
	if loaded_data.get("game_time") == "14:30":
		print("TEST 16 PASS: SaveManager faithfully persists and reloads game_time (14:30).")
		tests_passed += 1
	else:
		print("TEST 16 FAIL: SaveManager game_time persistence mismatch.")

	# --- TEST 17: SaveManager persists season and year ---
	var loaded_world: Dictionary = loaded_data.get("world", {})
	if loaded_world.get("season") == 1 and loaded_world.get("season_day") == 15 and loaded_world.get("year") == 2:
		print("TEST 17 PASS: SaveManager faithfully persists and reloads Season (1), Season Day (15), and Year (2).")
		tests_passed += 1
	else:
		print("TEST 17 FAIL: SaveManager season persistence mismatch.")

	# --- TEST 18: SaveManager persists weather and temperature ---
	if loaded_world.get("weather") == "rain" and is_equal_approx(float(loaded_world.get("temperature", 0.0)), 24.5):
		print("TEST 18 PASS: SaveManager faithfully persists and reloads weather ('rain') and temperature (24.5°C).")
		tests_passed += 1
	else:
		print("TEST 18 FAIL: SaveManager weather/temperature persistence mismatch.")

	# --- TEST 19: ResourceNode components instantiate and report interactions ---
	var node_count := shore.resources_container.get_child_count()
	var first_res: ResourceNode = shore.resources_container.get_child(0) as ResourceNode if node_count > 0 else null
	var harvested_event: Array[String] = [""]
	if first_res:
		first_res.harvested.connect(func(res_id, _amt): harvested_event[0] = res_id)
		first_res.interact(shore.player)
	if node_count >= 3 and harvested_event[0] != "":
		print("TEST 19 PASS: %d ResourceNode components active; interaction reports harvest event without error." % node_count)
		tests_passed += 1
	else:
		print("TEST 19 FAIL: ResourceNode verification failed.")

	# --- TEST 20: Wildlife entities (Crab, Seagull) instantiate with valid states ---
	var crab := Crab.new()
	var gull := Seagull.new()
	root.add_child(crab)
	root.add_child(gull)
	var crab_ok: bool = (crab.current_state == WildlifeBase.State.IDLE or crab.current_state == WildlifeBase.State.WANDER)
	var gull_ok: bool = (gull.current_state == WildlifeBase.State.IDLE or gull.current_state == WildlifeBase.State.WANDER)
	if crab_ok and gull_ok and crab.wander_speed > 0.0 and gull.flee_speed > 0.0:
		print("TEST 20 PASS: Wildlife entities (Crab, Seagull) initialize cleanly with non-combat wander/flee parameters.")
		tests_passed += 1
	else:
		print("TEST 20 FAIL: Wildlife entities verification failed.")

	# Clean up
	crab.queue_free()
	gull.queue_free()
	wt.queue_free()
	sm.queue_free()
	wm.queue_free()
	tm.queue_free()
	shore.queue_free()
	shelter.queue_free()
	game_state.queue_free()
	save_manager.delete_save("test_m5_slot")
	save_manager.queue_free()

	print("==================================================")
	print("  TOTAL: %d / %d TESTS PASSED" % [tests_passed, total_tests])
	print("==================================================")

	if tests_passed == total_tests:
		print(">>> ALL 20 MILESTONE 5 REQUIREMENTS VERIFIED SUCCESSFULLY! <<<")
		quit(0)
	else:
		print(">>> SOME TESTS FAILED! <<<")
		quit(1)