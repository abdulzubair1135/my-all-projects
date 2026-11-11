# VISUAL REVIEW: 20 BASELINE SCREENSHOTS
**Project**: Evergreen: After the Fall  
**Date**: November 11, 2026  
**Auditor**: Lead Art Director & Production Orchestrator  
**Baseline Directory**: `docs/visual_audit/before/`

---

## 1. `01_main_menu.png` (Main Menu)
- **What looks good**: Functional layout, clean title typography, clear button navigation ("New Game", "Continue", "Settings", "Credits", "Exit").
- **What looks unfinished**: Solid dark blue-grey backdrop lacks illustrative scenery, atmospheric weather, or animated pixel-art background art.
- **What looks inconsistent**: Buttons use default flat theme styling rather than custom carved-wood / weathered-brass post-apocalyptic UI frames.
- **What is missing**: Illustrated pastoral valley sunset or ruined fence background artwork; drifting smoke/pollen particles.
- **What needs replacement**: Flat color rectangles with an evocative 960×540 illustrated pixel-art title screen.
- **What should be redesigned**: Panel borders, button 9-patch textures, and typography treatment.

---

## 2. `02_character_selection.png` (Character Selection Modal)
- **What looks good**: Side-by-side comparison cards for Archi and Danish, displaying distinct class identities and starting perks.
- **What looks unfinished**: Cards are plain grey boxes; portraits are tiny 64×64 icons with basic shading.
- **What looks inconsistent**: Font sizes and button outlines do not share a cohesive post-apocalyptic survivor aesthetic.
- **What is missing**: Full-body character concept art / large illustrated pixel busts; weapon silhouettes; difficulty badge icons.
- **What needs replacement**: Simple flat rect cards with ornate wooden/canvas-trimmed survivor dossiers.
- **What should be redesigned**: Character presentation cards, selection indicators, and perk descriptions.

---

## 3. `03_evergreen_farm_daytime.png` (Evergreen Farm Daytime)
- **What looks good**: 32×32 grid alignment, basic farm layout (cabin, well, tilled soil, perimeter fence, storage chest).
- **What looks unfinished**: Grass is flat uniform green without tufts, wild clover, soil dirt patches, or pebble scattering; cabin is a single 2D facade without depth.
- **What looks inconsistent**: Fence posts have sharp flat edges that don't match the organic contours of trees.
- **What is missing**: Animated chimneys/smoke, wildflower patches, pathways with edge blend transitions, tool sheds, chickens wandering naturally.
- **What needs replacement**: Flat green grass tileset with a 9-slice multi-variant terrain set with auto-tiling blends.
- **What should be redesigned**: Farmhouse cabin sprite (needs overhang eaves, wooden grain, stone chimney, glass sheen).

---

## 4. `04_evergreen_farm_nighttime.png` (Evergreen Farm Nighttime)
- **What looks good**: CanvasModulate deep blue tint creates recognizable nocturnal atmosphere.
- **What looks unfinished**: Darkness is uniform across the screen without local light sources (lanterns, porch lights, torch flickers).
- **What looks inconsistent**: Windows in the cabin stay dark blue rather than casting a warm amber glow onto the porch.
- **What is missing**: PointLight2D nodes for porch lantern, well bucket glow, fireflies in grass, and player flashlights/torches.
- **What needs replacement**: Flat global modulation needs local warm 2D radial light sources.
- **What should be redesigned**: Lighting strategy to balance horror tension and cozy safe-zone warmth.

---

## 5. `05_farmhouse_exterior.png` (Farmhouse Exterior & Porch)
- **What looks good**: Cabin scale is appropriately sized relative to player height (approx 2.5x player height).
- **What looks unfinished**: Front door lacks iron handle hardware; walls lack textured logs/planks; roof shingles lack edge highlights.
- **What looks inconsistent**: Well stones and cabin wood planks have slightly mismatched pixel outlines.
- **What is missing**: Hanging herbs, porch bench, firewood pile, boots on porch, rain barrels.
- **What needs replacement**: Flat brown box building with handcrafted layered log-cabin pixel art.
- **What should be redesigned**: Exterior prop placement to establish a lived-in survival homestead feeling.

---

## 6. `06_farmhouse_interior.png` (Farmhouse Interior / Porch Zone)
- **What looks good**: Clear boundary between exterior yard and shelter footprint.
- **What looks unfinished**: Interior space is represented on the same exterior canvas plane without wall separation or floorboards.
- **What looks inconsistent**: Indoor bed / kitchen objects placed directly on green terrain.
- **What is missing**: Dedicated interior room tileset (oak floorboards, stone fireplace, wooden kitchen table, rug, pantry shelves).
- **What needs replacement**: Direct outdoor bed placement with seamless interior cabin streaming or designated interior walls.
- **What should be redesigned**: Cabin interior as an intimate cozy refuge from the nighttime horrors.

---

## 7. `07_farming_area.png` (Farming Area & Crops)
- **What looks good**: Distinct states for tilled dry soil, dark watered soil, seedlings, growing vines, and mature crops.
- **What looks inconsistent**: Soil plot borders are stark 32×32 brown squares with hard transitions against green grass.
- **What is missing**: Dirt mound ridges, irrigation canal transitions, crop sway animations, water droplets/glisten effect.
- **What needs replacement**: Rigid square soil plots with organic rounded tilled mounds and blending corners.
- **What should be redesigned**: Crop growth sprites to have richer color saturation and distinct harvest outlines.

---

## 8. `08_evergreen_village.png` (Evergreen Village)
- **What looks good**: Spatial layout provides clear pathways between Lily's Store, Marcus's Forge, and Notice Board.
- **What looks unfinished**: Ground is largely blank; buildings use scaled-up farm prop placeholders.
- **What looks inconsistent**: Shop facades share the exact same silhouette as the farm cabin.
- **What is missing**: Cobblestone streets, market stalls, anvil and weapon racks for the smithy, wooden signposts, streetlamps.
- **What needs replacement**: Reused farm cabin sprites with bespoke commercial building facades (awning, forge chimney, shop counter).
- **What should be redesigned**: Village square into a bustling fortified settlement center.

---

## 9. `09_greenwood_forest.png` (Greenwood Forest)
- **What looks good**: Ranger station hut and roaming Drifter zombies establish immediate tension.
- **What looks unfinished**: Trees are sparse single stamps with identical silhouettes; canopy doesn't feel dense or oppressive.
- **What looks inconsistent**: Forest ground is identical color to the manicured farm lawn.
- **What is missing**: Overlapping multi-tiered pine/oak tree clusters, fallen hollow logs, moss, wild mushrooms, floating volumetric fog.
- **What needs replacement**: Solitary tree stamps with clustered dense forest canopy tile layers.
- **What should be redesigned**: Forest terrain with darker earthy moss tones and shadow overlays.

---

## 10. `10_crystal_lake.png` (Crystal Lake)
- **What looks good**: Serene atmosphere, water shoreline contrast, fishing pier structure.
- **What looks unfinished**: Water surface is static flat blue without wave ripples, foam foamlines, or water glisten.
- **What looks inconsistent**: Shoreline is a straight horizontal cut rather than natural curving sand/gravel banks.
- **What is missing**: Animated water shaders / sprite ripples, water lily pads, docked wooden rowboat, fishing bobber effects.
- **What needs replacement**: Flat blue rectangle with multi-frame animated lake water texture and wave edges.
- **What should be redesigned**: Shoreline transition to feature gravel, sand, and reed foliage.

---

## 11. `11_archi_walking.png` (Archi Walking)
- **What looks good**: 32×48 proportions, recognizable female silhouette, auburn hair, green vest/apron.
- **What looks unfinished**: 4-frame walk cycle has stiff vertical bob without dynamic leg swinging or hair bounce.
- **What looks inconsistent**: Footstep collision point doesn't align perfectly with the shadow base.
- **What is missing**: Secondary animation on hair, shoulder bag strap, tool holster, footstep dust puffs.
- **What needs replacement**: Basic 4-frame walk sheet with a polished 6-frame smooth walking cycle.
- **What should be redesigned**: Clothing folds and contrast shading to enhance depth on 32×32 logical grid.

---

## 12. `12_danish_walking.png` (Danish Walking)
- **What looks good**: Broad-shouldered silhouette, leather jacket/vest, tool belt, rugged survivor aesthetic.
- **What looks unfinished**: Arms move rigidly along torso without natural forward/back counterbalance swing.
- **What looks inconsistent**: Shading on back and front views has slightly different highlight angles.
- **What is missing**: Tool strap bounce, wrench/hammer swinging from hip belt, boot scuff particles.
- **What needs replacement**: Stiff 4-frame walk cycle with fluid 6-frame stride.
- **What should be redesigned**: Silhouette clarity to make him instantly distinguishable from zombies at night.

---

## 13. `13_archi_sprinting.png` (Archi Sprinting)
- **What looks good**: Increased frame rate, forward lean angle conveys speed and urgency.
- **What looks unfinished**: Sprint poses are just accelerated walk frames rather than dedicated low-center-of-gravity sprint poses.
- **What looks inconsistent**: Stamina drain in HUD doesn't show visual sparks or fatigue indicator on the character sprite.
- **What is missing**: Trailing dust puffs, wind lines, hair trailing back in wind.
- **What needs replacement**: Recycled walk frames with dedicated high-energy running animation frames.
- **What should be redesigned**: Sprint animation keyframes (extended stride, pumped arms).

---

## 14. `14_combat_scene.png` (Combat Scene - Melee Attack)
- **What looks good**: Player attack frame with forward weapon extension, clear weapon hitbox area.
- **What looks unfinished**: Machete blade is a single static pixel strip without arc trail or whoosh slash VFX.
- **What looks inconsistent**: Enemy stagger animation is a flat red color modulate rather than an impact flash + particle burst.
- **What is missing**: Curved pixel slash trail (white-to-translucent swoosh), blood/splatter impact droplets, screen shake punch.
- **What needs replacement**: Static strike pose with 3-frame arc animation (Windup -> Slash Arc -> Followthrough).
- **What should be redesigned**: Combat visual feedback (particle bursts, impact pauses, directional slash trails).

---

## 15. `15_zombie_encounter.png` (Zombie Encounter)
- **What looks good**: Clear visual differentiation between slow Drifter (shambler) and hunched Sprinter (agile).
- **What looks unfinished**: Zombie clothes and skin palette are somewhat desaturated without grotesque rotting detail or glowing eyes.
- **What looks inconsistent**: Drifter silhouette is too close to a normal human NPC in low light.
- **What is missing**: Tattered clothes, exposed rib/bone pixels, glowing faint yellow/red eye glints in darkness, shadow pools.
- **What needs replacement**: Simplistic zombie spritesheets with horrific, decayed infected sprites.
- **What should be redesigned**: Zombie aggro visual cues (exclamation mark / red eye flash upon detecting sound/sight).

---

## 16. `16_hud.png` (In-Game HUD)
- **What looks good**: High readability, clean layout, portrait box, HP & Stamina bars, clock, quickbar slots [1..5].
- **What looks inconsistent**: Flat modern UI progress bars with sharp borders clash with 2D retro pixel-art world.
- **What is missing**: Pixel-art ornate frames (wooden border with iron studs), heart/energy icons, weather icons (sun/rain/moon).
- **What needs replacement**: Generic Godot theme ThemeStyleBoxes with custom 9-patch pixel frames.
- **What should be redesigned**: Entire HUD skin into a unified weathered leather-and-iron survival journal style.

---

## 17. `17_inventory.png` (Inventory & Storage Backpack)
- **What looks good**: 24 slots grid layout, item names, stack numbers, easy navigation.
- **What looks unfinished**: Standard grey Godot buttons with raw text labels (`seed_tu\nx5`) rather than dedicated high-res item icons.
- **What looks inconsistent**: Item icons not rendered inside slots; text truncation looks unpolished.
- **What is missing**: 24×24 pixel icons for every weapon, seed, crop, material, and medical supply; item detail tooltip panel with flavor text.
- **What needs replacement**: Text-only button grid with icon-driven visual inventory slots.
- **What should be redesigned**: Full backpack modal with equipment slots (Weapon, Armor, Accessory) and item stats panel.

---

## 18. `18_dialogue.png` (NPC Dialogue Box)
- **What looks good**: Clear speaker title ("Thomas"), multi-line dialogue support, responsive text wrapping.
- **What looks unfinished**: Dialogue panel is a generic translucent box; speaker portrait is absent from the box.
- **What looks inconsistent**: Font is system default antialiased font rather than crisp pixel font.
- **What is missing**: Large 64×64 animated talking portrait in corner of box, nameplate banner, pulsing "Press E" arrow indicator.
- **What needs replacement**: Standard label box with a handcrafted parchment/wood dialog frame.
- **What should be redesigned**: Dialogue box layout to integrate speaker portrait, stylized nameplate, and animated cursor.

---

## 19. `19_relationship_screen.png` (Relationship Screen)
- **What looks good**: Comprehensive tracking of Trust, Closeness, Respect, and Shared Memories list.
- **What looks unfinished**: Displayed as raw plain-text labels on a dark canvas.
- **What looks inconsistent**: Lacks visual heart / friendship meters, milestone badges, or companion character portraits.
- **What is missing**: Interlocking heart meters, memory polaroids/sketches, companion status portrait with facial expressions.
- **What needs replacement**: Plain text labels with an illustrated "Companion Diary" interface.
- **What should be redesigned**: Romance & partnership screen into an intimate, emotionally resonant journal.

---

## 20. `20_mobile_ui.png` (Mobile Touch Controls)
- **What looks good**: Functional analog virtual stick and 5 action buttons (ATTACK, HEAVY, DODGE, INTERACT, RUN).
- **What looks unfinished**: Joystick is a flat grey rectangle with square knob; buttons are plain rectangular text buttons.
- **What looks inconsistent**: Modern square buttons obstruct the game view and look like debug tools.
- **What is missing**: Semi-transparent circular thumbstick with inner deadzone ring; circular action buttons with embossed pixel icons (sword, shield, boot, hand).
- **What needs replacement**: Rectangular debug buttons with beautiful ergonomic semi-transparent circular buttons.
- **What should be redesigned**: Touch control overlay to be sleek, unobtrusive, and visually cohesive with the indie pixel aesthetic.
