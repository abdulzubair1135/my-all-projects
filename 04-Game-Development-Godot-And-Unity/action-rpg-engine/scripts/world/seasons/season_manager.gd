class_name SeasonManager
extends Node

signal season_changed(new_season: Season)
signal year_changed(new_year: int)

enum Season {
	SPRING,
	SUMMER,
	AUTUMN,
	WINTER
}

@export var days_per_season: int = 30
var current_season: Season = Season.SPRING
var season_day: int = 1
var year: int = 1

func advance_day() -> void:
	season_day += 1
	if season_day > days_per_season:
		season_day = 1
		_advance_season()

func _advance_season() -> void:
	match current_season:
		Season.SPRING:
			current_season = Season.SUMMER
		Season.SUMMER:
			current_season = Season.AUTUMN
		Season.AUTUMN:
			current_season = Season.WINTER
		Season.WINTER:
			current_season = Season.SPRING
			year += 1
			year_changed.emit(year)

	season_changed.emit(current_season)

func set_season_state(p_season: int, p_season_day: int, p_year: int) -> void:
	current_season = int(clamp(p_season, 0, 3)) as Season
	season_day = int(clamp(p_season_day, 1, days_per_season))
	year = max(1, p_year)

func get_season_name() -> String:
	match current_season:
		Season.SPRING: return "Spring"
		Season.SUMMER: return "Summer"
		Season.AUTUMN: return "Autumn"
		Season.WINTER: return "Winter"
	return "Spring"

func get_season_tint() -> Color:
	match current_season:
		Season.SPRING: return Color(1.0, 1.03, 0.98, 1.0)
		Season.SUMMER: return Color(1.05, 1.02, 0.95, 1.0)
		Season.AUTUMN: return Color(1.05, 0.95, 0.88, 1.0)
		Season.WINTER: return Color(0.92, 0.96, 1.05, 1.0)
	return Color.WHITE