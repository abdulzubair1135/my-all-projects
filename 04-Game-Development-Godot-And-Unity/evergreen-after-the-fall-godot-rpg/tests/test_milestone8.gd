extends Node

# Evergreen: After the Fall - Milestone 8 Automated Test Suite
# Tests AudioService synthesis, TouchControls mobile input synthesis, Settings persistence, and system-wide integration

func _ready() -> void:
	print("\n=======================================================")
	print("--- EVERGREEN: MILESTONE 8 VERIFICATION TEST SUITE ---")
	print("=======================================================")
	
	await get_tree().process_frame
	
	test_audio_service_synthesis_and_volume()
	test_settings_and_accessibility_persistence()
	await test_touch_controls_input_synthesis()
	test_export_presets_configuration()
	test_system_wide_singleton_registry()
	
	print("\n=======================================================")
	print(">>> ALL MILESTONE 8 TESTS PASSED SUCCESSFULLY! (100%) <<<")
	print("=======================================================\n")
	get_tree().quit(0)

func test_audio_service_synthesis_and_volume() -> void:
	print("[Test M8] 1. Testing Procedural Audio Synthesis & Volume Mixing...")
	
	assert(AudioService != null, "AudioService autoload must exist")
	
	# Verify soundbank generation
	var expected_sfx = [
		"ui_click", "attack_swing", "hit_impact", "harvest",
		"morning_chime", "quest_fanfare", "night_warning", "zombie_growl"
	]
	for sfx in expected_sfx:
		assert(AudioService.sfx_cache.has(sfx), "Soundbank must contain %s" % sfx)
		var stream: AudioStreamWAV = AudioService.sfx_cache[sfx]
		assert(stream.data.size() > 0, "%s audio buffer must not be empty" % sfx)
	
	# Test playback without exceptions
	AudioService.play_sfx("ui_click", 1.2)
	AudioService.play_sfx("attack_swing")
	AudioService.play_sfx("harvest")
	
	# Test volume controls
	AudioService.set_master_volume(0.65)
	AudioService.set_music_volume(0.5)
	AudioService.set_sfx_volume(0.8)
	assert(abs(AudioService.master_volume - 0.65) < 0.01, "Master volume should be 0.65")
	assert(abs(AudioService.music_volume - 0.5) < 0.01, "Music volume should be 0.5")
	assert(abs(AudioService.sfx_volume - 0.8) < 0.01, "SFX volume should be 0.8")
	print(" -> PASS: Procedural soundbank synthesis and volume control verified.")

func test_settings_and_accessibility_persistence() -> void:
	print("[Test M8] 2. Testing Settings & Accessibility Persistence...")
	
	# Modify settings
	GameState.screen_shake_enabled = false
	GameState.damage_numbers_enabled = true
	GameState.touch_controls_mode = "always"
	GameState.colorblind_mode = "protanopia"
	GameState.text_scale = 1.25
	
	GameState.save_settings()
	
	# Mutate memory state
	GameState.screen_shake_enabled = true
	GameState.touch_controls_mode = "never"
	GameState.colorblind_mode = "none"
	GameState.text_scale = 1.0
	
	# Reload from disk
	GameState.load_settings()
	
	assert(GameState.screen_shake_enabled == false, "Screen shake should be reloaded as false")
	assert(GameState.touch_controls_mode == "always", "Touch mode should be reloaded as always")
	assert(GameState.colorblind_mode == "protanopia", "Colorblind should be reloaded as protanopia")
	assert(abs(GameState.text_scale - 1.25) < 0.01, "Text scale should be reloaded as 1.25")
	print(" -> PASS: Settings and accessibility configuration persistence verified.")

func test_touch_controls_input_synthesis() -> void:
	print("[Test M8] 3. Testing Mobile / Android Touch Controls & Input Synthesis...")
	
	var touch_scene = load("res://scenes/ui/TouchControls.tscn")
	var touch_ui: TouchControls = touch_scene.instantiate()
	touch_ui.force_visible_for_testing = true
	add_child(touch_ui)
	await get_tree().process_frame
	
	# Test synthetic movement right
	touch_ui._synthesize_movement_actions(Vector2(0.9, 0.0))
	assert(Input.is_action_pressed("move_right"), "move_right should be active from virtual joystick")
	assert(not Input.is_action_pressed("move_left"), "move_left should not be active")
	
	# Test synthetic movement up-left
	touch_ui._synthesize_movement_actions(Vector2(-0.8, -0.8))
	assert(Input.is_action_pressed("move_left"), "move_left should be active")
	assert(Input.is_action_pressed("move_up"), "move_up should be active")
	
	# Test joystick release / reset
	touch_ui._reset_joystick()
	assert(not Input.is_action_pressed("move_left"), "move_left should release after reset")
	assert(not Input.is_action_pressed("move_up"), "move_up should release after reset")
	
	# Test action buttons
	touch_ui._press_action("attack")
	assert(Input.is_action_pressed("attack"), "attack action should be active")
	touch_ui._release_action("attack")
	assert(not Input.is_action_pressed("attack"), "attack action should be released")
	
	touch_ui.queue_free()
	print(" -> PASS: Virtual joystick and touch action input synthesis verified.")

func test_export_presets_configuration() -> void:
	print("[Test M8] 4. Testing Export Presets Configuration File...")
	
	assert(FileAccess.file_exists("res://export_presets.cfg"), "export_presets.cfg must exist")
	var file = FileAccess.open("res://export_presets.cfg", FileAccess.READ)
	var content = file.get_as_text()
	file.close()
	
	assert("Windows Desktop" in content, "Must contain Windows Desktop export preset")
	assert("Android (Google Play)" in content, "Must contain Android export preset")
	assert("com.evergreen.afterthefall" in content, "Must declare unique Android package ID")
	assert("GAME_SIMULATION" in content, "Must declare Google Play app category")
	print(" -> PASS: Export presets validated for Windows and Android/Google Play.")

func test_system_wide_singleton_registry() -> void:
	print("[Test M8] 5. Testing Full System-Wide Architecture & Autoload Registry...")
	
	var expected_autoloads = [
		GameState,
		EventBus,
		InventoryService,
		SaveService,
		CraftingService,
		RelationshipService,
		WorldManager,
		QuestService,
		AudioService
	]
	
	for s in expected_autoloads:
		assert(s != null and is_instance_valid(s), "Autoload singleton %s must be active and valid" % s.name)
	
	print(" -> PASS: All 9 core architecture subsystems verified in scene tree.")
