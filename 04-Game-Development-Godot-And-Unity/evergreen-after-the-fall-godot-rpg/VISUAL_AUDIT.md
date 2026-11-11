# VISUAL AUDIT & ART PRODUCTION SPECIFICATION
**Project**: Evergreen: After the Fall  
**Version**: 1.0 (Visual Overhaul Baseline)  
**Date**: November 11, 2026  
**Auditor**: Lead Art Director & Production Orchestrator  

---

## 1. Executive Summary

A comprehensive visual and technical audit of all 20 game systems and scenes was completed using actual engine captures on the target hardware (NVIDIA GeForce RTX 2050 / Godot 4.6.2 Forward+). 

While the underlying gameplay architecture (Farming, Combat, AI, Schedules, World Streaming, Save Persistence, Dialog, Audio) is robust and passes all automated tests at 100%, the visual presentation currently relies on early prototype geometric blocks, rudimentary spritesheets, and placeholder UI themes. To achieve commercial indie standing (comparable to *Stardew Valley*, *Graveyard Keeper*, or *Eastward*), a comprehensive, multi-phase artistic overhaul is required.

---

## 2. Asset Quality Breakdown

### A. Character Quality (Grade: C+)
- **Current State**: Archi and Danish sprites are 32×48 pixels across 4 directions (Down, Up, Left, Right). While palettes are distinct (auburn/green for Archi, brown/leather for Danish), silhouettes lack micro-details like hair movement, belt buckles, backpack straps, and expressive clothing folds.
- **Infected/Zombies**: Drifter and Sprinter spritesheets are functional but lack horrific rot, decayed cloth tatters, and glowing night-eyes that communicate nocturnal danger.
- **NPCs**: Portraits for Thomas, Elena, and Marcus exist at 64×64, but their in-world sprites are minimal variants of base player frames.
- **Recommendations**:
  - Re-author Archi and Danish with hand-tuned high-contrast pixel shading, distinctive hair silhouettes, and weapon sheaths.
  - Expand animation cycles from 4 frames to 6 frames for walking, plus dedicated 6-frame sprint cycles and 4-frame combat slash arcs.
  - Add grotesque rot, tattered garments, and night-glow eye pixels to Drifter, Sprinter, and The Warden boss.

### B. Environment & Tileset Quality (Grade: C)
- **Current State**: `farm_tiles.png` (256×128) provides simple flat grass, dirt, and stone tiles. There are no autotile bitmask transitions, terrain blend borders, or micro-texture variations (clover, pebbles, wildflower sprigs).
- **Buildings & Props**: Farmhouse cabin, well, and storage chest are rendered as flat 2D facades in `farm_props.png` without roof shingle texture, stone depth, or overhang shadows.
- **Regions**:
  - *Evergreen Village* reuses cabin sprites for the General Store and Blacksmith.
  - *Greenwood Forest* has solitary tree stamps rather than clustered deep-canopy forest foliage.
  - *Crystal Lake* has a flat blue water rectangle with no wave animation, shore foam, or glisten.
- **Recommendations**:
  - Re-author the 32×32 terrain tileset with 4-corner transition autotiling (Grass-to-Dirt, Grass-to-Cobble, Grass-to-Water).
  - Create distinctive architectural facades: Log Cabin with stone chimney, Village Store with striped canvas awning, Blacksmith with outdoor forge/anvil, and Forest Ranger Watchtower.
  - Implement animated multi-frame water tiles with foamlines and floating lilypads.

### C. UI & UX Quality (Grade: C+)
- **Current State**: High technical responsiveness, but uses default Godot flat grey/blue ThemeStyleBoxes and raw system fonts. Inventory slots display raw text labels (`seed_tu\nx5`) instead of pixel icons.
- **Main Menu**: Plain blue backdrop without illustrated game world art or animated environmental dust/light shafts.
- **Dialogue**: Lacks speaker portrait frame integration, ornate nameplates, or pulsing typewriter indicators.
- **Mobile Touch Controls**: Rectangular flat debug boxes rather than sleek semi-transparent circular thumbsticks and embossed action icons.
- **Recommendations**:
  - Design a unified "Survivor's Field Journal" visual language: weathered parchment, carved oak borders, and forged iron rivets.
  - Create a complete 24×24 pixel icon library for all 30+ items (Tools, Crops, Seeds, Weapons, Defenses, Medical, Salvage).
  - Redesign Main Menu with an illustrated panoramic pixel backdrop of Evergreen Valley.
  - Redesign Mobile Touch Controls with ergonomic translucent circular buttons.

### D. Lighting & Atmosphere Quality (Grade: B-)
- **Current State**: `DayNightModulate` works reliably across Dawn, Day, Dusk, and Night, but is purely global.
- **Deficiencies**: No local PointLight2D nodes exist. At night, cabin windows remain dark blue, streetlamps don't cast light, and the player carries no lantern or torch.
- **Recommendations**:
  - Add soft radial PointLight2D nodes to the Farmhouse porch, cabin windows (warm amber glow during night), streetlamps in the Village, and campfire/ranger posts.
  - Provide an ambient firefly particle system on the Farm during dusk/night.
  - Introduce dynamic weather particles (Rain drizzle with puddle ripples, morning fog).

---

## 3. Prioritized Replacement Matrix

| Priority | Asset / System | Target Directory | Description of Overhaul |
|---|---|---|---|
| **P0 (Critical)** | Core Protagonists (Archi & Danish) | `assets/characters/` | 6-frame walk, 6-frame sprint, 4-frame combat slash, high-contrast palette |
| **P0 (Critical)** | Core Terrain & Crops | `assets/environment/` | 32×32 autotile grass/dirt/stone, 4-stage animated crop growth cycles |
| **P1 (High)** | Farm & Village Buildings | `assets/environment/` | Handcrafted Log Cabin, General Store with awning, Blacksmith forge |
| **P1 (High)** | Pixel Art UI & Icons | `assets/ui/` | Weathered wood/iron HUD, 24×24 item icon database, 9-patch frames |
| **P1 (High)** | Lighting & Lightmaps | `scenes/world/` | Porch lanterns, glowing cabin windows, campsite torches, ambient fog |
| **P2 (Medium)** | Infected & Boss Visuals | `assets/characters/infected/` | Rotting skin tones, tattered garments, glowing eyes, boss ground crack decals |
| **P2 (Medium)** | Mobile Touch Controls | `scenes/ui/` | Sleek semi-transparent circular analog stick & embossed action icons |
| **P3 (Polish)** | Main Menu Illustration | `scenes/main_menu/` | 960×540 panoramic pixel-art title illustration with drifting atmospheric particles |

---

## 4. Multi-Agent Team Execution Plan

To execute this overhaul systematically without regressions:
- **Agent 1: Art Director** -> Establishes `ART_STYLE_GUIDE.md` (color palettes, pixel ratios, shading rules).
- **Agent 2: Environment Artist** -> Crafts detailed 32×32 tilesets, lush vegetation, building facades, and props.
- **Agent 3: Character Artist** -> Authors distinctive Archi & Danish sprites, NPC portraits, and horrifying zombies.
- **Agent 4: Animation Specialist** -> Integrates 6-frame movement, sprint cycles, harvest animations, and combat arcs.
- **Agent 5: UI/UX Designer** -> Crafts weathered wood/iron HUD, 24×24 item icon library, and sleek mobile touch overlay.
- **Agent 6: QA & Performance Engineer** -> Validates 60 FPS, captures "After" screenshots, and runs automated regressions.
