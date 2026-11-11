class_name KingdomTerrainBuilder
extends Node3D

# Procedural kingdom structures: Castle Towers, Ramparts, Banners, and Trees

func _ready() -> void:
	build_kingdom_scenery()

func build_kingdom_scenery() -> void:
	# Materials
	var stone_mat = StandardMaterial3D.new()
	stone_mat.albedo_color = Color(0.38, 0.4, 0.44)
	stone_mat.roughness = 0.9
	
	var dark_stone = StandardMaterial3D.new()
	dark_stone.albedo_color = Color(0.25, 0.27, 0.3)
	dark_stone.roughness = 0.95
	
	var wood_mat = StandardMaterial3D.new()
	wood_mat.albedo_color = Color(0.35, 0.22, 0.12)
	
	var leaves_mat = StandardMaterial3D.new()
	leaves_mat.albedo_color = Color(0.18, 0.35, 0.15)
	leaves_mat.roughness = 0.8
	
	var gold_mat = StandardMaterial3D.new()
	gold_mat.albedo_color = Color(0.95, 0.82, 0.25)
	gold_mat.metallic = 0.9
	gold_mat.roughness = 0.2
	
	var blue_banner_mat = StandardMaterial3D.new()
	blue_banner_mat.albedo_color = Color(0.18, 0.4, 0.85)
	
	var red_banner_mat = StandardMaterial3D.new()
	red_banner_mat.albedo_color = Color(0.85, 0.2, 0.2)
	
	# 1. Four Castle Fortress Towers at the battlefield corners
	var tower_coords = [
		Vector3(-28, 0, 24), Vector3(28, 0, 24),   # Blue Kingdom Side
		Vector3(-28, 0, -24), Vector3(28, 0, -24)  # Red Kingdom Side
	]
	
	for i in range(tower_coords.size()):
		var t_pos = tower_coords[i]
		var is_blue = t_pos.z > 0
		
		# Tower Base
		var tower = MeshInstance3D.new()
		var cyl = CylinderMesh.new()
		cyl.top_radius = 2.4
		cyl.bottom_radius = 2.8
		cyl.height = 7.0
		tower.mesh = cyl
		tower.position = t_pos + Vector3(0, 3.5, 0)
		tower.set_surface_override_material(0, stone_mat)
		add_child(tower)
		
		# Tower Battlement Crown
		var battlement = MeshInstance3D.new()
		var b_cyl = CylinderMesh.new()
		b_cyl.top_radius = 2.8
		b_cyl.bottom_radius = 2.4
		b_cyl.height = 1.2
		battlement.mesh = b_cyl
		battlement.position = t_pos + Vector3(0, 7.5, 0)
		battlement.set_surface_override_material(0, dark_stone)
		add_child(battlement)
		
		# Castle Banner Pole
		var pole = MeshInstance3D.new()
		var p_cyl = CylinderMesh.new()
		p_cyl.top_radius = 0.08
		p_cyl.bottom_radius = 0.08
		p_cyl.height = 4.0
		pole.mesh = p_cyl
		pole.position = t_pos + Vector3(0, 9.8, 0)
		pole.set_surface_override_material(0, wood_mat)
		add_child(pole)
		
		# Flying Banner Flag
		var banner = MeshInstance3D.new()
		var b_box = BoxMesh.new()
		b_box.size = Vector3(0.04, 1.4, 1.8)
		banner.mesh = b_box
		banner.position = t_pos + Vector3(0, 10.5, 0.9)
		banner.set_surface_override_material(0, blue_banner_mat if is_blue else red_banner_mat)
		add_child(banner)

	# 2. Kingdom Perimeter Stone Walls
	for side in [-1, 1]:
		# Left and Right Stone Ramparts
		var wall = MeshInstance3D.new()
		var w_box = BoxMesh.new()
		w_box.size = Vector3(2.0, 4.0, 44.0)
		wall.mesh = w_box
		wall.position = Vector3(side * 28.0, 2.0, 0.0)
		wall.set_surface_override_material(0, dark_stone)
		add_child(wall)
		
	# 3. Surrounding Forest Trees on the outer plains
	var tree_seeds = [
		Vector3(-35, 0, 10), Vector3(-38, 0, -8), Vector3(-36, 0, -20),
		Vector3(35, 0, 15), Vector3(38, 0, -12), Vector3(37, 0, 4),
		Vector3(-15, 0, 34), Vector3(12, 0, 36), Vector3(-18, 0, -34), Vector3(16, 0, -35)
	]
	
	for t_pos in tree_seeds:
		# Tree Trunk
		var trunk = MeshInstance3D.new()
		var tr_cyl = CylinderMesh.new()
		tr_cyl.top_radius = 0.35
		tr_cyl.bottom_radius = 0.5
		tr_cyl.height = 3.0
		trunk.mesh = tr_cyl
		trunk.position = t_pos + Vector3(0, 1.5, 0)
		trunk.set_surface_override_material(0, wood_mat)
		add_child(trunk)
		
		# Pine Foliage Cone
		var foliage = MeshInstance3D.new()
		var cone = CylinderMesh.new()
		cone.top_radius = 0.1
		cone.bottom_radius = 2.2
		cone.height = 4.2
		foliage.mesh = cone
		foliage.position = t_pos + Vector3(0, 4.2, 0)
		foliage.set_surface_override_material(0, leaves_mat)
		add_child(foliage)
