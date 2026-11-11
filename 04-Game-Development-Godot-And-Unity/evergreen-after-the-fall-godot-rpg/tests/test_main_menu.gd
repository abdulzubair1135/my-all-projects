extends Node

# Evergreen: After the Fall - Main Menu Flow Automated Test

func _ready() -> void:
	print("--- TESTING MAIN MENU USER FLOW ---")
	var menu_scene = load("res://scenes/main_menu/MainMenu.tscn").instantiate()
	add_child(menu_scene)
	
	# 1. Open New Game Modal
	menu_scene._on_new_game_pressed()
	assert(menu_scene.new_game_panel.visible == true, "New Game panel must open!")
	
	# 2. Select Danish
	menu_scene._on_select_danish_pressed()
	assert(menu_scene.chosen_protagonist == GameState.PROTAGONIST_DANISH, "Chosen protagonist should be Danish")
	print("[PASS] Selected Danish in New Game modal.")
	
	# 3. Enter Farm Name
	menu_scene.farm_name_edit.text = "Sunrise Valley"
	
	# 4. Confirm Start Game
	menu_scene._on_start_game_confirmed()
	assert(GameState.current_protagonist == GameState.PROTAGONIST_DANISH, "GameState must update to Danish")
	assert(GameState.farm_name == "Sunrise Valley", "Farm name must be Sunrise Valley")
	print("[PASS] New Game session configured: Protagonist: %s, Farm: %s" % [GameState.current_protagonist, GameState.farm_name])
	
	print("--- MAIN MENU FLOW COMPLETED 100% ---")
	get_tree().quit(0)
