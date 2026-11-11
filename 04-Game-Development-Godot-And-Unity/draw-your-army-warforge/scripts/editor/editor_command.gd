class_name EditorCommand
extends RefCounted

func execute() -> void:
	pass

func undo() -> void:
	pass

# Concrete command: Placement
class PlaceUnitsCommand extends EditorCommand:
	var target_army: ArmyLoadout
	var placed_units: Array[Dictionary]
	
	func _init(army: ArmyLoadout, units: Array[Dictionary]) -> void:
		target_army = army
		placed_units = units
		
	func execute() -> void:
		for u in placed_units:
			target_army.units.append(u)
			
	func undo() -> void:
		for u in placed_units:
			var idx = target_army.units.find(u)
			if idx != -1:
				target_army.units.remove_at(idx)

# Concrete command: Deletion / Clear
class DeleteUnitsCommand extends EditorCommand:
	var target_army: ArmyLoadout
	var removed_units: Array[Dictionary]
	
	func _init(army: ArmyLoadout, units: Array[Dictionary]) -> void:
		target_army = army
		removed_units = units
		
	func execute() -> void:
		for u in removed_units:
			var idx = target_army.units.find(u)
			if idx != -1:
				target_army.units.remove_at(idx)
				
	func undo() -> void:
		for u in removed_units:
			target_army.units.append(u)
