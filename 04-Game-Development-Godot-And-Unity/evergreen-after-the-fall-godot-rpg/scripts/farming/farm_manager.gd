extends Node
class_name FarmManager

# Evergreen: After the Fall - Central Farm Simulation Manager
# Coordinates global day transitions for all crop plots without per-crop timers

var plots: Dictionary = {} # plot_id -> CropPlot node

func _ready() -> void:
	EventBus.day_started.connect(_on_day_started)

func register_plot(plot: CropPlot) -> void:
	plots[plot.plot_id] = plot

func unregister_plot(plot_id: String) -> void:
	if plots.has(plot_id):
		plots.erase(plot_id)

func _on_day_started(_day_number: int) -> void:
	advance_all_crops()

func advance_all_crops() -> void:
	var updated_count: int = 0
	for plot in plots.values():
		if is_instance_valid(plot):
			plot.advance_day()
			updated_count += 1
	print("[FarmManager] Advanced %d crop plots for the new day." % updated_count)

func serialize_all() -> Dictionary:
	var out: Dictionary = {}
	for id in plots.keys():
		var p = plots[id]
		if is_instance_valid(p):
			out[id] = p.serialize()
	return out

func deserialize_all(data: Dictionary) -> void:
	for id in data.keys():
		if plots.has(id) and is_instance_valid(plots[id]):
			plots[id].deserialize(data[id])
