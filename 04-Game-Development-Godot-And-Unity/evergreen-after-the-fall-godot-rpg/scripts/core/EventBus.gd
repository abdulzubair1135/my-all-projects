extends Node

# Evergreen: After the Fall - EventBus Autoload
# Centralized decoupled communication for UI, World, Player, and Systems

# Player signals
signal protagonist_switched(new_protagonist: String)
signal health_changed(current: float, max_health: float)
signal stamina_changed(current: float, max_stamina: float)
signal hunger_changed(current: float, max_hunger: float)
signal thirst_changed(current: float, max_thirst: float)
signal player_died
signal player_action_performed(action_name: String)

# Interaction signals
signal interaction_available(interactable: Node)
signal interaction_cleared(interactable: Node)
signal player_interacted(interactable: Node)
signal dialog_started(npc_id: String, lines: Array)
signal dialog_ended

# Time & Environment signals
signal time_updated(hour: int, minute: int, day: int, season: String)
signal day_started(day_number: int)
signal night_started(night_number: int)
signal weather_changed(weather_type: String)

# System signals
signal inventory_updated
signal notification_requested(message: String, duration: float)
signal region_change_requested(region_id: String, spawn_id: String)
signal game_saved(slot: int)
signal game_loaded(slot: int)
signal quest_started(quest_id: String, quest_data: Dictionary)
signal quest_completed(quest_id: String, quest_data: Dictionary)
signal night_alert_started
