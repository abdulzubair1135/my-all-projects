extends Node

# Evergreen: After the Fall - Crafting & Construction Service
# Manages blueprints, materials validation, Danish's Field Engineer discount perk, and item assembly

var recipes: Dictionary = {
	"recipe_barricade": {
		"id": "recipe_barricade",
		"name": "Wooden Barricade",
		"output_item": "crafted_barricade",
		"output_count": 1,
		"ingredients": {
			"mat_wood": 5
		},
		"category": "Defense"
	},
	"recipe_trap": {
		"id": "recipe_trap",
		"name": "Spike Trap",
		"output_item": "crafted_trap",
		"output_count": 1,
		"ingredients": {
			"mat_wood": 3,
			"mat_stone": 2
		},
		"category": "Defense"
	},
	"recipe_bandage": {
		"id": "recipe_bandage",
		"name": "Sterile Bandage",
		"output_item": "med_bandage",
		"output_count": 1,
		"ingredients": {
			"produce_egg": 1,
			"mat_wood": 1
		},
		"category": "Medical"
	},
	"recipe_bread": {
		"id": "recipe_bread",
		"name": "Fresh Bread",
		"output_item": "food_bread",
		"output_count": 1,
		"ingredients": {
			"produce_turnip": 2
		},
		"category": "Food"
	}
}

func get_recipe(recipe_id: String) -> Dictionary:
	return recipes.get(recipe_id, {})

func can_craft(recipe_id: String) -> bool:
	if not recipes.has(recipe_id):
		return false
	
	var r = recipes[recipe_id]
	var ing = r["ingredients"]
	var is_danish = (GameState.current_protagonist == GameState.PROTAGONIST_DANISH)
	
	for mat_id in ing.keys():
		var required = ing[mat_id]
		# Danish Field Engineer Perk: -1 wood requirement on defenses (min 1)
		if is_danish and r["category"] == "Defense" and mat_id == "mat_wood":
			required = max(1, required - 1)
		if not InventoryService.has_item(mat_id, required):
			return false
	return true

func craft(recipe_id: String) -> bool:
	if not can_craft(recipe_id):
		return false
	
	var r = recipes[recipe_id]
	var ing = r["ingredients"]
	var is_danish = (GameState.current_protagonist == GameState.PROTAGONIST_DANISH)
	
	# Deduct materials
	for mat_id in ing.keys():
		var required = ing[mat_id]
		if is_danish and r["category"] == "Defense" and mat_id == "mat_wood":
			required = max(1, required - 1)
		InventoryService.remove_item(mat_id, required)
	
	# Add output
	InventoryService.add_item(r["output_item"], r["output_count"])
	EventBus.notification_requested.emit("Crafted: %s (x%d)" % [r["name"], r["output_count"]], 2.2)
	return true
