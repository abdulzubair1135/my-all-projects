class_name ProgressionManager
extends Node

var player_level: int = 1
var player_xp: int = 0

var skills: Dictionary = {
	"combat": { "level": 1, "xp": 0 },
	"woodcutting": { "level": 1, "xp": 0 },
	"mining": { "level": 1, "xp": 0 },
	"farming": { "level": 1, "xp": 0 },
	"fishing": { "level": 1, "xp": 0 },
	"crafting": { "level": 1, "xp": 0 },
	"exploration": { "level": 1, "xp": 0 },
	"survival": { "level": 1, "xp": 0 }
}

static func get_xp_for_level(level: int) -> int:
	return int(100.0 * pow(float(level), 1.8))