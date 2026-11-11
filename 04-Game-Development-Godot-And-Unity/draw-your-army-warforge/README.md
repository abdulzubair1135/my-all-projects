# Draw Your Army: WarForge

## Overview
**Draw Your Army: WarForge** is a tactical strategy game built in **Godot Engine 4.6.2** combining:
1. **Soldier Creator**: Modular appearance customization, equipment catalogue, base archetypes, and calculated derived stats.
2. **Draw-to-Create Army Workshop**: Freehand and geometric formation drawing (lines, curves, boxes, rings, wedges) on a 3D battlefield with spatial placement validation, army budgets, and full undo/redo command history.
3. **Autonomous Combat Engine**: High-performance 3D battle simulation with spatial grid queries, state machines (idle, approach, attack, die), health, armor mitigation, and live battle HUD with statistics.
4. **Offline Practice Mode**: Instant battlefield engagement against AI armies with no external or network dependencies.
5. **Robust Local Persistence**: Versioned JSON schema serialization for soldier designs, army loadouts, and game settings.

---

## Directory Architecture
```
game 11/
├── assets/                  # 3D models, textures, materials, and UI icons
├── scenes/
│   ├── main_menu/           # Main menu scene and navigation
│   ├── soldier_creator/     # 3D turntable soldier customization studio
│   ├── army_workshop/       # Freehand draw-to-place battlefield editor
│   ├── battlefield/         # Autonomous combat battlefield and HUD
│   └── common/              # Reusable UI components
├── scripts/
│   ├── core/                # Autoloads: GameManager, EventBus, SettingsManager, DatabaseManager
│   ├── models/              # SoldierDesign, ArmyLoadout, EquipmentCatalog
│   ├── combat/              # Unit3D, UnitCombatData, CombatSimulationEngine, BattlefieldController
│   ├── editor/              # FormationMath, EditorCommand, EditorHistory, ArmyWorkshopController
│   ├── ui/                  # DrawingToolbar, MainMenuController, SoldierCreatorController
│   └── tests/               # Headless automated test runner & benchmarks
├── project.godot            # Godot 4.6 Engine configuration
├── REQUIREMENTS.md          # Traceable requirements register
└── README.md                # Project documentation
```

---

## How to Run

### 1. Launch Game
Launch the game using the installed Godot 4.6 executable:
```powershell
& "C:\Users\abdul\Godot\Godot_v4.6.2-stable_win64_console.exe" --path "c:\Users\abdul\OneDrive\ドキュメント\game 11"
```

### 2. Run Automated Test Suite
Run the 7-test headless verification suite:
```powershell
& "C:\Users\abdul\Godot\Godot_v4.6.2-stable_win64_console.exe" --headless --script res://scripts/tests/test_runner.gd
```
Expected output:
```
WARFORGE AUTOMATED TEST SUITE: MILESTONES 1 - 5
[TEST 1] Testing SoldierDesign Derived Stats & Cost Calculation... -> PASS
[TEST 2] Testing Soldier Serialization & Deserialization...       -> PASS
[TEST 3] Testing Formation Math Point Generation...               -> PASS
[TEST 4] Testing Army Budget & Collision Validation...            -> PASS
[TEST 5] Testing Undo / Redo Transactional History...             -> PASS
[TEST 6] Testing Combat Damage & Mitigation Formula...            -> PASS
[TEST 7] Testing 200-Unit Combat Engine & Spatial Indexing...     -> PASS (avg 1.00 ms/tick < 16.6ms budget)
TEST RESULTS SUMMARY: 7 PASSED, 0 FAILED
```
