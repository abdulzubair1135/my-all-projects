class_name DrawingToolbar
extends PanelContainer

signal tool_selected(tool_type: String)
signal clear_clicked()
signal undo_clicked()
signal redo_clicked()

const TOOLS = [
	{"id": "line", "label": "📏 Line"},
	{"id": "freehand", "label": "〰️ Curve"},
	{"id": "box", "label": "⏹️ Box"},
	{"id": "circle", "label": "⭕ Ring"},
	{"id": "wedge", "label": "📐 Wedge"}
]

var active_tool_id: String = "line"
var button_group: ButtonGroup = ButtonGroup.new()

func _ready() -> void:
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	add_child(vbox)
	
	var title = Label.new()
	title.text = "DRAW TOOLS"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_color_override("font_color", Color(0.95, 0.8, 0.3))
	title.add_theme_font_size_override("font_size", 16)
	vbox.add_child(title)
	
	var sep = HSeparator.new()
	vbox.add_child(sep)
	
	for t in TOOLS:
		var btn = Button.new()
		btn.text = t.label
		btn.custom_minimum_size = Vector2(0, 48)
		btn.toggle_mode = true
		btn.button_group = button_group
		btn.alignment = HORIZONTAL_ALIGNMENT_CENTER
		if t.id == active_tool_id:
			btn.button_pressed = true
		btn.pressed.connect(func(): _on_tool_pressed(t.id))
		vbox.add_child(btn)
		
	var sep2 = HSeparator.new()
	vbox.add_child(sep2)
	
	var undo_btn = Button.new()
	undo_btn.text = "↩️ Undo"
	undo_btn.custom_minimum_size = Vector2(0, 44)
	undo_btn.pressed.connect(func(): undo_clicked.emit())
	vbox.add_child(undo_btn)
	
	var redo_btn = Button.new()
	redo_btn.text = "↪️ Redo"
	redo_btn.custom_minimum_size = Vector2(0, 44)
	redo_btn.pressed.connect(func(): redo_clicked.emit())
	vbox.add_child(redo_btn)
	
	var clear_btn = Button.new()
	clear_btn.text = "🗑️ Clear"
	clear_btn.custom_minimum_size = Vector2(0, 44)
	clear_btn.pressed.connect(func(): clear_clicked.emit())
	vbox.add_child(clear_btn)

func _on_tool_pressed(tool_id: String) -> void:
	active_tool_id = tool_id
	tool_selected.emit(tool_id)
