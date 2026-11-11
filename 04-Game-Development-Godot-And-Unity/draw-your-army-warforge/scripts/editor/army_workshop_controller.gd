class_name ArmyWorkshopController
extends Node3D

@onready var camera: Camera3D = $Camera3D
@onready var placement_plane: StaticBody3D = $PlacementPlane
@onready var units_container: Node3D = $UnitsContainer
@onready var preview_container: Node3D = $PreviewContainer

@onready var budget_label: Label = $UI/TopBar/MarginContainer/HBoxContainer/BudgetLabel
@onready var units_label: Label = $UI/TopBar/MarginContainer/HBoxContainer/UnitsLabel
@onready var status_label: Label = $UI/TopBar/MarginContainer/HBoxContainer/StatusLabel
@onready var drawing_toolbar: DrawingToolbar = $UI/ToolbarPanel/DrawingToolbar

var current_army: ArmyLoadout
var active_design: SoldierDesign
var history: EditorHistory = EditorHistory.new()

var is_drawing: bool = false
var draw_points: Array[Vector3] = []
var active_tool: String = "line"
var placement_spacing: float = 1.6
var budget_limit: int = 1000
var max_units_limit: int = 300

func _ready() -> void:
	current_army = ArmyLoadout.new()
	if not GameManager.selected_soldier_design.is_empty():
		active_design = SoldierDesign.deserialize(GameManager.selected_soldier_design)
	else:
		active_design = SoldierDesign.new("player_champion", "Royal Champion")
	current_army.custom_soldiers[active_design.id] = active_design.serialize()
	
	if drawing_toolbar:
		drawing_toolbar.tool_selected.connect(_on_tool_selected)
		drawing_toolbar.clear_clicked.connect(clear_army)
		drawing_toolbar.undo_clicked.connect(undo)
		drawing_toolbar.redo_clicked.connect(redo)
		
	update_ui()

func _on_tool_selected(tool_id: String) -> void:
	active_tool = tool_id

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		if event.keycode == KEY_Z and event.ctrl_pressed:
			undo()
			get_viewport().set_input_as_handled()
		elif event.keycode == KEY_Y and event.ctrl_pressed:
			redo()
			get_viewport().set_input_as_handled()

	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				_start_drawing(event.position)
			else:
				_commit_drawing()
		elif event.button_index == MOUSE_BUTTON_RIGHT and is_drawing:
			_cancel_drawing()
			
	elif event is InputEventMouseMotion and is_drawing:
		_continue_drawing(event.position)

func _raycast_mouse_to_ground(mouse_pos: Vector2) -> Variant:
	var from = camera.project_ray_origin(mouse_pos)
	var dir = camera.project_ray_normal(mouse_pos)
	# Raycast against ground plane Y = 0
	if abs(dir.y) < 0.0001:
		return null
	var t = -from.y / dir.y
	if t < 0:
		return null
	var hit_pos = from + dir * t
	# Keep within deployment zone
	hit_pos.x = clampf(hit_pos.x, -40.0, 40.0)
	hit_pos.z = clampf(hit_pos.z, -30.0, 30.0)
	hit_pos.y = 0.0
	return hit_pos

func _start_drawing(screen_pos: Vector2) -> void:
	var ground_pos = _raycast_mouse_to_ground(screen_pos)
	if ground_pos == null:
		return
	is_drawing = true
	draw_points.clear()
	draw_points.append(ground_pos)
	_update_preview()

func _continue_drawing(screen_pos: Vector2) -> void:
	var ground_pos = _raycast_mouse_to_ground(screen_pos)
	if ground_pos == null:
		return
		
	if active_tool == "freehand":
		if draw_points.is_empty() or draw_points.back().distance_to(ground_pos) > 0.5:
			draw_points.append(ground_pos)
	else:
		if draw_points.size() >= 2:
			draw_points[1] = ground_pos
		else:
			draw_points.append(ground_pos)
			
	_update_preview()

func _calculate_candidate_points() -> Array[Vector3]:
	if draw_points.is_empty():
		return []
		
	match active_tool:
		"line":
			if draw_points.size() < 2:
				return [draw_points[0]]
			return FormationMath.generate_line_points(draw_points[0], draw_points[1], placement_spacing)
		"freehand":
			return FormationMath.generate_freehand_sampled_points(draw_points, placement_spacing)
		"box":
			if draw_points.size() < 2:
				return [draw_points[0]]
			return FormationMath.generate_box_points(draw_points[0], draw_points[1], placement_spacing)
		"circle":
			if draw_points.size() < 2:
				return [draw_points[0]]
			var r = draw_points[0].distance_to(draw_points[1])
			return FormationMath.generate_circle_points(draw_points[0], r, placement_spacing)
		"wedge":
			if draw_points.size() < 2:
				return [draw_points[0]]
			var apex = draw_points[0]
			var base = draw_points[1]
			var width = apex.distance_to(base) * 0.8
			return FormationMath.generate_wedge_points(apex, base, width, placement_spacing)
		_:
			return [draw_points[0]]

func _update_preview() -> void:
	for child in preview_container.get_children():
		child.queue_free()
		
	var candidates = _calculate_candidate_points()
	for p in candidates:
		var preview_mesh = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 0.4
		cyl.bottom_radius = 0.4
		cyl.height = 0.1
		preview_mesh.mesh = cyl
		preview_mesh.position = p + Vector3(0, 0.05, 0)
		
		var mat = StandardMaterial3D.new()
		mat.albedo_color = Color(0.2, 0.8, 0.3, 0.6)
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		preview_mesh.set_surface_override_material(0, mat)
		preview_container.add_child(preview_mesh)

func _commit_drawing() -> void:
	if not is_drawing:
		return
	is_drawing = false
	
	var candidates = _calculate_candidate_points()
	_cancel_drawing() # Clear preview
	
	if candidates.is_empty():
		return
		
	var unit_cost = active_design.calculate_derived_stats().total_cost
	var new_units: Array[Dictionary] = []
	var running_cost = current_army.calculate_total_cost()
	
	for p in candidates:
		# Check limit
		if current_army.units.size() + new_units.size() >= max_units_limit:
			status_label.text = "Max unit limit reached!"
			break
		if running_cost + unit_cost > budget_limit:
			status_label.text = "Budget limit reached!"
			break
			
		var u_dict = {
			"unit_id": "u_" + str(Time.get_unix_time_from_system()) + "_" + str(randi() % 10000),
			"design_id": active_design.id,
			"position": p,
			"rotation_y": 0.0
		}
		new_units.append(u_dict)
		running_cost += unit_cost
		
	if not new_units.is_empty():
		var cmd = EditorCommand.PlaceUnitsCommand.new(current_army, new_units)
		history.execute_command(cmd)
		_rebuild_army_visuals()
		update_ui()

func _cancel_drawing() -> void:
	is_drawing = false
	draw_points.clear()
	for child in preview_container.get_children():
		child.queue_free()

func _rebuild_army_visuals() -> void:
	for child in units_container.get_children():
		child.queue_free()
		
	for u in current_army.units:
		var pos = u.get("position", Vector3.ZERO)
		var d_id = u.get("design_id", "")
		var d_data = current_army.custom_soldiers.get(d_id, {})
		var design = SoldierDesign.deserialize(d_data) if not d_data.is_empty() else active_design
		
		var soldier_model = Unit3D.new()
		soldier_model.position = pos
		soldier_model.setup_from_design(design, 0, u.get("unit_id", "u_0"))
		soldier_model.set_physics_process(false) # Pause AI in editor mode
		units_container.add_child(soldier_model)

func undo() -> void:
	if history.undo():
		_rebuild_army_visuals()
		update_ui()
		status_label.text = "Undo successful"

func redo() -> void:
	if history.redo():
		_rebuild_army_visuals()
		update_ui()
		status_label.text = "Redo successful"

func clear_army() -> void:
	if current_army.units.is_empty():
		return
	var cmd = EditorCommand.DeleteUnitsCommand.new(current_army, current_army.units.duplicate())
	history.execute_command(cmd)
	_rebuild_army_visuals()
	update_ui()
	status_label.text = "Army cleared"

func update_ui() -> void:
	var total_cost = current_army.calculate_total_cost()
	var count = current_army.units.size()
	
	budget_label.text = "Budget: " + str(total_cost) + " / " + str(budget_limit)
	units_label.text = "Units: " + str(count) + " / " + str(max_units_limit)
	
	if total_cost > budget_limit:
		budget_label.add_theme_color_override("font_color", Color(1, 0.3, 0.3))
	else:
		budget_label.add_theme_color_override("font_color", Color(0.9, 0.9, 0.9))

func test_in_practice() -> void:
	var val = current_army.validate_army(budget_limit, max_units_limit)
	if not val.is_valid:
		status_label.text = val.errors[0]
		return
		
	GameManager.active_army_loadout = current_army.serialize()
	GameManager.change_scene("res://scenes/battlefield/battlefield.tscn")

func back_to_menu() -> void:
	GameManager.change_scene("res://scenes/main_menu/main_menu.tscn")
