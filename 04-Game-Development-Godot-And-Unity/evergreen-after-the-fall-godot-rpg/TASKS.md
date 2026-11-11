# EVERGREEN: AFTER THE FALL - Development Tasks & Milestone Tracker

## Milestone Overview & Status

- [x] **Pre-Production & Environment Audit**
  - [x] Godot version verified: Godot 4.6.2-stable.official (Win64)
  - [x] Workspace inspected and verified
  - [x] Documentation & architecture blueprint established (TASKS.md, DEVELOPMENT_LOG.md, ASSET_LICENSES.md, BUGS.md)
  - [x] GDD analyzed in detail

- [x] **Milestone 1: Foundation & First Playable Slice**
  - [x] Initialize `project.godot` with 2D pixel-art settings (nearest-neighbor filtering, 32x32 grid, 960x540 viewport scaling 2D canvas_items).
  - [x] Set up project folder structure (`res://scenes/`, `res://scripts/`, `res://assets/`, `res://data/`).
  - [x] Configure InputMap actions (WASD/arrows, sprint, attack, heavy attack, dodge, interact, inventory, map, quick_slot, switch_protagonist, pause).
  - [x] Generate pixel-perfect sprite sheets / textures for Archi (female lead, agile, green/apron palette) and Danish (male lead, sturdy, engineer/scavenger palette) with 4-direction idle & walk cycles.
  - [x] Build player controller (`Player.tscn` + `player_controller.gd`) supporting:
    - 8-direction smooth movement
    - Sprint (with stamina consumption and regen)
    - Dodge roll mechanic
    - Collision shape (foot-aligned box)
    - Character switching between Archi & Danish
    - Camera2D with smoothing and bounds
    - InteractionArea (Area2D for detecting nearby interactables)
  - [x] Build interactable framework (`Interactable.tscn`, `interactable.gd`) with popup prompts (E key indicator) and feedback.
  - [x] Build Evergreen Farm prototype map (`EvergreenFarm.tscn`) with 32x32 tiles (soil, grass, path, fences, farmhouse, well, storage chest).
  - [x] Build Main Menu (`MainMenu.tscn`) with:
    - New Game (Difficulty, Protagonist Selection Archi/Danish, Farm Name)
    - Continue / Load Game
    - Settings (Audio / Controls)
    - Exit
  - [x] Build In-Game HUD overlay (`HUD.tscn`):
    - Protagonist portrait & name
    - Health & stamina bars
    - Clock / Day indicator
    - Quick slot bar
    - Interaction hint banner
  - [x] Run Godot engine verification, headless/windowed test, debug any script or scene errors, and verify 60 FPS gameplay.

- [x] **Milestone 2: Farming & Economy Vertical Slice**
  - [x] Central farm manager (`farm_manager.gd`): Coordinates daily crop growth without per-crop timers.
  - [x] Soil tilling, seed planting, watering can, growth stages: `crop_plot.gd` + `CropPlot.tscn` supporting Dry, Watered, Seedling, Growing, Mature states.
  - [x] Crops: Turnip, Carrot, Potato (and seasonal rules) with custom pixel art in `crops.png`.
  - [x] Harvest and inventory storage: `inventory_service.gd` with 12 player slots, quickbar [1..5], stacking, consuming, and farm chest storage.
  - [x] Day/night atmospheric lighting: `CanvasModulate` with dynamic Dawn, Day, Dusk, and Night transitions; Farmhouse sleep cycle advancing clock to 06:00 AM, restoring stamina/HP, and triggering crop growth.
  - [x] SaveService version 1.0 (`SaveService.gd`): Atomic multi-slot save/load with JSON serialization, rotating `.bak` backups, and complete restoration of player position, protagonist, stats, calendar, inventory, and farm plots.
  - [x] Automated test suite `tests/TestMilestone2.tscn` passing 100%.

- [x] **Milestone 3: Combat, Survival & Night Defense**
  - [x] Real-time top-down melee combat: Hitbox & Hurtbox components, directional attacks (J: Light attack, K: Heavy attack), stamina cost, knockback, screen flash feedback.
  - [x] Character combat perks: Danish (+25% heavy weapon damage & stagger), Archi (agile recovery speed).
  - [x] Zombie AI architecture (`InfectedBase.tscn`): Finite State Machine (Idle, Patrol, Chase, Attack, Hurt, Dead), hearing perception (reacts to sprint sound), vision range, dynamic lunge attack hitbox, and salvage loot drops.
  - [x] Zombie Archetypes: Drifter (resilient shambler) and Sprinter (fast agile ambusher) with custom pixel-art spritesheets in `assets/characters/infected/`.
  - [x] Night alert system and horde defense: `NightDefenseDirector` triggers perimeter alert at dusk/night, spawns attacking horde waves, tracks remaining infected, and awards survival XP upon clearing.
  - [x] Automated test suite `tests/TestMilestone3.tscn` passing 100%.

- [x] **Milestone 4: Life Simulation & NPCs**
  - [x] NPC schedule & dialogue engine: `npc_base.gd` + `NPC.tscn` supporting hourly schedules (06:00 to 24:00), waypoint navigation, multi-line dialogue, and gift giving.
  - [x] First named NPCs: Thomas (N01 - Farmer mentor), Elena (N02 - Physician), Marcus (N03 - Blacksmith) with custom 64x64 pixel portraits and gift preferences.
  - [x] Farm Animals: `farm_animal.gd` + `FarmAnimal.tscn` for Chicken ("Clucky" -> fresh eggs) and Cow ("Bessie" -> fresh milk), daily feeding loop, and affection progression with custom pixel-art spritesheets.
  - [x] Workbench & Crafting system: `crafting_service.gd` supporting blueprints for Wooden Barricades, Spike Traps, Sterile Bandages, and Bread; includes Danish's "Field Engineer" -1 resource discount perk.
  - [x] Automated test suite `tests/TestMilestone4.tscn` passing 100%.

- [x] **Milestone 5: Relationship & Protagonist Arc**
  - [x] Relationship manager (`relationship_service.gd`): Multi-dimensional tracking (Trust, Closeness, Respect, Shared Memories).
  - [x] Milestone progression: "Shared Truth" (Trust 50), "Tea on the Porch" (Closeness 50), "Unbreakable Bond" (Trust 80 / Respect 75).
  - [x] Archi & Danish companion interactions: shared meals in cabin (heals both protagonists, records memories), gift exchanges (tailored preferences), and emotional camp dialogue.
  - [x] Companion passive support perks: +15% stamina regen bonus and +10% damage resistance when relationship is strong.

- [x] **Milestone 6: World Regions & Streaming**
  - [x] Centralized WorldManager service (`world_manager.gd`): Handles scene streaming, named spawn point handoffs, camera boundaries, and persistent discovered map registry.
  - [x] Region 1: Evergreen Farm (`EvergreenFarm.tscn`) with North road and East trail transition gates.
  - [x] Region 2: Evergreen Village (`EvergreenVillage.tscn`) safe community settlement, Lily's General Store, Marcus's Smithy, and town notice board.
  - [x] Region 3: Greenwood Forest (`GreenwoodForest.tscn`) danger zone with canopy lighting, Oliver's Ranger Station, and roaming infected Drifters.
  - [x] Region 4: Crystal Lake (`CrystalLake.tscn`) peaceful fishing pier with Fisherman Noah and fresh water pump.
  - [x] Automated test suite `tests/TestMilestones5_6.tscn` passing 100%.

- [x] **Milestone 7: Quests, Bosses & Story Acts**
  - [x] Quest & Story Campaign service (`quest_service.gd`): Multi-stage objectives, category tracking (Main Story, Farming, Relationship), reward idempotency, and story act transitions (Acts I through V).
  - [x] Boss encounter architecture (`boss_base.gd` + `BossWarden.tscn`): Multi-phase boss battle ("The Warden") featuring Phase 1 cleaver swings, Phase 2 enraged threshold (<50% HP), telegraphed AoE ground slam shockwave, guaranteed E.V.E.R. Research Keycard drop, and story flag updates.
  - [x] Narrative branching: Evaluator supporting all 6 GDD endings (Ending A: The Green Dawn, Ending B: Home Is Us, Ending C: Beyond the Valley, Ending D: The Last Light, Ending E: Evergreen Reborn, Ending F: The Hidden Record).
  - [x] Automated test suite `tests/TestMilestone7.tscn` passing 100%.

- [x] **Milestone 8: Audio, Accessibility, Android Release Prep & Polish**
  - [x] Audio service (`audio_service.gd`): Procedural 16-bit sound synthesizer with zero external dependencies (UI blip, weapon swing, impact crunch, harvest chime, morning chime, quest fanfare, night warning, zombie growl) and Master/Music/SFX volume mixing.
  - [x] Settings & Accessibility: ConfigFile persistence (`user://settings.cfg`) for screen shake toggle, damage numbers, colorblind modes, text scaling, and volume levels.
  - [x] Mobile & Android Touch Controls: CanvasLayer virtual overlay (`TouchControls.tscn` + `touch_controls.gd`) with responsive analog joystick and action buttons (Attack, Heavy, Dodge, Interact, Sprint) synthesizing Godot InputEvents.
  - [x] Android Release Preparation: `export_presets.cfg` template for Windows Desktop and Android Google Play (`com.evergreen.afterthefall`, ARM64, target SDK 34).
  - [x] Automated test suite `tests/TestMilestone8.tscn` passing 100%.
  - [x] Complete project regression sweep verified across all 8 milestones.
