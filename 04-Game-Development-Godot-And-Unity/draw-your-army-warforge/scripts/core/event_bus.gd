class_name EventBusNode
extends Node

# UI and Navigation signals
@warning_ignore("unused_signal")
signal scene_change_requested(scene_path: String)
@warning_ignore("unused_signal")
signal notification_posted(message: String, type: String)

# Soldier Creator signals
@warning_ignore("unused_signal")
signal soldier_design_selected(soldier_id: String)
@warning_ignore("unused_signal")
signal soldier_design_saved(soldier_data: Dictionary)
@warning_ignore("unused_signal")
signal soldier_stats_updated(derived_stats: Dictionary)

# Army Workshop signals
@warning_ignore("unused_signal")
signal army_budget_changed(current_cost: int, max_budget: int)
@warning_ignore("unused_signal")
signal army_unit_count_changed(count: int, max_units: int)
@warning_ignore("unused_signal")
signal army_selection_changed(selected_units: Array)
@warning_ignore("unused_signal")
signal army_placement_committed(units_added: Array)
@warning_ignore("unused_signal")
signal army_undo_triggered()
@warning_ignore("unused_signal")
signal army_redo_triggered()

# Battle & Combat signals
@warning_ignore("unused_signal")
signal battle_started()
@warning_ignore("unused_signal")
signal battle_paused(is_paused: bool)
@warning_ignore("unused_signal")
signal battle_speed_changed(time_scale: float)
@warning_ignore("unused_signal")
signal battle_unit_killed(unit_id: String, team_id: int, killer_id: String)
@warning_ignore("unused_signal")
signal battle_finished(winner_team_id: int, summary: Dictionary)

# Networking signals
@warning_ignore("unused_signal")
signal match_state_changed(new_state: String)
@warning_ignore("unused_signal")
signal network_error_received(error_msg: String)
