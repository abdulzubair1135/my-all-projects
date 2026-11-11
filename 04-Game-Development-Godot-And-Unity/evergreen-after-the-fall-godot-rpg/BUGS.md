# KNOWN ISSUES & BUG TRACKER

| Bug ID | Severity | System | Description | Status | Resolution |
|---|---|---|---|---|---|
| BUG-001 | Low | Scene Parse | Duplicate `/VBox` in parent node path of DanishCard in `MainMenu.tscn` | Closed | Corrected parent hierarchy path in scene definition. |
| BUG-002 | Medium | Script Typing | Dynamic assignment to `interactable_id` on base `Area2D` in `farm_environment.gd` | Closed | Instantiated via `preload("...").new()` directly to ensure static type compatibility. |
| BUG-003 | Low | Main Menu | Scene change during tree setup warned about busy parent node | Closed | Switched scene change invocation to `get_tree().change_scene_to_file.call_deferred(...)`. |
| BUG-004 | Medium | EventBus | Missing `signal inventory_updated` in `EventBus.gd` causing inventory UI update crash | Closed | Declared `signal inventory_updated` in EventBus and connected to HUD. |
| BUG-005 | Medium | Persistence | JSON float representation for integers during inventory and plot deserialization | Closed | Explicitly cast numerical counts and stage indices using `int()` during deserialization. |
| BUG-006 | Medium | Combat | Hitbox not re-triggering damage on already-overlapping hurtboxes between consecutive swings | Closed | Added `check_overlaps()` query on attack activation to immediately hit overlapping hurtboxes. |
| BUG-007 | Low | Relationships | Type mismatch assigning deserialized JSON Array to typed `Array[Dictionary]` for memories | Closed | Populated typed array by iterating and checking each element. |
| BUG-008 | Low | EventBus | Missing `quest_completed` and `night_alert_started` signals on EventBus | Closed | Added signals to `EventBus.gd` and emitted from `quest_service.gd`. |
| BUG-009 | Low | Combat / Hurtbox | Method name discrepancy (`take_hit` vs `receive_hit`) in Hurtbox | Closed | Added `take_hit()` wrapper alias in `hurtbox.gd` forwarding directly to `receive_hit()`. |
| BUG-010 | High | Player / EventBus | Missing `signal player_interacted` on EventBus causing crash on 'E' keypress | Closed | Added `signal player_interacted(interactable: Node)` to `EventBus.gd`. |
| BUG-011 | High | Windows Launcher | Trailing backslash quote escaping in `.bat` script causing silent launch failure | Closed | Refactored batch scripts to use explicit clean paths and `start "" ... "res://scenes/main_menu/MainMenu.tscn"`. |
| BUG-012 | Low | Project Config | Duplicate UID warnings and nested starter project warning in `rpg/` | Closed | Removed unused `rpg/` folder and placed `.gdignore` in `assets/source/`, `assets/optimized/`, and `docs/`. |
