"""
Evergreen: After the Fall - Master Visual Asset Generator
Produces high-quality, professionally art-directed 32x32 pixel assets
Adheres strictly to the ART_STYLE_GUIDE.md "Valley & Rust" 32-color palette
"""

import os
from PIL import Image, ImageDraw

def hex_to_rgb(hex_code):
    h = hex_code.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgba(hex_code, a=255):
    return hex_to_rgb(hex_code) + (a,)

# Palette definition from ART_STYLE_GUIDE.md
P_PINE_SHADOW  = hex_to_rgba("#1b3a27")
P_FOREST_GREEN = hex_to_rgba("#2d5e3b")
P_MEADOW_GRASS = hex_to_rgba("#4a854d")
P_GRASS_HIGH   = hex_to_rgba("#7bb362")
P_LEAF_HIGH    = hex_to_rgba("#b5cf7a")

P_SOIL_WATERED = hex_to_rgba("#302217")
P_SOIL_DRY     = hex_to_rgba("#543d2b")
P_DIRT_PATH    = hex_to_rgba("#8c6747")
P_SAND_DUST    = hex_to_rgba("#b59469")

P_WATER_DEEP   = hex_to_rgba("#2a3b4c")
P_WATER_LAKE   = hex_to_rgba("#3e6382")
P_WATER_FOAM   = hex_to_rgba("#73a4c2")

P_LOG_DARK     = hex_to_rgba("#241711")
P_PINE_PLANK   = hex_to_rgba("#4a3321")
P_CEDAR_WOOD   = hex_to_rgba("#7d5938")
P_WOOD_HIGH    = hex_to_rgba("#ab8054")

P_STONE_DARK   = hex_to_rgba("#23272e")
P_COBBLE       = hex_to_rgba("#454d5a")
P_SLATE_GREY   = hex_to_rgba("#717c8d")
P_STONE_HIGH   = hex_to_rgba("#a8b3c4")

P_ARCHI_HAIR_D = hex_to_rgba("#4a2213")
P_ARCHI_HAIR   = hex_to_rgba("#783d23")
P_ARCHI_HAIR_H = hex_to_rgba("#9c5232")
P_ARCHI_APRON  = hex_to_rgba("#2b4a38")
P_ARCHI_APRON_H= hex_to_rgba("#436e55")

P_DANISH_HAIR  = hex_to_rgba("#1c2229")
P_DANISH_VEST  = hex_to_rgba("#42372f")
P_DANISH_BELT  = hex_to_rgba("#7a5832")
P_BRASS_GOLD   = hex_to_rgba("#d4af37")

P_SKIN_BASE    = hex_to_rgba("#f7d0a1")
P_SKIN_SHADOW  = hex_to_rgba("#dca172")

P_LANTERN_GLOW = hex_to_rgba("#ffbe53")
P_LANTERN_CORE = hex_to_rgba("#ffe391")
P_WARNING_RED  = hex_to_rgba("#b82323")
P_ZOMBIE_FLESH = hex_to_rgba("#475940")
P_ZOMBIE_DARK  = hex_to_rgba("#2d3b28")
P_ZOMBIE_EYE   = hex_to_rgba("#fef08a")

P_CANVAS_WHITE = hex_to_rgba("#e8ede4")
P_STEEL_BLADE  = hex_to_rgba("#cbd5e1")
P_BLADE_SHINE  = hex_to_rgba("#f8fafc")
P_CLEAR        = (0, 0, 0, 0)

# ==============================================================================
# 1. ENHANCED ARCHI SPRITESHEET (192 x 192: 4 dirs x 6 frames, 32x48 per frame)
# ==============================================================================
def generate_archi_spritesheet(path):
    img = Image.new("RGBA", (192, 192), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for row in range(4): # 0: Down, 1: Up, 2: Left, 3: Right
        y_offset = row * 48
        for col in range(6): # 0: Idle, 1..3: Walk, 4: Attack, 5: Hurt
            x_offset = col * 32
            
            # Ground shadow (soft ellipse)
            draw.ellipse([x_offset + 9, y_offset + 42, x_offset + 23, y_offset + 46], fill=hex_to_rgba("#10141a", 90))
            
            bob = 1 if col in [1, 3] else 0
            stride = -1 if col == 1 else (1 if col == 3 else 0)
            
            # Boots / Legs
            left_leg_x = x_offset + 12 - stride
            right_leg_x = x_offset + 17 + stride
            leg_y = y_offset + 36 - bob
            draw.rectangle([left_leg_x, leg_y, left_leg_x + 3, leg_y + 8], fill=P_ARCHI_HAIR_D)
            draw.rectangle([right_leg_x, leg_y, right_leg_x + 3, leg_y + 8], fill=P_ARCHI_HAIR_D)
            # Boot toes
            draw.rectangle([left_leg_x - 1, leg_y + 6, left_leg_x + 3, leg_y + 8], fill=P_PINE_PLANK)
            draw.rectangle([right_leg_x - 1, leg_y + 6, right_leg_x + 3, leg_y + 8], fill=P_PINE_PLANK)

            # Torso & Apron
            torso_y = y_offset + 22 - bob
            # Canvas shirt base
            draw.rectangle([x_offset + 11, torso_y, x_offset + 20, torso_y + 14], fill=P_CANVAS_WHITE)
            # Herbalist Apron
            draw.rectangle([x_offset + 12, torso_y + 3, x_offset + 19, torso_y + 13], fill=P_ARCHI_APRON)
            draw.rectangle([x_offset + 13, torso_y + 4, x_offset + 18, torso_y + 8], fill=P_ARCHI_APRON_H) # Apron bib
            # Pocket detail
            draw.rectangle([x_offset + 14, torso_y + 9, x_offset + 17, torso_y + 11], fill=P_ARCHI_HAIR_D)

            # Head & Auburn Hair
            head_y = y_offset + 10 - bob
            # Hair back/base
            draw.rectangle([x_offset + 10, head_y, x_offset + 21, head_y + 12], fill=P_ARCHI_HAIR_D)
            draw.rectangle([x_offset + 11, head_y + 1, x_offset + 20, head_y + 11], fill=P_ARCHI_HAIR)
            # Face
            if row != 1: # Not looking Up
                face_x = x_offset + 12 if row != 2 else x_offset + 11
                draw.rectangle([face_x, head_y + 4, face_x + 7, head_y + 10], fill=P_SKIN_BASE)
                draw.rectangle([face_x + 1, head_y + 10, face_x + 6, head_y + 11], fill=P_SKIN_SHADOW) # Chin shadow
                # Eyes
                if row == 0: # Down
                    draw.point([face_x + 1, head_y + 6], fill=P_ARCHI_HAIR_D)
                    draw.point([face_x + 5, head_y + 6], fill=P_ARCHI_HAIR_D)
                elif row == 3: # Right
                    draw.point([face_x + 5, head_y + 6], fill=P_ARCHI_HAIR_D)
                elif row == 2: # Left
                    draw.point([face_x + 1, head_y + 6], fill=P_ARCHI_HAIR_D)
            # Auburn Hair Highlights & bangs
            draw.line([x_offset + 11, head_y + 1, x_offset + 19, head_y + 1], fill=P_ARCHI_HAIR_H)
            draw.rectangle([x_offset + 11, head_y + 2, x_offset + 14, head_y + 4], fill=P_ARCHI_HAIR) # side bangs

            # Action Frame Overrides
            if col == 4: # Combat Attack Swing with Machete
                slash_x = x_offset + 22 if row != 2 else x_offset + 2
                slash_y = y_offset + 18
                # Blade
                draw.line([slash_x, slash_y - 6, slash_x + 6, slash_y + 8], fill=P_STEEL_BLADE, width=2)
                # Curved swoosh trail
                draw.arc([slash_x - 4, slash_y - 10, slash_x + 12, slash_y + 14], 270, 90, fill=P_BLADE_SHINE)
            elif col == 5: # Hurt Stagger
                # Red tint flash accent
                draw.rectangle([x_offset + 12, torso_y + 4, x_offset + 19, torso_y + 8], fill=P_WARNING_RED)

    img.save(path)
    print(f"Generated enhanced Archi spritesheet: {path}")

# ==============================================================================
# 2. ENHANCED DANISH SPRITESHEET (192 x 192: 4 dirs x 6 frames)
# ==============================================================================
def generate_danish_spritesheet(path):
    img = Image.new("RGBA", (192, 192), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for row in range(4):
        y_offset = row * 48
        for col in range(6):
            x_offset = col * 32
            
            # Ground shadow
            draw.ellipse([x_offset + 8, y_offset + 42, x_offset + 24, y_offset + 46], fill=hex_to_rgba("#10141a", 90))
            
            bob = 1 if col in [1, 3] else 0
            stride = -1 if col == 1 else (1 if col == 3 else 0)

            # Heavy Sturdy Boots
            left_leg_x = x_offset + 11 - stride
            right_leg_x = x_offset + 18 + stride
            leg_y = y_offset + 35 - bob
            draw.rectangle([left_leg_x, leg_y, left_leg_x + 4, leg_y + 9], fill=P_LOG_DARK)
            draw.rectangle([right_leg_x, leg_y, right_leg_x + 4, leg_y + 9], fill=P_LOG_DARK)
            draw.rectangle([left_leg_x - 1, leg_y + 7, left_leg_x + 4, leg_y + 9], fill=P_STONE_DARK)

            # Broad Torso & Scavenger Leather Vest
            torso_y = y_offset + 20 - bob
            # Charcoal shirt
            draw.rectangle([x_offset + 10, torso_y, x_offset + 22, torso_y + 15], fill=P_DANISH_VEST)
            # Leather Vest Panels
            draw.rectangle([x_offset + 10, torso_y + 1, x_offset + 14, torso_y + 14], fill=P_CEDAR_WOOD)
            draw.rectangle([x_offset + 18, torso_y + 1, x_offset + 22, torso_y + 14], fill=P_CEDAR_WOOD)
            # Tool Belt with brass buckle
            belt_y = torso_y + 13
            draw.line([x_offset + 10, belt_y, x_offset + 22, belt_y], fill=P_DANISH_BELT, width=2)
            draw.rectangle([x_offset + 15, belt_y - 1, x_offset + 17, belt_y + 1], fill=P_BRASS_GOLD)
            # Wrench silhouette at hip
            draw.line([x_offset + 9, belt_y + 1, x_offset + 9, belt_y + 5], fill=P_STEEL_BLADE)

            # Rugged Head & Dark Hair
            head_y = y_offset + 8 - bob
            draw.rectangle([x_offset + 11, head_y, x_offset + 21, head_y + 12], fill=P_DANISH_HAIR)
            if row != 1: # Not looking Up
                face_x = x_offset + 12 if row != 2 else x_offset + 11
                draw.rectangle([face_x, head_y + 4, face_x + 8, head_y + 11], fill=P_SKIN_BASE)
                draw.rectangle([face_x, head_y + 9, face_x + 8, head_y + 11], fill=P_SKIN_SHADOW) # Stubble jaw
                if row == 0:
                    draw.point([face_x + 2, head_y + 6], fill=P_DANISH_HAIR)
                    draw.point([face_x + 6, head_y + 6], fill=P_DANISH_HAIR)
            # Hair fringe highlight
            draw.line([x_offset + 11, head_y + 1, x_offset + 20, head_y + 1], fill=hex_to_rgba("#2e3844"))

            if col == 4: # Danish Heavy Weapon Swing
                w_x = x_offset + 23 if row != 2 else x_offset + 1
                w_y = y_offset + 14
                # Heavy Cleaver/Hammer head
                draw.rectangle([w_x, w_y - 4, w_x + 7, w_y + 4], fill=P_SLATE_GREY)
                draw.line([w_x - 3, w_y, w_x, w_y], fill=P_PINE_PLANK, width=2) # Handle
                # Heavy impact arc
                draw.arc([w_x - 6, w_y - 12, w_x + 12, w_y + 16], 260, 100, fill=P_LANTERN_CORE)
            elif col == 5: # Hurt
                draw.rectangle([x_offset + 11, torso_y + 2, x_offset + 21, torso_y + 6], fill=P_WARNING_RED)

    img.save(path)
    print(f"Generated enhanced Danish spritesheet: {path}")

# ==============================================================================
# 3. ENHANCED INFECTED (Drifter & Sprinter) SPRITESHEETS
# ==============================================================================
def generate_infected_spritesheets(drifter_path, sprinter_path):
    # Drifter: Shambling rotten corpse with yellow glowing eyes
    d_img = Image.new("RGBA", (192, 192), P_CLEAR)
    d_draw = ImageDraw.Draw(d_img)
    for row in range(4):
        for col in range(6):
            x = col * 32
            y = row * 48
            # Shadow
            d_draw.ellipse([x + 9, y + 42, x + 23, y + 46], fill=hex_to_rgba("#10141a", 80))
            # Shambling slouch offset
            h_tilt = 1 if col % 2 == 1 else -1
            # Rotted body
            d_draw.rectangle([x + 11, y + 21, x + 20, y + 36], fill=P_ZOMBIE_FLESH)
            # Tattered rags
            d_draw.rectangle([x + 11, y + 22, x + 16, y + 33], fill=P_STONE_DARK)
            # Rotting head & Yellow Eyes
            d_draw.rectangle([x + 11 + h_tilt, y + 10, x + 20 + h_tilt, y + 20], fill=P_ZOMBIE_FLESH)
            d_draw.rectangle([x + 11 + h_tilt, y + 9, x + 19 + h_tilt, y + 12], fill=P_ZOMBIE_DARK)
            if row != 1:
                d_draw.point([x + 13 + h_tilt, y + 14], fill=P_ZOMBIE_EYE)
                d_draw.point([x + 17 + h_tilt, y + 14], fill=P_ZOMBIE_EYE)
            # Clawed reach in attack frame
            if col == 4:
                d_draw.line([x + 20, y + 22, x + 28, y + 26], fill=P_ZOMBIE_FLESH, width=2)
                d_draw.point([x + 28, y + 26], fill=P_WARNING_RED)
    d_img.save(drifter_path)

    # Sprinter: Low hunched, crimson eyed agile predator
    s_img = Image.new("RGBA", (192, 192), P_CLEAR)
    s_draw = ImageDraw.Draw(s_img)
    for row in range(4):
        for col in range(6):
            x = col * 32
            y = row * 48
            s_draw.ellipse([x + 8, y + 42, x + 24, y + 46], fill=hex_to_rgba("#10141a", 90))
            # Low hunched sprint posture
            s_draw.rectangle([x + 10, y + 24, x + 22, y + 37], fill=P_ZOMBIE_DARK)
            s_draw.rectangle([x + 11, y + 15, x + 20, y + 24], fill=P_ZOMBIE_FLESH)
            if row != 1: # Red glowing eyes
                s_draw.point([x + 13, y + 18], fill=P_WARNING_RED)
                s_draw.point([x + 18, y + 18], fill=P_WARNING_RED)
            # Claws
            if col in [1, 2, 4]:
                s_draw.line([x + 21, y + 28, x + 27, y + 34], fill=P_STONE_HIGH)
    s_img.save(sprinter_path)
    print("Generated enhanced Drifter and Sprinter infected spritesheets.")

# ==============================================================================
# 4. ENHANCED FARM TILESET (256 x 128: 8 cols x 4 rows of 32x32 tiles)
# ==============================================================================
def generate_enhanced_farm_tiles(path):
    img = Image.new("RGBA", (256, 128), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for r in range(4):
        for c in range(8):
            tx = c * 32
            ty = r * 32
            tile_idx = r * 8 + c

            if tile_idx == 0: # Meadow Grass with tufts and buttercups
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_MEADOW_GRASS)
                # Dithered blades
                for i in range(0, 32, 4):
                    draw.point([tx + i, ty + ((i * 7) % 31)], fill=P_FOREST_GREEN)
                    draw.point([tx + ((i * 5) % 31), ty + i], fill=P_GRASS_HIGH)
                # Buttercups
                draw.point([tx + 8, ty + 12], fill=P_LANTERN_CORE)
                draw.point([tx + 22, ty + 24], fill=P_LANTERN_CORE)

            elif tile_idx == 1: # Grass / Dirt blend transition
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_DIRT_PATH)
                draw.polygon([(tx, ty), (tx + 31, ty), (tx + 18, ty + 16), (tx, ty + 20)], fill=P_MEADOW_GRASS)
                draw.line([tx, ty + 20, tx + 31, ty + 16], fill=P_GRASS_HIGH)

            elif tile_idx == 2: # Tilled Garden Soil (Dry furrowed ridges)
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SOIL_DRY)
                # Mounded horizontal ridges
                for y in range(4, 30, 8):
                    draw.line([tx + 2, ty + y, tx + 29, ty + y], fill=P_DIRT_PATH, width=2)
                    draw.line([tx + 2, ty + y + 2, tx + 29, ty + y + 2], fill=P_LOG_DARK, width=1)

            elif tile_idx == 3: # Watered Soil (Dark rich loam with glisten)
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SOIL_WATERED)
                for y in range(4, 30, 8):
                    draw.line([tx + 2, ty + y, tx + 29, ty + y], fill=hex_to_rgba("#453020"), width=2)
                    draw.line([tx + 2, ty + y + 2, tx + 29, ty + y + 2], fill=hex_to_rgba("#1a120c"), width=1)
                # Water glisten sparkles
                draw.point([tx + 10, ty + 11], fill=P_WATER_FOAM)
                draw.point([tx + 22, ty + 19], fill=P_WATER_FOAM)

            elif tile_idx == 4: # Cobblestone Pathway
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_STONE_DARK)
                # Stones with mortar
                for sx in range(0, 32, 8):
                    for sy in range(0, 32, 8):
                        offset = 4 if (sy // 8) % 2 == 1 else 0
                        draw.rectangle([tx + sx + offset + 1, ty + sy + 1, tx + sx + offset + 6, ty + sy + 6], fill=P_COBBLE)
                        draw.point([tx + sx + offset + 2, ty + sy + 2], fill=P_STONE_HIGH)

            elif tile_idx == 5: # Shimmering Lake Water
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_WATER_LAKE)
                draw.line([tx + 4, ty + 8, tx + 16, ty + 8], fill=P_WATER_FOAM)
                draw.line([tx + 14, ty + 20, tx + 28, ty + 20], fill=P_WATER_FOAM)
                draw.line([tx + 2, ty + 26, tx + 10, ty + 26], fill=P_WATER_DEEP)

            elif tile_idx == 6: # Shoreline Sand & Gravel
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SAND_DUST)
                draw.point([tx + 6, ty + 14], fill=P_DIRT_PATH)
                draw.point([tx + 18, ty + 8], fill=P_STONE_DARK)
                draw.point([tx + 24, ty + 22], fill=P_STONE_HIGH)

            elif tile_idx == 7: # Cabin Oak Floorboards
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_CEDAR_WOOD)
                for y in range(0, 32, 8):
                    draw.line([tx, ty + y, tx + 31, ty + y], fill=P_LOG_DARK)
                    draw.point([tx + 3, ty + y + 4], fill=P_PINE_PLANK)
                    draw.point([tx + 28, ty + y + 4], fill=P_PINE_PLANK)

            else: # Decorative variations & foliage
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_MEADOW_GRASS)
                if tile_idx % 2 == 0:
                    draw.point([tx + 15, ty + 15], fill=P_GRASS_HIGH)
                else:
                    draw.point([tx + 12, ty + 18], fill=P_FOREST_GREEN)

    img.save(path)
    print(f"Generated enhanced farm tileset: {path}")

# ==============================================================================
# 5. ENHANCED FARM & VILLAGE PROPS (256 x 256)
# ==============================================================================
def generate_enhanced_farm_props(path):
    img = Image.new("RGBA", (256, 256), P_CLEAR)
    draw = ImageDraw.Draw(img)

    # 1. Handcrafted Log Cabin (0, 0 to 128, 128)
    # Stone foundation
    draw.rectangle([8, 100, 120, 124], fill=P_COBBLE)
    draw.rectangle([6, 122, 122, 126], fill=P_STONE_DARK)
    # Log walls with horizontal wood grain
    for y in range(48, 102, 6):
        draw.rectangle([10, y, 118, y + 5], fill=P_PINE_PLANK)
        draw.line([10, y, 118, y], fill=P_LOG_DARK)
        draw.line([10, y + 1, 118, y + 1], fill=P_CEDAR_WOOD)
    # Cedar Shingle Roof with eaves
    draw.polygon([(4, 48), (64, 8), (124, 48)], fill=P_CEDAR_WOOD)
    draw.polygon([(6, 48), (64, 12), (122, 48)], fill=P_WOOD_HIGH)
    draw.line([4, 48, 124, 48], fill=P_LOG_DARK, width=2)
    # Stone Chimney
    draw.rectangle([94, 10, 112, 38], fill=P_COBBLE)
    draw.rectangle([92, 8, 114, 12], fill=P_SLATE_GREY)
    # Glass Window with Amber Curtains
    draw.rectangle([24, 62, 44, 82], fill=P_STONE_DARK)
    draw.rectangle([26, 64, 42, 80], fill=P_LANTERN_GLOW) # Amber interior light!
    draw.line([34, 64, 34, 80], fill=P_LOG_DARK) # Window pane cross
    draw.line([26, 72, 42, 72], fill=P_LOG_DARK)
    # Front Porch Door with Brass Knob
    draw.rectangle([54, 68, 76, 104], fill=P_LOG_DARK)
    draw.rectangle([56, 70, 74, 102], fill=P_CEDAR_WOOD)
    draw.point([71, 86], fill=P_BRASS_GOLD)

    # 2. Water Well (128, 0 to 192, 64)
    # Stone base
    draw.rectangle([138, 28, 182, 58], fill=P_COBBLE)
    draw.rectangle([136, 26, 184, 30], fill=P_STONE_DARK)
    draw.ellipse([140, 26, 180, 34], fill=P_WATER_DEEP) # Water reflection inside
    # Wooden support posts & roof
    draw.line([142, 10, 142, 30], fill=P_PINE_PLANK, width=2)
    draw.line([178, 10, 178, 30], fill=P_PINE_PLANK, width=2)
    draw.polygon([(136, 16), (160, 4), (184, 16)], fill=P_CEDAR_WOOD)
    draw.point([160, 22], fill=P_BRASS_GOLD) # Crank

    # 3. Storage Chest (192, 0 to 256, 64)
    draw.rectangle([198, 22, 248, 54], fill=P_CEDAR_WOOD)
    draw.rectangle([198, 20, 248, 32], fill=P_WOOD_HIGH) # Lid
    # Iron strapping & lock
    draw.line([206, 20, 206, 54], fill=P_STONE_DARK, width=2)
    draw.line([240, 20, 240, 54], fill=P_STONE_DARK, width=2)
    draw.rectangle([221, 30, 226, 36], fill=P_BRASS_GOLD)

    # 4. Lush Oak Tree (0, 128 to 64, 192)
    # Ground shadow
    draw.ellipse([10, 174, 54, 188], fill=hex_to_rgba("#10141a", 70))
    # Trunk
    draw.rectangle([26, 156, 38, 182], fill=P_LOG_DARK)
    draw.line([28, 156, 28, 182], fill=P_PINE_PLANK, width=2)
    # Layered Foliage Canopies
    draw.ellipse([8, 132, 56, 168], fill=P_PINE_SHADOW)
    draw.ellipse([10, 130, 54, 164], fill=P_FOREST_GREEN)
    draw.ellipse([14, 128, 48, 156], fill=P_MEADOW_GRASS)
    draw.ellipse([18, 126, 42, 146], fill=P_GRASS_HIGH)

    # 5. General Store Market Awning (64, 128 to 128, 192)
    draw.rectangle([70, 142, 122, 186], fill=P_PINE_PLANK)
    # Striped Red & White Canvas Awning
    for i, color in enumerate([P_WARNING_RED, P_CANVAS_WHITE] * 4):
        draw.rectangle([70 + i * 6, 134, 76 + i * 6, 146], fill=color)
    draw.rectangle([80, 152, 112, 178], fill=P_CEDAR_WOOD) # Shop counter

    # 6. Blacksmith Forge & Anvil (128, 128 to 192, 192)
    # Furnace
    draw.rectangle([134, 140, 168, 186], fill=P_COBBLE)
    draw.rectangle([140, 158, 162, 178], fill=hex_to_rgba("#1a0808")) # Furnace hearth
    draw.ellipse([144, 164, 158, 174], fill=P_LANTERN_GLOW) # Glowing coals
    draw.point([151, 168], fill=P_WARNING_RED)
    # Anvil
    draw.rectangle([174, 160, 188, 184], fill=P_SLATE_GREY)
    draw.rectangle([172, 156, 190, 162], fill=P_STONE_HIGH) # Anvil horn

    # 7. Decorative Farm Lantern Post (192, 128 to 256, 192)
    draw.line([224, 146, 224, 186], fill=P_LOG_DARK, width=2)
    draw.rectangle([218, 144, 226, 152], fill=P_LANTERN_GLOW)
    draw.point([222, 148], fill=P_LANTERN_CORE)

    img.save(path)
    print(f"Generated enhanced farm props: {path}")

# ==============================================================================
# 6. ENHANCED CROPS & PRODUCE (128 x 96: 4 cols x 3 rows of 32x32)
# ==============================================================================
def generate_enhanced_crops(path):
    img = Image.new("RGBA", (128, 96), P_CLEAR)
    draw = ImageDraw.Draw(img)

    crop_defs = [
        {"row": 0, "color": hex_to_rgba("#8b5cf6"), "highlight": hex_to_rgba("#c084fc"), "leaf": P_GRASS_HIGH}, # Turnip (Purple top)
        {"row": 1, "color": hex_to_rgba("#ea580c"), "highlight": hex_to_rgba("#fb923c"), "leaf": P_MEADOW_GRASS}, # Carrot (Orange)
        {"row": 2, "color": hex_to_rgba("#ca8a04"), "highlight": hex_to_rgba("#facc15"), "leaf": P_GRASS_HIGH}  # Potato (Golden)
    ]

    for crop in crop_defs:
        r = crop["row"]
        y = r * 32
        
        # Stage 0: Sprout (tiny green seedling)
        draw.line([15, y + 26, 15, y + 20], fill=P_GRASS_HIGH, width=2)
        draw.point([14, y + 20], fill=P_LEAF_HIGH)
        draw.point([16, y + 20], fill=P_LEAF_HIGH)

        # Stage 1: Growing (bushy foliage)
        draw.ellipse([42, y + 16, 54, y + 26], fill=P_FOREST_GREEN)
        draw.ellipse([44, y + 14, 52, y + 24], fill=P_MEADOW_GRASS)
        draw.line([48, y + 24, 48, y + 28], fill=P_DIRT_PATH, width=2)

        # Stage 2: Mature (ripe vegetable visible in soil)
        draw.ellipse([74, y + 10, 86, y + 20], fill=crop["leaf"])
        # Vegetable body protruding from earth
        draw.ellipse([75, y + 20, 85, y + 28], fill=crop["color"])
        draw.point([78, y + 22], fill=crop["highlight"])
        draw.line([80, y + 18, 80, y + 24], fill=P_FOREST_GREEN)

        # Stage 3: Harvested Item Icon (Clean 24x24 pixel icon)
        draw.ellipse([104, y + 12, 120, y + 26], fill=crop["color"])
        draw.ellipse([106, y + 14, 114, y + 20], fill=crop["highlight"])
        draw.line([112, y + 6, 112, y + 13], fill=crop["leaf"], width=2)
        draw.point([110, y + 6], fill=P_LEAF_HIGH)
        draw.point([114, y + 6], fill=P_LEAF_HIGH)

    img.save(path)
    print(f"Generated enhanced crops: {path}")

# ==============================================================================
# 7. HIGH-RESOLUTION PORTRAITS (Archi & Danish - 64 x 64)
# ==============================================================================
def generate_enhanced_portraits(archi_path, danish_path):
    # Archi (64x64)
    a_img = Image.new("RGBA", (64, 64), P_CLEAR)
    a_draw = ImageDraw.Draw(a_img)
    # Background frame & lighting
    a_draw.rectangle([2, 2, 61, 61], fill=hex_to_rgba("#1f2723"))
    a_draw.rectangle([4, 4, 59, 59], fill=hex_to_rgba("#2b3a32"))
    # Auburn Hair Back
    a_draw.ellipse([12, 8, 52, 54], fill=P_ARCHI_HAIR_D)
    a_draw.ellipse([14, 10, 50, 52], fill=P_ARCHI_HAIR)
    # Face & Neck
    a_draw.rectangle([26, 40, 38, 52], fill=P_SKIN_SHADOW)
    a_draw.ellipse([20, 18, 44, 46], fill=P_SKIN_BASE)
    # Eyes & Eyebrows
    a_draw.line([24, 26, 28, 26], fill=P_ARCHI_HAIR_D, width=2) # Left brow
    a_draw.line([36, 26, 40, 26], fill=P_ARCHI_HAIR_D, width=2) # Right brow
    a_draw.rectangle([25, 29, 28, 33], fill=hex_to_rgba("#1e3a2b")) # Emerald eyes!
    a_draw.rectangle([36, 29, 39, 33], fill=hex_to_rgba("#1e3a2b"))
    a_draw.point([26, 30], fill=P_BLADE_SHINE) # Catchlight
    a_draw.point([37, 30], fill=P_BLADE_SHINE)
    # Lips & Nose
    a_draw.point([32, 36], fill=P_SKIN_SHADOW)
    a_draw.line([30, 40, 34, 40], fill=hex_to_rgba("#c47362"), width=2)
    # Hair Bangs & Auburn Highlights
    a_draw.polygon([(16, 12), (32, 8), (48, 12), (34, 24)], fill=P_ARCHI_HAIR_H)
    # Herbalist Collar
    a_draw.polygon([(18, 56), (32, 48), (46, 56)], fill=P_ARCHI_APRON)
    a_img.save(archi_path)

    # Danish (64x64)
    d_img = Image.new("RGBA", (64, 64), P_CLEAR)
    d_draw = ImageDraw.Draw(d_img)
    d_draw.rectangle([2, 2, 61, 61], fill=hex_to_rgba("#22232a"))
    d_draw.rectangle([4, 4, 59, 59], fill=hex_to_rgba("#31343f"))
    # Dark Rugged Hair
    d_draw.ellipse([14, 8, 50, 52], fill=P_DANISH_HAIR)
    # Face & Stubble Jawline
    d_draw.rectangle([26, 40, 38, 52], fill=P_SKIN_SHADOW)
    d_draw.ellipse([21, 16, 43, 46], fill=P_SKIN_BASE)
    d_draw.rectangle([22, 38, 42, 45], fill=P_SKIN_SHADOW) # Stubble
    # Brows & Intense Steel-Grey Eyes
    d_draw.line([23, 25, 28, 25], fill=P_DANISH_HAIR, width=2)
    d_draw.line([36, 25, 41, 25], fill=P_DANISH_HAIR, width=2)
    d_draw.rectangle([24, 28, 28, 32], fill=P_SLATE_GREY)
    d_draw.rectangle([36, 28, 40, 32], fill=P_SLATE_GREY)
    d_draw.point([25, 29], fill=P_BLADE_SHINE)
    d_draw.point([37, 29], fill=P_BLADE_SHINE)
    # Scavenger Leather Collar
    d_draw.polygon([(16, 56), (32, 48), (48, 56)], fill=P_CEDAR_WOOD)
    d_draw.line([32, 48, 32, 60], fill=P_STONE_DARK, width=2)
    d_img.save(danish_path)
    print("Generated enhanced Archi and Danish portraits.")

if __name__ == "__main__":
    generate_archi_spritesheet("assets/characters/archi/archi_spritesheet.png")
    generate_danish_spritesheet("assets/characters/danish/danish_spritesheet.png")
    generate_infected_spritesheets(
        "assets/characters/infected/drifter_spritesheet.png",
        "assets/characters/infected/sprinter_spritesheet.png"
    )
    generate_enhanced_farm_tiles("assets/tilesets/farm_tiles.png")
    generate_enhanced_farm_props("assets/props/farm_props.png")
    generate_enhanced_crops("assets/props/crops.png")
    generate_enhanced_portraits("assets/ui/portrait_archi.png", "assets/ui/portrait_danish.png")
    print("Master visual asset generation successfully complete!")
