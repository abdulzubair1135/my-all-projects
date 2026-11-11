extends CharacterBody2D
class_name FarmAnimal

# Evergreen: After the Fall - Farm Animal Life Simulation
# Handles gentle pasture movement, feeding, affection progression, and daily product harvesting (Eggs & Milk)

@export var animal_type: String = "chicken" # "chicken" or "cow"
@export var animal_name: String = "Clucky"
@export var affection: int = 15
@export var is_fed: bool = false
@export var has_product: bool = true

var home_position: Vector2 = Vector2.ZERO
var wander_timer: float = 0.0
var facing_dir: Vector2 = Vector2.LEFT

@onready var sprite: Sprite2D = $Sprite2D
@onready var interact_area: Area2D = $InteractArea

func _ready() -> void:
	add_to_group("animals")
	home_position = position
	_configure_appearance()
	EventBus.day_started.connect(_on_day_started)

func _configure_appearance() -> void:
	if not sprite:
		return
	
	if animal_type == "cow":
		sprite.texture = load("res://assets/characters/animals/cow.png")
		sprite.hframes = 2
		sprite.vframes = 2
	else: # chicken
		sprite.texture = load("res://assets/characters/animals/chicken.png")
		sprite.hframes = 2
		sprite.vframes = 2

func _physics_process(delta: float) -> void:
	wander_timer -= delta
	if wander_timer <= 0.0:
		wander_timer = randf_range(2.5, 6.0)
		if randf() > 0.4:
			# Pick small random offset from home position
			var target = home_position + Vector2(randf_range(-50, 50), randf_range(-40, 40))
			velocity = (target - position).normalized() * (18.0 if animal_type == "chicken" else 12.0)
			facing_dir = velocity.normalized()
		else:
			velocity = Vector2.ZERO
	
	move_and_slide()
	_update_animation()

func _update_animation() -> void:
	if not sprite:
		return
	
	var row = 1 if facing_dir.x > 0 else 0
	var col = 1 if velocity.length() > 2.0 else 0
	sprite.frame = row * 2 + col

func get_interaction_info() -> Dictionary:
	var prompt = "Pet %s" % animal_name
	if has_product:
		prompt = "Collect %s" % ("Egg" if animal_type == "chicken" else "Milk")
	elif not is_fed:
		prompt = "Feed %s" % animal_name
	
	return {
		"id": "animal_" + animal_name.to_lower(),
		"name": animal_name,
		"prompt": prompt
	}

func interact(_player: Node2D) -> void:
	# 1. Collect animal product
	if has_product:
		has_product = false
		var item_id = "produce_egg" if animal_type == "chicken" else "produce_milk"
		var item_name = "Farm Fresh Egg" if animal_type == "chicken" else "Fresh Milk Bottle"
		InventoryService.add_item(item_id, 1)
		affection = min(100, affection + 2)
		EventBus.notification_requested.emit("Collected %s from %s!" % [item_name, animal_name], 2.2)
		return
	
	# 2. Feed animal if player has seeds or food
	if not is_fed:
		var food_item = "seed_turnip" if animal_type == "chicken" else "produce_turnip"
		if InventoryService.has_item(food_item, 1):
			InventoryService.remove_item(food_item, 1)
			is_fed = true
			affection = min(100, affection + 5)
			EventBus.notification_requested.emit("Fed %s with %s. Affection +5 (Now %d/100)!" % [animal_name, food_item, affection], 2.5)
			return
		elif InventoryService.has_item("food_bread", 1):
			InventoryService.remove_item("food_bread", 1)
			is_fed = true
			affection = min(100, affection + 6)
			EventBus.notification_requested.emit("Fed %s fresh bread. Affection +6 (Now %d/100)!" % [animal_name, affection], 2.5)
			return
	
	# 3. Pet animal
	affection = min(100, affection + 3)
	EventBus.notification_requested.emit("Gently petted %s <3. Affection: %d/100" % [animal_name, affection], 2.0)

func _on_day_started(_day: int) -> void:
	advance_day()

func advance_day() -> void:
	if is_fed:
		has_product = true
		is_fed = false
	else:
		has_product = false # Need feed to produce!

func serialize() -> Dictionary:
	return {
		"animal_type": animal_type,
		"animal_name": animal_name,
		"affection": affection,
		"is_fed": is_fed,
		"has_product": has_product,
		"pos_x": position.x,
		"pos_y": position.y
	}

func deserialize(data: Dictionary) -> void:
	animal_type = data.get("animal_type", animal_type)
	animal_name = data.get("animal_name", animal_name)
	affection = int(data.get("affection", affection))
	is_fed = bool(data.get("is_fed", is_fed))
	has_product = bool(data.get("has_product", has_product))
	if data.has("pos_x") and data.has("pos_y"):
		position = Vector2(data["pos_x"], data["pos_y"])
		home_position = position
	_configure_appearance()
