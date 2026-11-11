class_name DatabaseManagerNode
extends Node

const USER_DATA_PATH = "user://saves/"
const SOLDIERS_DIR = "user://saves/soldiers/"
const ARMIES_DIR = "user://saves/armies/"
const FORMATIONS_DIR = "user://saves/formations/"

func _ready() -> void:
	_ensure_directories()

func _ensure_directories() -> void:
	for path in [USER_DATA_PATH, SOLDIERS_DIR, ARMIES_DIR, FORMATIONS_DIR]:
		if not DirAccess.dir_exists_absolute(path):
			DirAccess.make_dir_recursive_absolute(path)

func save_json_file(relative_path: String, data: Dictionary) -> bool:
	var full_path = USER_DATA_PATH + relative_path
	var dir = full_path.get_base_dir()
	if not DirAccess.dir_exists_absolute(dir):
		DirAccess.make_dir_recursive_absolute(dir)
	
	var file = FileAccess.open(full_path, FileAccess.WRITE)
	if not file:
		push_error("Failed to open file for writing: " + full_path)
		return false
	
	var json_string = JSON.stringify(data, "\t")
	file.store_string(json_string)
	file.close()
	return true

func load_json_file(relative_path: String) -> Dictionary:
	var full_path = USER_DATA_PATH + relative_path
	if not FileAccess.file_exists(full_path):
		return {}
	
	var file = FileAccess.open(full_path, FileAccess.READ)
	if not file:
		push_error("Failed to open file for reading: " + full_path)
		return {}
	
	var content = file.get_as_text()
	file.close()
	
	var json = JSON.new()
	var error = json.parse(content)
	if error != OK:
		push_error("JSON Parse Error in " + full_path + ": " + json.get_error_message())
		return {}
	
	if typeof(json.data) == TYPE_DICTIONARY:
		return json.data
	return {}

func list_files_in_dir(relative_dir: String, extension: String = ".json") -> Array[String]:
	var full_path = USER_DATA_PATH + relative_dir
	var result: Array[String] = []
	if not DirAccess.dir_exists_absolute(full_path):
		return result
	
	var dir = DirAccess.open(full_path)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if not dir.current_is_dir() and file_name.ends_with(extension):
				result.append(file_name)
			file_name = dir.get_next()
		dir.list_dir_end()
	return result

func delete_file(relative_path: String) -> bool:
	var full_path = USER_DATA_PATH + relative_path
	if FileAccess.file_exists(full_path):
		var err = DirAccess.remove_absolute(full_path)
		return err == OK
	return false
