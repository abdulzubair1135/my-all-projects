extends CanvasLayer
class_name TouchControls

# Evergreen: After the Fall - Mobile & Android Touch Controls
# Provides on-screen virtual joystick and action buttons (Attack, Heavy, Dodge, Interact, Sprint)
# Synthesizes Godot InputEvents so existing player controllers work seamlessly on touch devices

@export var force_visible_for_testing: bool = false
@export var joystick_radius: float = 64.0
@export var deadzone: float = 0.15

var is_dragging_joystick: bool = false
var joystick_touch_index: int = -1
var joystick_center: Vector2 = Vector2.ZERO
var joystick_current_vector: Vector2 = Vector2.ZERO

@onready var joystick_base: Control = $JoystickContainer/JoystickBase
@onready var joystick_knob: Control = $JoystickContainer/JoystickBase/Knob
@onready var btn_attack: Button = $ActionsContainer/BtnAttack
@onready var btn_heavy: Button = $ActionsContainer/BtnHeavy
@onready var btn_dodge: Button = $ActionsContainer/BtnDodge
@onready var btn_interact: Button = $ActionsContainer/BtnInteract
@onready var btn_sprint: Button = $ActionsContainer/BtnSprint

func _ready() -> void:
	# Show touch controls on Android/iOS or when touchscreen is available or when forced
	var is_mobile = OS.get_name() in ["Android", "iOS"] or DisplayServer.is_touchscreen_available()
	visible = is_mobile or force_visible_for_testing
	
	if joystick_base:
		joystick_center = joystick_base.global_position + (joystick_base.size * 0.5)
	
	_connect_buttons()

func _connect_buttons() -> void:
	if btn_attack:
		btn_attack.button_down.connect(func(): _press_action("attack"))
		btn_attack.button_up.connect(func(): _release_action("attack"))
	if btn_heavy:
		btn_heavy.button_down.connect(func(): _press_action("heavy_attack"))
		btn_heavy.button_up.connect(func(): _release_action("heavy_attack"))
	if btn_dodge:
		btn_dodge.button_down.connect(func(): _press_action("dodge"))
		btn_dodge.button_up.connect(func(): _release_action("dodge"))
	if btn_interact:
		btn_interact.button_down.connect(func(): _press_action("interact"))
		btn_interact.button_up.connect(func(): _release_action("interact"))
	if btn_sprint:
		btn_sprint.button_down.connect(func(): _press_action("sprint"))
		btn_sprint.button_up.connect(func(): _release_action("sprint"))

func _input(event: InputEvent) -> void:
	if not visible:
		return
	
	if event is InputEventScreenTouch:
		if event.pressed:
			# Check if touch is inside joystick region (bottom-left 320x320 area)
			if event.position.x <= 320 and event.position.y >= 260 and not is_dragging_joystick:
				is_dragging_joystick = true
				joystick_touch_index = event.index
				_update_joystick(event.position)
		else:
			if event.index == joystick_touch_index:
				_reset_joystick()
				
	elif event is InputEventScreenDrag:
		if is_dragging_joystick and event.index == joystick_touch_index:
			_update_joystick(event.position)

func _update_joystick(touch_pos: Vector2) -> void:
	if joystick_base:
		joystick_center = joystick_base.global_position + (joystick_base.size * 0.5)
	
	var offset = touch_pos - joystick_center
	var dist = offset.length()
	
	if dist > joystick_radius:
		offset = offset.normalized() * joystick_radius
	
	if joystick_knob:
		joystick_knob.position = (joystick_base.size * 0.5) + offset - (joystick_knob.size * 0.5)
	
	var normalized_vec = offset / joystick_radius
	if normalized_vec.length() < deadzone:
		normalized_vec = Vector2.ZERO
	
	joystick_current_vector = normalized_vec
	_synthesize_movement_actions(normalized_vec)

func _synthesize_movement_actions(vec: Vector2) -> void:
	# Left / Right
	if vec.x < -0.3:
		_press_action("move_left")
		_release_action("move_right")
	elif vec.x > 0.3:
		_press_action("move_right")
		_release_action("move_left")
	else:
		_release_action("move_left")
		_release_action("move_right")
	
	# Up / Down
	if vec.y < -0.3:
		_press_action("move_up")
		_release_action("move_down")
	elif vec.y > 0.3:
		_press_action("move_down")
		_release_action("move_up")
	else:
		_release_action("move_up")
		_release_action("move_down")

func _reset_joystick() -> void:
	is_dragging_joystick = false
	joystick_touch_index = -1
	joystick_current_vector = Vector2.ZERO
	if joystick_knob and joystick_base:
		joystick_knob.position = (joystick_base.size * 0.5) - (joystick_knob.size * 0.5)
	
	_release_action("move_left")
	_release_action("move_right")
	_release_action("move_up")
	_release_action("move_down")

func _press_action(action: String) -> void:
	if not Input.is_action_pressed(action):
		Input.action_press(action)

func _release_action(action: String) -> void:
	if Input.is_action_pressed(action):
		Input.action_release(action)
