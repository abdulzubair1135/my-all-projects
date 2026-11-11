# EVERGREEN: AFTER THE FALL — ART STYLE GUIDE
**Version**: 1.0  
**Lead Art Director**: Agent 1 (Art Direction Lead)  
**Target Viewport**: 960 × 540 (16:9 2D Pixel Viewport, Integer Scaling)  
**Tile Grid**: 32 × 32 Pixels  

---

## 1. Visual Identity & Mood

*Evergreen: After the Fall* blends the warm, pastoral comfort of traditional farming RPGs (*Stardew Valley*, *Harvest Moon*) with the atmospheric survival horror of a post-collapse valley (*The Last of Us*, *Project Zomboid*).

- **Daytime (06:00 – 18:00)**: Soft golden sunshine, lush emerald pine greens, warm cedar wood, organic loam soils, and cheerful yellow wildflowers. Safety, renewal, and domestic productivity.
- **Dusk (18:00 – 20:00)**: Melancholic amber and violet gradients. Shadows lengthen; the peaceful valley transforms into a vulnerable frontier.
- **Nighttime (20:00 – 06:00)**: Deep desaturated navy-blues, eerie moonlight, silhouettes with glowing eyes in the mist, punctuated by the warm comforting amber radius of handcrafted porch lanterns and campfires.

---

## 2. Core Palette: "Valley & Rust" (32 Colors)

### Nature & Environment
- `#1b3a27` Deep Pine Shadow
- `#2d5e3b` Forest Green
- `#4a854d` Lush Meadow Grass
- `#7bb362` Spring Sprout Highlight
- `#b5cf7a` Sunlit Leaf / Clover
- `#302217` Rich Loam Soil (Watered)
- `#543d2b` Tilled Garden Earth (Dry)
- `#8c6747` Worn Footpath Dirt
- `#b59469` Pale Sand / Road Dust
- `#2a3b4c` Deep River Bed
- `#3e6382` Shimmering Lake Water
- `#73a4c2` Wave Crest / Foam Highlight

### Timber, Stone & Architecture
- `#241711` Weathered Log Dark
- `#4a3321` Hand-hewn Pine Plank
- `#7d5938` Warm Cedar Wood
- `#ab8054` Porch / Wood Highlight
- `#23272e` Basalt Foundation Dark
- `#454d5a` River Stone / Cobble
- `#717c8d` Slate Shingle / Anvil Grey
- `#a8b3c4` Polished Stone Highlight

### Protagonists & Characters
- `#4a2213` Archi's Auburn Hair
- `#783d23` Archi's Hair Midtone
- `#2b4a38` Archi's Herbalist Apron
- `#1c2229` Danish's Dark Hair
- `#42372f` Danish's Rugged Scavenger Vest
- `#7a5832` Danish's Tool Belt Leather
- `#f7d0a1` Warm Peach Skin
- `#dca172` Warm Skin Shadow

### Lighting, Horror & Accents
- `#ffbe53` Warm Amber Lantern Glow
- `#ffe391` Porch Light Filament
- `#b82323` Infected Blood / Warning Red
- `#3d4d35` Rotting Zombie Flesh Green
- `#161c29` Midnight Vignette Shadow
- `#f0f6ff` Crisp Moonlight Frost

---

## 3. Scale, Perspective & Grid Guidelines

1. **Logical Grid**: Every gameplay element aligns to a 32×32 pixel grid.
2. **Perspective**: 3/4 top-down camera angle with Y-sorting enabled (`y_sort_enabled = true`).
3. **Character Dimensions**:
   - Frame Canvas: 32×48 pixels (1×1.5 tiles).
   - Collision Shape: 14×8 pixel foot-aligned rectangle at bottom `(0, -4)`.
   - Visual Origin: Centered horizontally, bottom anchored at character feet `(16, 44)`.
4. **Light Source Direction**: Consistent directional sunlight from **Top-Left (10:30 clock position)**. Highlights land on upper and left surfaces; cast shadows fall toward bottom-right.
5. **No Sub-Pixel Rendering**: All sprites must maintain clean 1:1 pixel scaling without non-integer rotation or blur.

---

## 4. Animation Specifications

- **Locomotion**: 6 frames per directional walk (Down, Up, Left, Right). 10 FPS playback speed.
- **Sprint**: Dedicated 6-frame run with forward 12° torso lean and swinging arms. 14 FPS playback speed.
- **Combat Swing**: 4-frame arc:
  1. *Anticipation*: Weapon drawn back (0.08s)
  2. *Strike Arc*: Forward swoosh with pixel slash curve (0.06s)
  3. *Impact Followthrough*: Full extension with motion blur (0.10s)
  4. *Recovery*: Return to ready stance (0.12s)
- **Farming**: 4-frame Hoe swing, Watering can tilt with droplet stream, Harvest pluck.
