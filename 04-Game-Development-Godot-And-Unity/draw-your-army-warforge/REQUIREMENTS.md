# DRAW YOUR ARMY: WARFORGE - REQUIREMENTS REGISTER

## Document Information
- **Title**: Draw Your Army: WarForge - Traceable Requirements Specification
- **Version**: 1.0.0
- **Engine**: Godot Engine 4.6.2 Stable (Windows x86_64)
- **Status**: Active / In Progress

---

## Priority Classification
- **P0**: Essential for core playable product (Soldier creation, drawing formations, autonomous combat, offline practice, persistence, core UI).
- **P1**: Required for first public release (Polished maps, full equipment catalog, complete UI/UX, audio/SFX, 2-client authoritative multiplayer loop).
- **P2**: Valuable post-launch features (Ranked rating, match history, server backend persistence, spectator mode).
- **P3**: Experimental / Long-term (Custom map editor, mobile Android builds, community workshop hub).

---

## Traceable Requirements Matrix

| Req ID | Category | Title & Summary | Priority | Dependencies | Status | Test Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-M1-01** | Core | Godot 4.6 Project Initialization & Directory Architecture | P0 | None | Completed | Project parses and loads in headless Godot |
| **REQ-M1-02** | Core | Centralized Game Configuration & Branding Singleton | P0 | REQ-M1-01 | In Progress | Config loads, title matches, settings defaults exist |
| **REQ-M1-03** | Core | Scene Navigation & Event Bus System | P0 | REQ-M1-01 | In Progress | Seamless transitions between Menu, Workshop, Practice |
| **REQ-M2-01** | Combat | Unit Data Models (Archetypes, Stats, Formulas) | P0 | REQ-M1-01 | Pending | Unit stat derivation and cost calculation unit tests |
| **REQ-M2-02** | Combat | Autonomous 3D Unit State Machine (Idle, Move, Attack, Die) | P0 | REQ-M2-01 | Pending | Headless combat engine simulation test |
| **REQ-M2-03** | Combat | Combat Calculations & Projectiles (Melee, Ranged, Armor) | P0 | REQ-M2-02 | Pending | Damage mitigation and range calculation tests |
| **REQ-M3-01** | Creator | Modular Soldier 3D Appearance Customizer | P0 | REQ-M2-01 | Pending | Visual modular pieces attach correctly |
| **REQ-M3-02** | Creator | Equipment Catalogue & Cost Calculation | P0 | REQ-M2-01 | Pending | Stat modifiers apply and calculate total cost |
| **REQ-M3-03** | Persistence | Soldier Design Local Save/Load (JSON/Resource) | P0 | REQ-M3-01 | Pending | Serialization round-trip and validation tests |
| **REQ-M4-01** | Editor | 3D Raycast Battlefield Pointer & Surface Projection | P0 | REQ-M1-01 | Pending | Screen-to-plane projection tests |
| **REQ-M4-02** | Editor | Freehand Curve & Shape Drawing Pipeline (Lines, Circles, Boxes) | P0 | REQ-M4-01 | Pending | Path sampling, spacing, and candidate point generation tests |
| **REQ-M4-03** | Editor | Spatial Placement Validation (Budget, Collision, Bounds) | P0 | REQ-M4-02 | Pending | Over-budget and overlapping placement rejection tests |
| **REQ-M4-04** | Editor | Undo / Redo Command History Architecture | P0 | REQ-M4-02 | Pending | Push, Undo, Redo state integrity tests |
| **REQ-M4-05** | Persistence | Army Loadout Serialization & Blueprint Presets | P0 | REQ-M4-03 | Pending | Army loadout save/load/validate tests |
| **REQ-M5-01** | GameMode | Offline Practice Battlefield Environment | P0 | REQ-M2-02, REQ-M4-05 | Pending | Battlefield loads with deployment zones |
| **REQ-M5-02** | GameMode | Autonomous Army Battle Simulation Loop & AI Opponent | P0 | REQ-M5-01 | Pending | 100+ units battle autonomously without stalling |
| **REQ-M5-03** | GameMode | Battle Victory Conditions, HUD, and Results Screen | P0 | REQ-M5-02 | Pending | Accurate kill, loss, duration, and survivor tracking |
| **REQ-M6-01** | UI/UX | High-Quality Slate & Metallic Design System Components | P1 | REQ-M1-02 | Pending | Button states, modal dialogs, cards, tooltips |
| **REQ-M6-02** | UI/UX | Settings System (Audio, Video, Display, Controls) | P1 | REQ-M1-02 | Pending | Settings persist to disk and apply immediately |
| **REQ-M6-03** | UI/UX | Progressive Interactive Tutorial | P1 | REQ-M3, REQ-M4, REQ-M5 | Pending | Step-by-step guidance tracking |
| **REQ-M7-01** | Performance | MultiMesh / Batched Rendering & AI Staggered Updates | P1 | REQ-M5-02 | Pending | 200+ units benchmark profiling >= 60 FPS |
| **REQ-M8-01** | Multiplayer | Dedicated Authoritative Server Match Simulation Loop | P1 | REQ-M5-02 | Pending | Headless server runs authoritative match ticks |
| **REQ-M8-02** | Multiplayer | 2-Client Network Protocol (Snapshot Replication, Orders) | P1 | REQ-M8-01 | Pending | Two clients connect, deploy armies, receive snapshots |
| **REQ-M9-01** | Backend | REST API Server for Authentication, Profiles, Armies | P2 | REQ-M8-02 | Pending | Node/TypeScript or Python FastAPI test suite |
| **REQ-M10-01**| Security | Server-Side Army Validation & Anti-Tamper Checks | P1 | REQ-M8-01 | Pending | Rejects over-budget or hacked stat packets |
