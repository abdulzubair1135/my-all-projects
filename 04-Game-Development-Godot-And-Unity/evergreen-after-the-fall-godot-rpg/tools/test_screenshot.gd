extends Node

func _ready() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	var img = get_viewport().get_texture().get_image()
	print("Image size: ", img.get_size(), " format: ", img.get_format())
	var err = img.save_png("docs/visual_audit/before/test_capture.png")
	print("Save PNG result: ", err)
	get_tree().quit(0)
