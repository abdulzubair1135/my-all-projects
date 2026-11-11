extends Node
class_name NightDefenseDirector

# Evergreen: After the Fall - Night Defense & Horde Director
# Coordinates nocturnal infected spawns, perimeter defense alerts, and wave completion rewards

@export var enabled: bool = true

const INFECTED_SCENE = preload("res://scenes/enemies/InfectedBase.tscn")

var active_enemies: Array[Node2D] = []
var wave_in_progress: bool = false
var wave_number: int = 1

# Perimeter spawn locations (North gate, East forest trail, South fence)
const SPAWN_POINTS = [
	Vector2(480, 40), # North entrance road
	Vector2(900, 340), # East forest path
	Vector2(600, 580) # South-east fence line
]

func _ready() -> void:
	EventBus.night_started.connect(_on_night_started)

func _on_night_started(night_num: int) -> void:
	if not enabled:
		return
	
	wave_number = night_num
	EventBus.notification_requested.emit("WARNING: Night has fallen! Infected detected near the farm boundary.", 4.0)
	# Stagger spawn slightly after dusk warning
	get_tree().create_timer(3.0).timeout.connect(func(): spawn_night_wave(2 + min(night_num, 4)))

func spawn_night_wave(count: int = 3) -> void:
	wave_in_progress = true
	var parent_world = get_parent()
	if not parent_world:
		return
	
	var enemies_container = parent_world.get_node_or_null("YSortProps")
	if not enemies_container:
		enemies_container = parent_world
	
	for i in range(count):
		var enemy: InfectedBase = INFECTED_SCENE.instantiate()
		var spawn_pos = SPAWN_POINTS[i % SPAWN_POINTS.size()]
		# Add small random jitter
		spawn_pos += Vector2(randf_range(-20, 20), randf_range(-20, 20))
		enemy.position = spawn_pos
		
		# Mix in 1 sprinter for every 3 drifters
		if i % 3 == 2:
			enemy.archetype = "sprinter"
		else:
			enemy.archetype = "drifter"
		
		enemies_container.add_child(enemy)
		active_enemies.append(enemy)
		enemy.tree_exited.connect(_on_enemy_defeated.bind(enemy))
	
	print("[NightDefenseDirector] Spawned wave of %d infected for Night %d." % [count, wave_number])

func _on_enemy_defeated(enemy: Node2D) -> void:
	if active_enemies.has(enemy):
		active_enemies.erase(enemy)
	
	if wave_in_progress and active_enemies.is_empty():
		wave_in_progress = false
		EventBus.notification_requested.emit("PERIMETER SECURED: All infected cleared! +50 Valley Defense XP", 3.5)
		print("[NightDefenseDirector] Wave %d cleared successfully!" % wave_number)
