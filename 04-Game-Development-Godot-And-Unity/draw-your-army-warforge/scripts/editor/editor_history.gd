class_name EditorHistory
extends RefCounted

var undo_stack: Array[EditorCommand] = []
var redo_stack: Array[EditorCommand] = []
var max_history: int = 50

func execute_command(command: EditorCommand) -> void:
	command.execute()
	undo_stack.append(command)
	redo_stack.clear()
	if undo_stack.size() > max_history:
		undo_stack.pop_front()

func undo() -> bool:
	if undo_stack.is_empty():
		return false
	var cmd = undo_stack.pop_back()
	cmd.undo()
	redo_stack.append(cmd)
	return true

func redo() -> bool:
	if redo_stack.is_empty():
		return false
	var cmd = redo_stack.pop_back()
	cmd.execute()
	undo_stack.append(cmd)
	return true

func can_undo() -> bool:
	return not undo_stack.is_empty()

func can_redo() -> bool:
	return not redo_stack.is_empty()

func clear() -> void:
	undo_stack.clear()
	redo_stack.clear()
