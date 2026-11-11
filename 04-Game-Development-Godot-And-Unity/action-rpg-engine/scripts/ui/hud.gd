class_name HUD
extends CanvasLayer

@onready var health_bar: ProgressBar = $MarginContainer/VBoxContainer/HealthBar
@onready var stamina_bar: ProgressBar = $MarginContainer/VBoxContainer/StaminaBar
@onready var health_label: Label = $MarginContainer/VBoxContainer/HealthBar/HealthLabel
@onready var stamina_label: Label = $MarginContainer/VBoxContainer/StaminaBar/StaminaLabel
@onready var debug_label: Label = $DebugContainer/DebugLabel
@onready var debug_container: Control = $DebugContainer

var tracked_player: Player = null
var debug_enabled: bool = true

func _ready() -> void:
	if debug_container:
		debug_container.visible = debug_enabled

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.physical_keycode == KEY_F3:
			debug_enabled = not debug_enabled
			if debug_container:
				debug_container.visible = debug_enabled

func _process(_delta: float) -> void:
	if debug_enabled and tracked_player and debug_label:
		_update_debug_overlay()

func register_player(player: Player) -> void:
	tracked_player = player
	if tracked_player:
		if not player.health_changed.is_connected(update_health):
			player.health_changed.connect(update_health)
		if not player.stamina_changed.is_connected(update_stamina):
			player.stamina_changed.connect(update_stamina)
		update_health(player.current_health, player.max_health)
		update_stamina(player.current_stamina, player.max_stamina)

func update_health(current: float, maximum: float) -> void:
	if health_bar:
		health_bar.max_value = maximum
		health_bar.value = current
	if health_label:
		health_label.text = "HP %d / %d" % [int(current), int(maximum)]

func update_stamina(current: float, maximum: float) -> void:
	if stamina_bar:
		stamina_bar.max_value = maximum
		stamina_bar.value = current
	if stamina_label:
		stamina_label.text = "STAMINA %d / %d" % [int(current), int(maximum)]

func _update_debug_overlay() -> void:
	if not tracked_player:
		return
	var c := tracked_player.combat_controller
	var state_str: String = Player.State.keys()[tracked_player.current_state] if tracked_player.current_state < Player.State.size() else "UNKNOWN"
	var facing_str: String = Player.Facing.keys()[tracked_player.current_facing] if tracked_player.current_facing < Player.Facing.size() else "UNKNOWN"
	var dodge_cd: float = c.dodge_cooldown_timer if c else 0.0
	var heavy_cd: float = c.heavy_cooldown_timer if c else 0.0
	var iframes: bool = tracked_player.hurtbox.is_invulnerable if tracked_player.hurtbox else false
	var hitbox_active: bool = c.attack_hitbox.is_active if (c and c.attack_hitbox) else false

	debug_label.text = "[F3 DEBUG OVERLAY]\n" \
		+ "State: %s | Facing: %s\n" % [state_str, facing_str] \
		+ "HP: %.0f/%.0f | Stamina: %.0f/%.0f\n" % [tracked_player.current_health, tracked_player.max_health, tracked_player.current_stamina, tracked_player.max_stamina] \
		+ "Dodge CD: %.2fs | i-frames: %s\n" % [dodge_cd, str(iframes)] \
		+ "Heavy CD: %.2fs | Hitbox: %s" % [heavy_cd, "ACTIVE" if hitbox_active else "OFF"]
