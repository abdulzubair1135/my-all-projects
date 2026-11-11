class_name Hitbox
extends Area2D

signal hit_landed(target_hurtbox: Hurtbox, damage_info: DamageInfo)

@export var owner_node: Node2D

var current_damage_info: DamageInfo = null
var targets_hit: Dictionary = {}
var is_active: bool = false

func _ready() -> void:
	if not owner_node and get_parent() is Node2D:
		owner_node = get_parent() as Node2D
	monitoring = false
	monitorable = false
	if not area_entered.is_connected(_on_area_entered):
		area_entered.connect(_on_area_entered)

func activate(damage_info: DamageInfo) -> void:
	current_damage_info = damage_info
	targets_hit.clear()
	is_active = true
	monitoring = true
	# Immediately check any overlapping areas already inside the hitbox
	for area in get_overlapping_areas():
		if area is Hurtbox:
			_check_and_damage_hurtbox(area as Hurtbox)

func deactivate() -> void:
	is_active = false
	monitoring = false
	targets_hit.clear()
	current_damage_info = null

func _on_area_entered(area: Area2D) -> void:
	if not is_active or not current_damage_info:
		return
	if area is Hurtbox:
		_check_and_damage_hurtbox(area as Hurtbox)

func _check_and_damage_hurtbox(hurtbox: Hurtbox) -> void:
	if targets_hit.has(hurtbox):
		return
	# Prevent hitting self
	if hurtbox.owner_node and current_damage_info.source and hurtbox.owner_node == current_damage_info.source:
		return
	targets_hit[hurtbox] = true
	var connected: bool = hurtbox.receive_damage(current_damage_info)
	if connected:
		hit_landed.emit(hurtbox, current_damage_info)
