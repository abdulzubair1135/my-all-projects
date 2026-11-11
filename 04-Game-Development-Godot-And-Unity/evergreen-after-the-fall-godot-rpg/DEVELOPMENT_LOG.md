# DEVELOPMENT LOG - EVERGREEN: AFTER THE FALL

## Production Log

### 2026-11-11 - Project Inception & Technical Audit
- **Engine Audit**: Godot v4.6.2-stable.official.71f334935 verified on Windows 64-bit (`C:\Users\abdul\Godot\Godot_v4.6.2-stable_win64_console.exe`).
- **GDD Ingestion**: Ingested full Game Design Document detailing 15 regions, 120 quests, 15 zombie archetypes, 25 crops, animals, crafting, NPC schedules, romance system, and save architecture.
- **Environment Setup**: Initialized project repository at `c:\Users\abdul\OneDrive\Documents\rpgm games`.
- **Roadmap**: Created Milestone-driven development tracking in `TASKS.md`.
- **Milestone 1 Kickoff**: Designing Godot 4.6 project configuration with pixel-perfect 2D rendering, custom InputMap, player controller for Archi & Danish, farm prototype environment, camera bounds, interactables, and main menu with character selection.

### 2026-11-11 - Milestone 1: Foundation & First Playable Slice Complete
- **Pixel Art Generation**: Generated authentic pixel-art assets via `tools/generate_pixel_assets.py`:
  - 32x32 tileset (`farm_tiles.png`): grass, wildflowers, tilled soil, watered soil, cobble paths, wood planks, stone walls, water, wooden fences.
  - 32x48 character spritesheets: Archi (`archi_spritesheet.png`) and Danish (`danish_spritesheet.png`) with 4-direction idle and 4-frame walk animations.
  - 64x64 detailed pixel portraits for Archi and Danish.
  - Farm props (`farm_props.png`): Farmhouse with warm glowing windows, stone water well, storage chest, pine trees.
  - UI sheet (`ui_elements.png` and `icon.png`): Hearts, stamina bolts, sun/clock, interact key prompt bubble, quickslot frames, tool icons.
- **Core Architecture & Singletons**:
  - `EventBus.gd`: Decoupled signals for player state, stats, interactions, clock, and dialogue.
  - `GameState.gd`: Full stats tracking for Archi and Danish, in-game calendar, stamina consumption/recovery, safe-zone switching.
- **Player Controller**:
  - `Player.tscn` + `player_controller.gd`: 8-direction smooth movement, sprint stamina drain, dodge roll with invulnerability window, foot-aligned collision, dynamic sprite & portrait swapping, interaction detector with floating prompt.
- **Interactables & World**:
  - `Interactable.gd`: Universal interaction handling for doors, wells, chests, signposts, and companions.
  - `EvergreenFarm.tscn` + `farm_environment.gd` + `evergreen_farm.gd`: Full 30x20 tile farm hub, farmhouse, well, chest, signpost, perimeter fencing/trees, companion placement, camera boundary limits.
- **UI & Menus**:
  - `MainMenu.tscn` + `main_menu.gd`: Complete menu with New Game modal (Difficulty, Farm Name, Character Cards for Archi & Danish with stats/perks), Settings modal, Credits modal, Scene transition to farm.
  - `HUD.tscn` + `hud_controller.gd`: Dynamic portrait, health/stamina bars, clock/season panel, 5-slot quickbar, notification banner, multi-line dialogue box with speaker formatting.
- **Automated Verification**:
  - Created `tests/test_runner.gd` and `tests/test_main_menu.gd`.
  - Executed tests under Godot 4.6.2 engine. Verified 100% pass on movement, collision, sprint, stamina, dodge roll, well interaction, safe-zone character switching, companion sync, and main menu flow.

### 2026-11-11 - Milestone 2: Farming & Economy Vertical Slice Complete
- **Crop Spritesheet Generation**: Authored 32x32 pixel sprites in `assets/props/crops.png` for Turnips, Carrots, and Potatoes across Sprout, Growing, Mature, and Produce item icons.
- **Inventory System (`inventory_service.gd`)**:
  - 12 player slots with 5-slot quickbar support.
  - Full item registry: tools (Hoe, Can, Machete), seeds (Turnip, Carrot, Potato), produce, materials (Wood, Stone), and bread.
  - Multi-stacking logic up to 99 items, active slot selection (1-5, Q), consumption, and farm chest container storage.
- **Crop Lifecycle & Central Farm Simulation**:
  - `CropPlot.tscn` + `crop_plot.gd`: Interactive 32x32 plot supporting tilling, watering, seed planting, and harvesting.
  - `farm_manager.gd`: Coordinates global daily crop updates across all registered plots when `EventBus.day_started` emits.
  - Archi's "Green Thumb" signature perk implemented: yields 2x produce on harvest.
- **Atmospheric Day/Night Cycle & Sleep**:
  - CanvasModulate system dynamically blends from Night blue (`0.28, 0.32, 0.48`) to Dawn peach (`0.95, 0.85, 0.72`) to bright daylight (`1.0, 1.0, 1.0`) to Dusk amber (`0.88, 0.62, 0.52`).
  - Farmhouse sleep interaction restores full HP & Stamina, advances clock to 06:00 AM next day, triggers crop growth, and autosaves.
- **Save & Load Architecture (`SaveService.gd`)**:
  - Versioned schema with multi-slot support and automatic `.bak` backup generation.
  - Complete persistence for protagonist, player position, stats, inventory, chest storage, calendar time, and all farm plot states.
- **Automated Testing**:
  - Built `tests/test_milestone2.gd` and `tests/TestMilestone2.tscn`.
  - Validated inventory stacking, tool interactions, day advance, crop maturity, harvest perk bonuses, and round-trip save/load restoration with 100% pass.

### 2026-11-11 - Milestone 3: Combat, Survival & Night Defense Complete
- **Infected Spritesheet Generation**: Authored 32x48 pixel sprites in `assets/characters/infected/` for both Drifter (`drifter_spritesheet.png`) and Sprinter (`sprinter_spritesheet.png`) across 4-direction Idle, Walk, Attack, and Hurt/Dead states.
- **Combat Hitbox & Hurtbox Pipeline**:
  - `Hitbox.gd` (Area2D layer 4/16): Deals directional damage, knockback impulse, and immediate overlap detection.
  - `Hurtbox.gd` (Area2D layer 8/16): Invulnerability frames, hit signals, and damage dispatch.
- **Player Real-Time Melee Attacks**:
  - Light Attack (J / Left Click): 8 stamina cost, fast directional slash.
  - Heavy Attack (K / Right Click): 18 stamina cost, heavy stagger, strong knockback.
  - Character Perks: Danish deals +25% melee damage (60.0 on heavy strike), Archi has 30% faster frame recovery.
  - Player Hurtbox: Takes damage from infected lunges, flashes red, updates health in GameState and HUD.
- **Infected AI Architecture (`InfectedBase.tscn`)**:
  - FSM: `IDLE` -> `PATROL` -> `CHASE` -> `ATTACK` -> `RECOVER` -> `HURT` -> `DEAD`.
  - Hearing Perception: Detects running player (sprint) within 220–300 px radius.
  - Vision Perception: Line-of-sight distance checks.
  - Archetypes: Drifter (65 HP, 52 Speed, 16 Dmg), Sprinter (45 HP, 135 Speed, 22 Dmg).
  - Death & Salvage: Drops materials/seeds on death (`mat_wood`, `seed_potato`).
- **Night Defense & Horde Director (`NightDefenseDirector.gd`)**:
  - Coordinates perimeter alerts when night falls at 20:00.
  - Spawns multi-archetype infected waves near farm borders.
  - Rewards player upon clearing the horde.
- **Automated Testing**:
  - Created `tests/test_milestone3.gd` and `tests/TestMilestone3.tscn`.
  - Full automated validation: melee strike damage, Danish perk boost, sprint hearing alert, infected attack damage to player, horde wave spawn & completion. Passed 100%.

### 2026-11-11 - Milestone 4: Life Simulation & NPCs Complete
- **Animal & NPC Pixel Art Generation**:
  - Authored 32x32 Chicken spritesheet (`chicken.png`) with peck and walk cycles.
  - Authored 48x32 Cow spritesheet (`cow.png`) with graze and walk cycles.
  - Authored 64x64 detailed pixel portraits for Thomas, Dr. Elena, and Marcus in `assets/characters/npcs/`.
- **Farm Animal Life Simulation (`farm_animal.gd`)**:
  - Chicken ("Clucky"): produces daily farm fresh eggs (`produce_egg`), accepts seeds for feeding, gains affection on petting.
  - Cow ("Bessie"): produces fresh milk bottles (`produce_milk`), accepts crops/bread.
  - Autonomous pasture wandering around home coordinates.
- **Named NPC Social & Schedule Architecture (`npc_base.gd`)**:
  - Thomas (N01): hourly routine from morning garden inspection (08:00 at 260, 290) to afternoon workshop (14:00 at 210, 160) to farmhouse rest.
  - Gift Giving: Loved gifts (Thomas: Turnips/Potatoes; Elena: Bandages/Carrots; Marcus: Wood/Stone) award +15 trust/friendship; neutral items award +6.
- **Crafting & Construction System (`crafting_service.gd`)**:
  - Blueprints: Wooden Barricade, Spike Trap, Sterile Bandage, Fresh Bread.
  - Danish's "Field Engineer" perk: automatically grants a resource discount on defense structures (costs 4 wood instead of 5).
  - Expanded inventory capacity to 24 slots (`MAX_PLAYER_SLOTS = 24`) for tools, materials, and produce.
- **Automated Testing**:
  - Created `tests/test_milestone4.gd` and `tests/TestMilestone4.tscn`.
  - 100% pass across all 5 test suites (M1, M2, M3, M4, and Main Menu).

### 2026-11-11 - Milestones 5 & 6: Relationships & World Region Streaming Complete
- **Relationship & Romance System (`relationship_service.gd`)**:
  - Multi-dimensional metrics: Trust, Closeness, Respect, and Shared Memories array.
  - Milestones: "Shared Truth" (Trust 50), "Tea on the Porch" (Closeness 50), "Unbreakable Bond" (Trust 80 / Respect 75).
  - Shared Meals: Cabin supper consumes bread/turnips, heals both protagonists for +25 HP, increases Trust & Closeness, and logs a persistent memory.
  - Companion Gifts: Archi favors medicinal items and seeds; Danish favors building lumber, stone, and defensive barricades.
  - Passive Support Perks: +15% stamina regen bonus and +10% damage resistance when relationship thresholds are achieved.
- **WorldManager & Region Streaming Architecture (`world_manager.gd`)**:
  - Scene streaming between regions with persistent state handoffs and camera limits.
  - Spawn Point markers (`SpawnPoint_default`, `SpawnPoint_north_gate`, `SpawnPoint_east_trail`).
  - Region 1: Evergreen Farm (`EvergreenFarm.tscn`) - player homestead.
  - Region 2: Evergreen Village (`EvergreenVillage.tscn`) - community settlement with Lily's Store, Marcus's Smithy, and Notice Board.
  - Region 3: Greenwood Forest (`GreenwoodForest.tscn`) - wilderness danger zone with filtered canopy lighting, Oliver's Ranger Station, and roaming Drifter infected.
  - Region 4: Crystal Lake (`CrystalLake.tscn`) - lakeside retreat with fishing pier and Fisherman Noah.
- **Region Transition Component (`RegionExit.tscn` + `region_exit.gd`)**:
  - Area2D trigger that connects road exits to destination regions and places the player at appropriate spawn markers.
- **Automated Verification**:
  - Created `tests/test_milestones_5_6.gd` and `tests/TestMilestones5_6.tscn`.
  - Executed full project test suite (Milestones 1 through 6) with 100% pass on all 6 suites.

### 2026-11-11 - Milestone 7: Quest System, Story Acts, Boss Combat & Multi-Endings Complete
- **Quest & Campaign Architecture (`quest_service.gd`)**:
  - Multi-stage quest objectives across Acts I–V, covering Main Story, Farming, and Relationship categories.
  - Reward idempotency guarantees quest rewards are never duplicated.
  - Story act transition automation: completing "First Night" (ms04) transitions campaign to Act II — The Valley Remembers.
  - Integrated into `SaveService.gd` atomic save/load routines.
- **Boss Fight Architecture (`boss_base.gd` + `BossWarden.tscn`)**:
  - Multi-phase boss battle ("The Warden"): 250 HP pool with 25% poise damage reduction.
  - Phase 1: Heavy cleaver strikes and chase behaviors.
  - Phase 2: Enraged threshold at <= 125 HP with increased speed and crimson aura.
  - Telegraphed AoE Ground Slam: 0.75s flashing red warning followed by a 64px radius shockwave strike.
  - Drops guaranteed `quest_item_research_key` ("E.V.E.R. Research Keycard") and updates narrative flags.
- **Branching Endings Evaluator**:
  - Evaluates all 6 GDD endings: The Green Dawn (True Cure), Home Is Us (Relationship), Beyond the Valley (Evacuation), The Last Light (Survival), Evergreen Reborn (Settlement), and The Hidden Record (Bunker secret).
- **Automated Verification**:
  - Created `tests/test_milestone7.gd` and `tests/TestMilestone7.tscn`.
  - 100% pass.

### 2026-11-11 - Milestone 8: Audio Synthesis, Touch Controls, Settings & Android Prep Complete
- **Audio Service (`audio_service.gd`)**:
  - Zero-dependency procedural 16-bit sound generator creating audio waveforms in memory:
    - `ui_click`, `attack_swing`, `hit_impact`, `harvest`, `morning_chime`, `quest_fanfare`, `night_warning`, `zombie_growl`.
  - Audio mixing with Master, Music, and SFX volume controls.
  - Decoupled signal hooks connecting to EventBus (quest completed, day started, night alerts).
- **Settings & Accessibility Architecture (`GameState.gd`)**:
  - ConfigFile disk persistence (`user://settings.cfg`) for screen shake, damage numbers, touch control mode, colorblind palettes, text scale, and audio volumes.
- **Mobile / Android Touch Controls (`touch_controls.gd` + `TouchControls.tscn`)**:
  - Virtual floating joystick with deadzone and drag clamp.
  - Action buttons: Attack (J), Heavy Attack (K), Dodge (Space), Interact (E), Sprint (Shift).
  - Feeds into Godot's Input server via `Input.action_press()` and `Input.action_release()` for seamless controller parity.
- **Android / Google Play Packaging Preparation**:
  - Created `export_presets.cfg` configured for Windows Desktop and Android (`com.evergreen.afterthefall`, ARM64, target SDK 34).
- **Full Regression Verification**:
  - Executed all 8 test suites in headless Godot: MainMenu, Milestone 2, Milestone 3, Milestone 4, Milestones 5 & 6, Milestone 7, and Milestone 8.
  - 100% pass across all systems.
