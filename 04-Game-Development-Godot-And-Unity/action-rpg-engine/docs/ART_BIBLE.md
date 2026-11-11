# ART BIBLE — ASHEN KINGDOM

## 1. Visual Identity & Mood
- **Theme**: Dark Medieval Survival RPG, ruins of a fallen kingdom, somber and haunting.
- **Tone**: Atmospheric, mysterious, dangerous, grounded (not neon or overly whimsical).
- **Inspiration**: Muted European medieval dark fantasy, decaying stone, iron, ash, torchlight, creeping plague corruption.

## 2. Technical Specifications
- **Base Resolution (Viewport)**: 480 × 270 (16:9 native pixel-art canvas).
- **Window Scaling**: Scaled cleanly up to 1080p (4x), 1440p, and mobile screens using integer/aspect-preserving viewport scaling.
- **Texture Filter**: Nearest-neighbor (no linear filtering or blur).
- **Pixel Snap**: Enabled on 2D transforms and vertices to prevent subpixel jitter.

## 3. Grid & Sprite Dimensions
- **Standard Characters (Player, NPCs, Humanoid Zombies)**: 32 × 32 pixels.
- **Tall / Armored Humanoids**: 32 × 48 or 48 × 48 pixels.
- **Bosses (Plague Beast, Large Horrors)**: 64 × 64 to 96 × 96 pixels.
- **Tileset Grid**: 16 × 16 base tiles (floors, walls, paths) or 32 × 32 composite objects (trees, ruins, structures).
- **Icons / Inventory Slots**: 16 × 16 or 24 × 24 in UI frames.

## 4. Color Palette
A cohesive muted color palette emphasizing ash, rusted iron, decayed wood, and torchlight warmth:
- **Ash & Stone**: `#1a1c23`, `#2b2d42`, `#4a4e69`, `#72788d`, `#9da3b4`
- **Earth & Decayed Wood**: `#1e1512`, `#362419`, `#543d2b`, `#7c5c3f`, `#a47e58`
- **Rusted Metal & Armor**: `#23272a`, `#3e444c`, `#5d6673`, `#8d99ae`
- **Faded Royal Purple/Violet (Fallen Lineage)**: `#221226`, `#3d1e44`, `#5a2a66`, `#814294`
- **Torchlight / Flame Embers**: `#3d1308`, `#7a2b0e`, `#c45d1d`, `#f09a3e`, `#ffd166`
- **Plague & Blight (Toxic/Blighted Flesh)**: `#142314`, `#1d3a24`, `#2f5e3b`, `#488b56`, `#74c67a`
- **Blood / Damage Indicator**: `#3a0808`, `#6b1414`, `#a82323`, `#d94141`

## 5. Outlines & Shading
- **Outlines**: Dark selective outlines (colored outlines using the darkest ambient shade rather than pure `#000000` pitch black, unless framing UI or high-contrast foreground silhouettes).
- **Shading**: 3 to 4 tone clusters per surface (dark shadow, mid-tone, highlight, subtle specular rim).
- **Dithering**: Minimal to none on characters for readability; slight pattern dithering allowed on large ground tiles and stone transitions.

## 6. Proportions & Silhouette
- **Proportions**: Semi-chibi / stylized dark fantasy (approx. 3 heads tall for standard 32px characters), allowing clear weapon and armor reads.
- **Silhouettes**: Distinct headgear, cape/cloak edges, and weapon profiles to distinguish player, survivors, and enemy types at a glance.

## 7. Animation Conventions
- **Framerate**: 6 to 10 FPS for walking; 10 to 12 FPS for attack and dodge rolls.
- **Standard Directions**: 4-way base sprites (Down, Up, Side/Right) with horizontal flip for Left. 8-direction movement maps to the 4 visual sprite directions or 8 when full sheets exist.
- **Key States**:
  - `idle`: 2 to 4 frames (subtle breathing/stance shift).
  - `walk`: 4 to 6 frames (step cycle with bobbing).
  - `attack_light`: 3 to 4 frames (anticipation, strike, recovery).
  - `dodge`: 4 frames (roll/evasion with i-frames).
  - `hurt`: 2 frames (knockback recoil).
  - `death`: 4 to 5 frames (collapse to ground).

## 8. Lighting & Atmosphere
- Godot `CanvasModulate` used for global time-of-day tinting.
- `PointLight2D` with soft falloff for torches, campfires, and glowing plague cysts.
- Normal maps reserved for special environmental features if performance allows on mobile.
