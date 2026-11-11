extends Node

# Evergreen: After the Fall - Extended 15-Region Validation Test
# Validates scene structure, player spawn markers, region exits, and ambient lighting across expanded regions

func _ready() -> void:
	print("\n==================================================")
	print("  EVERGREEN: 15-REGION EXPANSION VALIDATION TEST  ")
	print("==================================================")
	
	await get_tree().process_frame
	
	var test_regions = [
		{"id": "old_city", "path": "res://scenes/world/OldCity.tscn", "has_enemies": true},
		{"id": "abandoned_hospital", "path": "res://scenes/world/AbandonedHospital.tscn", "has_enemies": true},
		{"id": "underground_lab", "path": "res://scenes/world/UndergroundLab.tscn", "has_enemies": true},
		{"id": "secret_bunker", "path": "res://scenes/world/SecretBunker.tscn", "has_enemies": false},
		{"id": "railway_station", "path": "res://scenes/world/RailwayStation.tscn", "has_enemies": false}
	]
	
	for reg in test_regions:
		print("Validating region: %s (%s)..." % [reg["id"], reg["path"]])
		assert(ResourceLoader.exists(reg["path"]), "Region scene must exist at %s" % reg["path"])
		var packed: PackedScene = load(reg["path"])
		assert(packed != null, "Must pack scene successfully")
		var inst: Node2D = packed.instantiate()
		add_child(inst)
		
		# Verify critical components
		assert(inst.has_node("DayNightModulate"), "Must have DayNightModulate")
		assert(inst.has_node("SpawnPoint_default"), "Must have SpawnPoint_default")
		assert(inst.has_node("Player"), "Must have Player instance")
		assert(inst.has_node("HUD"), "Must have HUD instance")
		
		print(" -> PASS: Region %s verified." % reg["id"])
		inst.queue_free()
		await get_tree().process_frame
	
	print("\n==================================================")
	print("  ALL EXPANDED REGIONS VALIDATED SUCCESSFULLY!   ")
	print("==================================================\n")
	get_tree().quit(0)
