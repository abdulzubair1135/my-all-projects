class_name FormationMath
extends RefCounted

static func generate_line_points(start_pos: Vector3, end_pos: Vector3, spacing: float = 1.6) -> Array[Vector3]:
	var points: Array[Vector3] = []
	var diff = end_pos - start_pos
	diff.y = 0.0
	var length = diff.length()
	if length < 0.1:
		points.append(start_pos)
		return points
		
	var dir = diff.normalized()
	var count = int(floor(length / spacing)) + 1
	var actual_spacing = length / max(1, count - 1) if count > 1 else 0.0
	
	for i in range(count):
		points.append(start_pos + dir * (i * actual_spacing))
	return points

static func generate_freehand_sampled_points(raw_path: Array[Vector3], spacing: float = 1.6) -> Array[Vector3]:
	var points: Array[Vector3] = []
	if raw_path.is_empty():
		return points
	if raw_path.size() == 1:
		points.append(raw_path[0])
		return points
		
	var last_placed = raw_path[0]
	points.append(last_placed)
	var accumulated_dist: float = 0.0
	
	for i in range(1, raw_path.size()):
		var p1 = raw_path[i - 1]
		var p2 = raw_path[i]
		p1.y = 0.0
		p2.y = 0.0
		var seg_len = p1.distance_to(p2)
		if seg_len < 0.001:
			continue
			
		var dir = (p2 - p1).normalized()
		var curr_offset = 0.0
		
		while curr_offset + (spacing - accumulated_dist) <= seg_len:
			var step = spacing - accumulated_dist
			curr_offset += step
			var candidate = p1 + dir * curr_offset
			points.append(candidate)
			accumulated_dist = 0.0
			
		accumulated_dist += (seg_len - curr_offset)
		
	return points

static func generate_box_points(corner_a: Vector3, corner_b: Vector3, spacing: float = 1.6) -> Array[Vector3]:
	var points: Array[Vector3] = []
	var min_x = min(corner_a.x, corner_b.x)
	var max_x = max(corner_a.x, corner_b.x)
	var min_z = min(corner_a.z, corner_b.z)
	var max_z = max(corner_a.z, corner_b.z)
	
	var count_x = max(1, int(floor((max_x - min_x) / spacing)) + 1)
	var count_z = max(1, int(floor((max_z - min_z) / spacing)) + 1)
	
	var step_x = (max_x - min_x) / max(1, count_x - 1) if count_x > 1 else 0.0
	var step_z = (max_z - min_z) / max(1, count_z - 1) if count_z > 1 else 0.0
	
	for ix in range(count_x):
		for iz in range(count_z):
			points.append(Vector3(min_x + ix * step_x, 0.0, min_z + iz * step_z))
	return points

static func generate_circle_points(center: Vector3, radius: float, spacing: float = 1.6) -> Array[Vector3]:
	var points: Array[Vector3] = []
	if radius < 0.5:
		points.append(center)
		return points
		
	var circumference = 2.0 * PI * radius
	var count = max(3, int(floor(circumference / spacing)))
	var angle_step = (2.0 * PI) / float(count)
	
	for i in range(count):
		var ang = i * angle_step
		points.append(center + Vector3(cos(ang) * radius, 0.0, sin(ang) * radius))
	return points

static func generate_wedge_points(apex: Vector3, base_center: Vector3, width: float, spacing: float = 1.6) -> Array[Vector3]:
	var points: Array[Vector3] = []
	points.append(apex)
	var forward = (base_center - apex)
	forward.y = 0.0
	var depth = forward.length()
	if depth < 0.5:
		return points
		
	var dir = forward.normalized()
	var right = Vector3(-dir.z, 0.0, dir.x)
	var rows = max(2, int(floor(depth / spacing)) + 1)
	
	for r in range(1, rows):
		var t = float(r) / float(rows - 1)
		var row_center = apex + dir * (r * spacing)
		var current_width = width * t
		var units_in_row = r + 1
		var row_step = current_width / max(1, units_in_row - 1)
		for u in range(units_in_row):
			var offset = - (current_width * 0.5) + u * row_step
			points.append(row_center + right * offset)
	return points
