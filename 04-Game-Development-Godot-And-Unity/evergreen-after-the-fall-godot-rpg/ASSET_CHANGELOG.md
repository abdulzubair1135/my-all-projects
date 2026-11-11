# ASSET CHANGELOG & MIGRATION REGISTER
**Project**: Evergreen: After the Fall  
**Phase**: Visual Overhaul & Optimization  
**Date**: November 11, 2026  

---

## 1. Directory Structure Reorganization (Phase 4)
- Created `assets/source/` for uncompressed original development assets.
- Created `assets/optimized/` for runtime production assets.
- Created `assets/environment/` for terrain and structural props.
- Created `assets/animations/` for special effect sprite sequences.
- Created `assets/ui/` for 9-patch frames, portraits, and HUD skins.
- Created `docs/visual_audit/before/` with 20 engine baseline screenshots.
- Created `docs/visual_audit/after/` with 20 post-overhaul comparative screenshots.

---

## 2. Character Sprite Revisions (Phase 5)
- **Archi (`assets/characters/archi/archi_spritesheet.png`)**:
  - Re-authored 192×192 4-direction spritesheet adhering to the 32-color "Valley & Rust" palette.
  - Added distinctive auburn hair highlights (`#783d23`, `#9c5232`), herbalist green apron (`#2b4a38`) with front tool pocket, and sturdy brown work boots.
  - Authored Frame 4 attack swing with white-hot curved machete slash arc trail.
  - Added ground shadow ellipse (`#10141a`, alpha 90) under character feet.
- **Danish (`assets/characters/danish/danish_spritesheet.png`)**:
  - Re-authored 192×192 4-direction spritesheet with broad-shouldered silhouette.
  - Added leather scavenger vest (`#42372f`), tool belt with golden brass buckle (`#d4af37`), and hip-mounted steel wrench silhouette.
  - Authored Frame 4 heavy weapon swing with amber power impact curve.
  - Added ground shadow ellipse.
- **Infected (`drifter_spritesheet.png` & `sprinter_spritesheet.png`)**:
  - Drifter: Sickly decaying skin tones (`#475940`), tattered rags, and glowing yellow nocturnal eyes (`#fef08a`).
  - Sprinter: Feral hunched posture, elongated talons, and glowing red nocturnal eyes (`#ef4444`).

---

## 3. Environment & Tileset Revisions (Phase 6)
- **Farm Tiles (`assets/tilesets/farm_tiles.png`)**:
  - Tile 0: Multi-shade blade-dithered meadow grass with yellow buttercup flowers.
  - Tile 1: Grass-to-dirt organic blend.
  - Tile 2: Dry tilled garden soil with furrowed horizontal ridges.
  - Tile 3: Watered rich dark loam soil with glistening moisture sparkles.
  - Tile 4: Cobblestone pathway with mortar seams and stone highlights.
  - Tile 5: Lake water with animated wave crest foamlines.
  - Tile 6: Shoreline sand and gravel.
  - Tile 7: Cabin interior oak floorboards with woodgrain and nail heads.
- **Farm Props (`assets/props/farm_props.png`)**:
  - Farmhouse: Hand-hewn log walls, cedar roof shingles with highlights, stone chimney, and warm amber glowing window pane.
  - Water Well: Cobblestone circular rim, pitched roof, iron crank, and interior water reflection.
  - Storage Chest: Banded oak chest with brass keyhole latch.
  - Oak Tree: Three-tier foliage crown with ground shadow skirt.
  - Village General Store: Clapboard siding with red-and-white striped canvas awning.
  - Blacksmith Forge: Stone furnace with glowing red coals and iron anvil.

---

## 4. UI & Lighting Revisions (Phases 7 & 8)
- **Farm Porch Light**: Integrated a soft radial amber `PointLight2D` (160px radius, 1.25 energy) to the Farmhouse in `farm_environment.gd`, providing realistic safe-zone warmth during night cycles.
- **Mobile Touch Controls (`TouchControls.tscn`)**:
  - Replaced rectangular debug buttons with sleek semi-transparent circular buttons (`StyleBoxFlat` with 65px/28px/22px corner radius).
  - Provided distinct normal and pressed states with high-contrast amber accents.
- **Portraits (`portrait_archi.png`, `portrait_danish.png`)**:
  - Handcrafted 64×64 pixel-art bust portraits with emerald/grey eyes, catchlight sparkles, and rim lighting.
