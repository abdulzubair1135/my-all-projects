"""
Evergreen: After the Fall - Master Professional Pixel Asset Generator
Produces high-quality, seamless, commercial-grade 32x32 tilesets, props, and character sheets.
"""

import os
from PIL import Image, ImageDraw

def hex_to_rgba(hex_code, a=255):
    h = hex_code.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

# Professional Palette
P_CLEAR        = (0, 0, 0, 0)
P_SHADOW_ALPHA = hex_to_rgba("#0d1217", 90)

# Nature Greens (Rich, seamless, soothing emerald tones)
P_GRASS_BASE   = hex_to_rgba("#3d7343")
P_GRASS_DARK   = hex_to_rgba("#2d5933")
P_GRASS_LIGHT  = hex_to_rgba("#4f8f55")
P_GRASS_TENDER = hex_to_rgba("#6bb872")
P_FLOWER_YEL   = hex_to_rgba("#fbd34d")
P_FLOWER_WHT   = hex_to_rgba("#f8fafc")
P_FLOWER_CORE  = hex_to_rgba("#ea580c")

# Earth, Roads & Soil
P_SOIL_DRY_B   = hex_to_rgba("#593f2c")
P_SOIL_DRY_D   = hex_to_rgba("#422c1d")
P_SOIL_DRY_L   = hex_to_rgba("#73533a")

P_SOIL_WET_B   = hex_to_rgba("#382315")
P_SOIL_WET_D   = hex_to_rgba("#22140a")
P_SOIL_WET_L   = hex_to_rgba("#4f321f")
P_SOIL_SPARK   = hex_to_rgba("#93c5fd")

P_DIRT_ROAD_B  = hex_to_rgba("#82664d")
P_DIRT_ROAD_D  = hex_to_rgba("#664d36")
P_DIRT_ROAD_L  = hex_to_rgba("#9c7d60")

# Cobblestones (Natural river stones with warm mortar)
P_COBBLE_BASE  = hex_to_rgba("#646c77")
P_COBBLE_DARK  = hex_to_rgba("#474d56")
P_COBBLE_LIGHT = hex_to_rgba("#86909e")
P_MORTAR       = hex_to_rgba("#3a3e45")

# Wood & Architecture
P_WOOD_BASE    = hex_to_rgba("#6e4f35")
P_WOOD_DARK    = hex_to_rgba("#4e3623")
P_WOOD_LIGHT   = hex_to_rgba("#8f6746")
P_WOOD_NAIL    = hex_to_rgba("#291c12")

# Water & Lake
P_WATER_DEEP   = hex_to_rgba("#23486a")
P_WATER_BASE   = hex_to_rgba("#32638f")
P_WATER_LIGHT  = hex_to_rgba("#487ea8")
P_WATER_CREST  = hex_to_rgba("#93c5fd")

# Shoreline Sand & Gravel
P_SAND_BASE    = hex_to_rgba("#a99171")
P_SAND_DARK    = hex_to_rgba("#8c7558")
P_SAND_LIGHT   = hex_to_rgba("#c4ad8d")

# Structural / Urban Tiles
P_STONE_SLAB   = hex_to_rgba("#525861")
P_STONE_SLAB_D = hex_to_rgba("#393e45")
P_STONE_SLAB_L = hex_to_rgba("#707884")

P_LAB_FLOOR    = hex_to_rgba("#cbd5e1")
P_LAB_GROUT    = hex_to_rgba("#94a3b8")
P_LAB_SHINE    = hex_to_rgba("#f1f5f9")

P_BALLAST_BASE = hex_to_rgba("#33373d")
P_BALLAST_DARK = hex_to_rgba("#1f2226")
P_BALLAST_LITE = hex_to_rgba("#4b5159")

# Characters: Archi
P_SKIN         = hex_to_rgba("#fcd3a7")
P_SKIN_SHADOW  = hex_to_rgba("#dfa776")
P_ARCHI_HAIR_D = hex_to_rgba("#4e2213")
P_ARCHI_HAIR_M = hex_to_rgba("#7d3c22")
P_ARCHI_HAIR_L = hex_to_rgba("#a75432")
P_ARCHI_APRON  = hex_to_rgba("#284d34")
P_ARCHI_APRON_L= hex_to_rgba("#3c6f4c")
P_ARCHI_SHIRT  = hex_to_rgba("#f1f5f9")
P_LEATHER_BOOT = hex_to_rgba("#382316")

# Characters: Danish
P_DANISH_HAIR  = hex_to_rgba("#1b1f24")
P_DANISH_HAIR_L= hex_to_rgba("#323942")
P_DANISH_VEST  = hex_to_rgba("#4a3b30")
P_DANISH_SHIRT = hex_to_rgba("#3b4252")
P_BRASS_GOLD   = hex_to_rgba("#eab308")
P_STEEL_GREY   = hex_to_rgba("#94a3b8")
P_BLADE_WHITE  = hex_to_rgba("#ffffff")
P_WARNING_RED  = hex_to_rgba("#dc2626")

# Infected
P_ZOMBIE_FLESH = hex_to_rgba("#52614b")
P_ZOMBIE_DARK  = hex_to_rgba("#364232")
P_ZOMBIE_PALE  = hex_to_rgba("#728269")
P_ZOMBIE_EYE_Y = hex_to_rgba("#facc15")
P_ZOMBIE_EYE_R = hex_to_rgba("#ef4444")

# ==============================================================================
# 1. MASTER 32x32 TILESET (farm_tiles.png - 256x128)
# ==============================================================================
def generate_tileset(path):
    img = Image.new("RGBA", (256, 128), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for r in range(4):
        for c in range(8):
            tx = c * 32
            ty = r * 32
            idx = r * 8 + c

            if idx == 0:
                # Tile 0: Seamless Emerald Meadow Grass
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_GRASS_BASE)
                for x in range(0, 32, 2):
                    for y in range(0, 32, 2):
                        if (x * 3 + y * 7) % 5 == 0:
                            draw.point([tx + x, ty + y], fill=P_GRASS_LIGHT)
                        elif (x * 7 + y * 3) % 7 == 0:
                            draw.point([tx + x, ty + y], fill=P_GRASS_DARK)

            elif idx == 1:
                # Tile 1: Meadow Grass with Wildflower Sprigs
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_GRASS_BASE)
                for x in range(0, 32, 2):
                    for y in range(0, 32, 2):
                        if (x * 3 + y * 7) % 5 == 0:
                            draw.point([tx + x, ty + y], fill=P_GRASS_LIGHT)
                        elif (x * 7 + y * 3) % 7 == 0:
                            draw.point([tx + x, ty + y], fill=P_GRASS_DARK)
                # Buttercups and daisies
                draw.point([tx + 8, ty + 10], fill=P_FLOWER_YEL)
                draw.point([tx + 7, ty + 10], fill=P_FLOWER_YEL)
                draw.point([tx + 8, ty + 11], fill=P_FLOWER_CORE)
                draw.point([tx + 22, ty + 20], fill=P_FLOWER_WHT)
                draw.point([tx + 23, ty + 20], fill=P_FLOWER_YEL)
                draw.point([tx + 14, ty + 24], fill=P_FLOWER_YEL)

            elif idx == 2:
                # Tile 2: Dry Tilled Garden Soil (furrowed ridges)
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SOIL_DRY_B)
                for y in range(3, 30, 6):
                    draw.line([tx + 2, ty + y, tx + 29, ty + y], fill=P_SOIL_DRY_L, width=2)
                    draw.line([tx + 2, ty + y + 2, tx + 29, ty + y + 2], fill=P_SOIL_DRY_D, width=1)
                draw.point([tx + 9, ty + 15], fill=P_SOIL_DRY_L)
                draw.point([tx + 21, ty + 27], fill=P_SOIL_DRY_L)

            elif idx == 3:
                # Tile 3: Watered Tilled Soil (deep rich loam with glisten)
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SOIL_WET_B)
                for y in range(3, 30, 6):
                    draw.line([tx + 2, ty + y, tx + 29, ty + y], fill=P_SOIL_WET_L, width=2)
                    draw.line([tx + 2, ty + y + 2, tx + 29, ty + y + 2], fill=P_SOIL_WET_D, width=1)
                draw.point([tx + 8, ty + 9], fill=P_SOIL_SPARK)
                draw.point([tx + 20, ty + 21], fill=P_SOIL_SPARK)

            elif idx == 4:
                # Tile 4: River Cobblestone Pavers (natural interlocking stones)
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_MORTAR)
                stones = [
                    (2, 2, 13, 13), (16, 2, 29, 11),
                    (2, 17, 14, 29), (17, 15, 29, 27),
                    (11, 11, 18, 19), (27, 8, 31, 17), (0, 12, 3, 20)
                ]
                for x1, y1, x2, y2 in stones:
                    draw.rectangle([tx + x1, ty + y1, tx + x2, ty + y2], fill=P_COBBLE_BASE)
                    draw.line([tx + x1, ty + y1, tx + x2, ty + y1], fill=P_COBBLE_LIGHT)
                    draw.line([tx + x1, ty + y1, tx + x1, ty + y2], fill=P_COBBLE_LIGHT)
                    draw.line([tx + x1, ty + y2, tx + x2, ty + y2], fill=P_COBBLE_DARK)
                    draw.line([tx + x2, ty + y1, tx + x2, ty + y2], fill=P_COBBLE_DARK)

            elif idx == 5:
                # Tile 5: Sandy Dirt Road / Forest Trail
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_DIRT_ROAD_B)
                for x in range(0, 32, 2):
                    for y in range(0, 32, 2):
                        if (x * 5 + y * 3) % 4 == 0:
                            draw.point([tx + x, ty + y], fill=P_DIRT_ROAD_L)
                        elif (x * 3 + y * 5) % 6 == 0:
                            draw.point([tx + x, ty + y], fill=P_DIRT_ROAD_D)

            elif idx == 6:
                # Tile 6: Shimmering Lake Water
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_WATER_BASE)
                draw.line([tx + 4, ty + 6, tx + 14, ty + 6], fill=P_WATER_CREST)
                draw.line([tx + 18, ty + 15, tx + 28, ty + 15], fill=P_WATER_CREST)
                draw.line([tx + 3, ty + 23, tx + 12, ty + 23], fill=P_WATER_CREST)
                draw.line([tx + 14, ty + 28, tx + 22, ty + 28], fill=P_WATER_DEEP)

            elif idx == 7:
                # Tile 7: Cedar / Oak Wood Floorboards
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_WOOD_BASE)
                for y in range(0, 32, 8):
                    draw.line([tx, ty + y, tx + 31, ty + y], fill=P_WOOD_DARK)
                    draw.line([tx, ty + y + 1, tx + 31, ty + y + 1], fill=P_WOOD_LIGHT)
                    draw.point([tx + 4, ty + y + 4], fill=P_WOOD_NAIL)
                    draw.point([tx + 26, ty + y + 4], fill=P_WOOD_NAIL)

            elif idx == 8:
                # Tile 8: Shoreline Sand & Fine Gravel
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_SAND_BASE)
                for x in range(0, 32, 3):
                    for y in range(0, 32, 3):
                        if (x + y) % 2 == 0:
                            draw.point([tx + x, ty + y], fill=P_SAND_LIGHT)
                        else:
                            draw.point([tx + x, ty + y], fill=P_SAND_DARK)

            elif idx == 9:
                # Tile 9: Stone Plaza Slab / Concrete Bunker Floor
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_STONE_SLAB)
                draw.rectangle([tx + 1, ty + 1, tx + 30, ty + 30], outline=P_STONE_SLAB_D)
                draw.line([tx + 1, ty + 1, tx + 30, ty + 1], fill=P_STONE_SLAB_L)
                draw.line([tx + 1, ty + 1, tx + 1, ty + 30], fill=P_STONE_SLAB_L)

            elif idx == 10:
                # Tile 10: Clinical Lab Tiles
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_LAB_FLOOR)
                draw.line([tx, ty + 16, tx + 31, ty + 16], fill=P_LAB_GROUT)
                draw.line([tx + 16, ty, tx + 16, ty + 31], fill=P_LAB_GROUT)
                draw.line([tx + 1, ty + 1, tx + 15, ty + 1], fill=P_LAB_SHINE)
                draw.line([tx + 17, ty + 1, tx + 30, ty + 1], fill=P_LAB_SHINE)

            elif idx == 11:
                # Tile 11: Railway Dark Stone Ballast
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_BALLAST_BASE)
                for x in range(0, 32, 4):
                    for y in range(0, 32, 4):
                        draw.point([tx + x, ty + y], fill=P_BALLAST_LITE)
                        draw.point([tx + x + 2, ty + y + 2], fill=P_BALLAST_DARK)

            else:
                # Fill remaining tiles with meadow grass variants
                draw.rectangle([tx, ty, tx + 31, ty + 31], fill=P_GRASS_BASE)
                if idx % 2 == 0:
                    draw.point([tx + 14, ty + 14], fill=P_GRASS_LIGHT)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Generated clean professional tileset: {path}")

# ==============================================================================
# 2. MASTER FARM & VILLAGE PROPS (farm_props.png - 256x256)
# ==============================================================================
def generate_farm_props(path):
    img = Image.new("RGBA", (256, 256), P_CLEAR)
    draw = ImageDraw.Draw(img)

    # 1. Farmhouse (0, 0 to 128, 128)
    # Stone foundation (y: 96 to 124)
    draw.rectangle([8, 96, 120, 124], fill=P_COBBLE_BASE)
    draw.rectangle([6, 122, 122, 126], fill=P_COBBLE_DARK)
    # Timber log walls (y: 48 to 96)
    draw.rectangle([12, 48, 116, 96], fill=P_WOOD_BASE)
    for bx in [12, 40, 64, 88, 114]:
        draw.rectangle([bx - 2, 48, bx + 2, 96], fill=P_WOOD_DARK)
    draw.rectangle([12, 48, 116, 52], fill=P_WOOD_DARK)
    draw.rectangle([12, 92, 116, 96], fill=P_WOOD_DARK)
    # Windows with warm interior amber glow
    draw.rectangle([20, 60, 36, 78], fill=hex_to_rgba("#fde68a"), outline=P_WOOD_DARK, width=2)
    draw.line([28, 60, 28, 78], fill=P_WOOD_DARK)
    draw.line([20, 69, 36, 69], fill=P_WOOD_DARK)
    draw.rectangle([92, 60, 108, 78], fill=hex_to_rgba("#fde68a"), outline=P_WOOD_DARK, width=2)
    draw.line([100, 60, 100, 78], fill=P_WOOD_DARK)
    draw.line([92, 69, 108, 69], fill=P_WOOD_DARK)
    # Front Porch Door
    draw.rectangle([54, 68, 74, 110], fill=P_WOOD_DARK)
    draw.rectangle([56, 70, 72, 108], fill=P_WOOD_BASE)
    draw.point([69, 90], fill=P_BRASS_GOLD)
    # Stone Chimney
    draw.rectangle([94, 8, 108, 32], fill=P_COBBLE_BASE)
    draw.rectangle([92, 6, 110, 10], fill=P_COBBLE_DARK)
    # Pitched Shingle Roof
    draw.polygon([(4, 52), (64, 12), (124, 52)], fill=hex_to_rgba("#833a2a"))
    for sy, sx in [(44, 12), (36, 24), (28, 36), (20, 48)]:
        draw.line([sx, sy, 128 - sx, sy], fill=hex_to_rgba("#a14835"), width=2)

    # 2. Water Well (32 x 48 at 136, 0)
    wx, wy = 136, 0
    draw.ellipse([wx + 2, wy + 26, wx + 30, wy + 46], fill=P_COBBLE_BASE, outline=P_COBBLE_DARK, width=2)
    draw.ellipse([wx + 6, wy + 30, wx + 26, wy + 42], fill=P_WATER_DEEP)
    draw.rectangle([wx + 3, wy + 10, wx + 6, wy + 32], fill=P_WOOD_DARK)
    draw.rectangle([wx + 26, wy + 10, wx + 29, wy + 32], fill=P_WOOD_DARK)
    draw.polygon([(wx, wy + 14), (wx + 16, wy + 2), (wx + 32, wy + 14)], fill=hex_to_rgba("#833a2a"))
    draw.line([wx + 16, wy + 8, wx + 16, wy + 26], fill=P_DIRT_ROAD_L)
    draw.point([wx + 16, wy + 24], fill=P_BRASS_GOLD)

    # 3. Wooden Storage Chest (32 x 24 at 176, 12)
    cx, cy = 176, 12
    draw.rectangle([cx + 2, cy + 2, cx + 30, cy + 22], fill=P_WOOD_BASE, outline=P_WOOD_DARK)
    draw.rectangle([cx + 2, cy + 2, cx + 5, cy + 22], fill=P_STEEL_GREY)
    draw.rectangle([cx + 27, cy + 2, cx + 30, cy + 22], fill=P_STEEL_GREY)
    draw.line([cx + 2, cy + 10, cx + 30, cy + 10], fill=P_WOOD_DARK)
    draw.rectangle([cx + 14, cy + 9, cx + 18, cy + 14], fill=P_BRASS_GOLD)

    # 4. Lush Pine Tree (64 x 96 at 136, 56)
    tx, ty = 136, 56
    # Trunk
    draw.rectangle([tx + 27, ty + 60, tx + 37, ty + 94], fill=P_WOOD_DARK)
    # Foliage tiers (rich evergreen pine)
    c_p1 = hex_to_rgba("#225e34")
    c_p2 = hex_to_rgba("#1b4d2b")
    c_p3 = hex_to_rgba("#133b20")
    draw.polygon([(tx + 32, ty), (tx + 12, ty + 36), (tx + 52, ty + 36)], fill=c_p1)
    draw.polygon([(tx + 32, ty + 20), (tx + 6, ty + 60), (tx + 58, ty + 60)], fill=c_p2)
    draw.polygon([(tx + 32, ty + 42), (tx + 2, ty + 82), (tx + 62, ty + 82)], fill=c_p3)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Generated clean master farm props: {path}")

# ==============================================================================
# 3. ARCHI SPRITESHEET (192x192: 4 dirs x 6 frames)
# ==============================================================================
def generate_archi_spritesheet(path):
    img = Image.new("RGBA", (192, 192), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for row in range(4): # 0: Down, 1: Up, 2: Left, 3: Right
        y_base = row * 48
        for col in range(6):
            x_base = col * 32
            draw.ellipse([x_base + 9, y_base + 42, x_base + 23, y_base + 46], fill=P_SHADOW_ALPHA)

            bob = 1 if col in [1, 3] else 0
            stride = -1 if col == 1 else (1 if col == 3 else 0)

            # Boots & Legs
            leg_y = y_base + 35 - bob
            draw.rectangle([x_base + 12 - stride, leg_y, x_base + 14 - stride, leg_y + 5], fill=P_ARCHI_HAIR_D)
            draw.rectangle([x_base + 17 + stride, leg_y, x_base + 19 + stride, leg_y + 5], fill=P_ARCHI_HAIR_D)
            draw.rectangle([x_base + 11 - stride, leg_y + 5, x_base + 15 - stride, leg_y + 9], fill=P_LEATHER_BOOT)
            draw.rectangle([x_base + 16 + stride, leg_y + 5, x_base + 20 + stride, leg_y + 9], fill=P_LEATHER_BOOT)

            # Torso & Herbalist Apron
            torso_y = y_base + 20 - bob
            draw.rectangle([x_base + 11, torso_y, x_base + 20, torso_y + 15], fill=P_ARCHI_SHIRT)
            draw.rectangle([x_base + 12, torso_y + 3, x_base + 19, torso_y + 14], fill=P_ARCHI_APRON)
            draw.rectangle([x_base + 13, torso_y + 3, x_base + 18, torso_y + 7], fill=P_ARCHI_APRON_L)
            draw.line([x_base + 12, torso_y + 8, x_base + 19, torso_y + 8], fill=P_LEATHER_BOOT)
            draw.point([x_base + 18, torso_y + 9], fill=P_BRASS_GOLD)

            # Head & Auburn Hair
            head_y = y_base + 8 - bob
            draw.rectangle([x_base + 11, head_y + 4, x_base + 20, head_y + 13], fill=P_SKIN)
            draw.rectangle([x_base + 10, head_y, x_base + 21, head_y + 5], fill=P_ARCHI_HAIR_M)
            draw.rectangle([x_base + 9, head_y + 2, x_base + 11, head_y + 11], fill=P_ARCHI_HAIR_D)
            draw.rectangle([x_base + 20, head_y + 2, x_base + 22, head_y + 11], fill=P_ARCHI_HAIR_D)

            if row == 0: # Facing Down
                draw.point([x_base + 13, head_y + 8], fill=P_ARCHI_HAIR_D)
                draw.point([x_base + 18, head_y + 8], fill=P_ARCHI_HAIR_D)
                draw.point([x_base + 15, head_y + 11], fill=P_SKIN_SHADOW)
            elif row == 1: # Facing Up
                draw.rectangle([x_base + 11, head_y + 2, x_base + 20, head_y + 12], fill=P_ARCHI_HAIR_M)
            elif row == 2: # Facing Left
                draw.point([x_base + 12, head_y + 8], fill=P_ARCHI_HAIR_D)
            elif row == 3: # Facing Right
                draw.point([x_base + 19, head_y + 8], fill=P_ARCHI_HAIR_D)

            # Combat / Swing in Frame 4
            if col == 4:
                w_x = x_base + 22 if row != 2 else x_base + 2
                w_y = y_base + 16
                draw.line([w_x, w_y, w_x + 5, w_y - 8], fill=P_BLADE_WHITE, width=2)
                draw.point([w_x + 6, w_y - 9], fill=P_STEEL_GREY)
            elif col == 5: # Hurt flash
                draw.rectangle([x_base + 11, torso_y + 2, x_base + 20, torso_y + 6], fill=P_WARNING_RED)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Generated clean professional Archi sheet: {path}")

# ==============================================================================
# 4. DANISH SPRITESHEET (192x192: 4 dirs x 6 frames)
# ==============================================================================
def generate_danish_spritesheet(path):
    img = Image.new("RGBA", (192, 192), P_CLEAR)
    draw = ImageDraw.Draw(img)

    for row in range(4):
        y_base = row * 48
        for col in range(6):
            x_base = col * 32
            draw.ellipse([x_base + 9, y_base + 42, x_base + 23, y_base + 46], fill=P_SHADOW_ALPHA)

            bob = 1 if col in [1, 3] else 0
            stride = -1 if col == 1 else (1 if col == 3 else 0)

            # Boots & Cargo Pants
            leg_y = y_base + 35 - bob
            draw.rectangle([x_base + 11 - stride, leg_y, x_base + 14 - stride, leg_y + 5], fill=P_DANISH_SHIRT)
            draw.rectangle([x_base + 17 + stride, leg_y, x_base + 20 + stride, leg_y + 5], fill=P_DANISH_SHIRT)
            draw.rectangle([x_base + 10 - stride, leg_y + 5, x_base + 15 - stride, leg_y + 9], fill=hex_to_rgba("#18191b"))
            draw.rectangle([x_base + 16 + stride, leg_y + 5, x_base + 21 + stride, leg_y + 9], fill=hex_to_rgba("#18191b"))

            # Heavy Scavenger Torso
            torso_y = y_base + 20 - bob
            draw.rectangle([x_base + 10, torso_y, x_base + 21, torso_y + 15], fill=P_DANISH_VEST)
            draw.line([x_base + 15, torso_y, x_base + 15, torso_y + 15], fill=P_DANISH_HAIR, width=2)
            draw.line([x_base + 10, torso_y + 11, x_base + 21, torso_y + 11], fill=hex_to_rgba("#18191b"), width=2)
            draw.point([x_base + 15, torso_y + 11], fill=P_BRASS_GOLD)

            # Head & Dark Hair
            head_y = y_base + 8 - bob
            draw.rectangle([x_base + 11, head_y + 4, x_base + 20, head_y + 13], fill=P_SKIN)
            draw.rectangle([x_base + 10, head_y, x_base + 21, head_y + 4], fill=P_DANISH_HAIR)
            draw.rectangle([x_base + 9, head_y + 1, x_base + 11, head_y + 8], fill=P_DANISH_HAIR)
            draw.rectangle([x_base + 20, head_y + 1, x_base + 22, head_y + 8], fill=P_DANISH_HAIR)

            if row == 0:
                draw.point([x_base + 13, head_y + 7], fill=P_DANISH_HAIR)
                draw.point([x_base + 18, head_y + 7], fill=P_DANISH_HAIR)
                draw.line([x_base + 12, head_y + 11, x_base + 19, head_y + 11], fill=P_SKIN_SHADOW)
            elif row == 1:
                draw.rectangle([x_base + 10, head_y + 2, x_base + 21, head_y + 11], fill=P_DANISH_HAIR)
            elif row == 2:
                draw.point([x_base + 12, head_y + 7], fill=P_DANISH_HAIR)
            elif row == 3:
                draw.point([x_base + 19, head_y + 7], fill=P_DANISH_HAIR)

            if col == 4: # Heavy Cleaver Swing
                w_x = x_base + 23 if row != 2 else x_base + 1
                w_y = y_base + 14
                draw.rectangle([w_x, w_y - 4, w_x + 6, w_y + 4], fill=P_STEEL_GREY)
                draw.line([w_x - 3, w_y, w_x, w_y], fill=P_WOOD_BASE, width=2)
            elif col == 5:
                draw.rectangle([x_base + 11, torso_y + 2, x_base + 21, torso_y + 6], fill=P_WARNING_RED)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"Generated clean professional Danish sheet: {path}")

# ==============================================================================
# 5. INFECTED SPRITESHEETS (drifter & sprinter)
# ==============================================================================
def generate_infected_sheets(drifter_path, sprinter_path):
    # Drifter
    d_img = Image.new("RGBA", (192, 192), P_CLEAR)
    d_draw = ImageDraw.Draw(d_img)
    for row in range(4):
        for col in range(6):
            x = col * 32
            y = row * 48
            d_draw.ellipse([x + 9, y + 42, x + 23, y + 46], fill=P_SHADOW_ALPHA)
            tilt = 1 if col % 2 == 1 else -1
            # Rotted body
            d_draw.rectangle([x + 11, y + 21, x + 20, y + 36], fill=P_ZOMBIE_FLESH)
            d_draw.rectangle([x + 11, y + 22, x + 16, y + 33], fill=P_STONE_SLAB_D)
            # Head & glowing yellow eyes
            d_draw.rectangle([x + 11 + tilt, y + 10, x + 20 + tilt, y + 20], fill=P_ZOMBIE_FLESH)
            d_draw.rectangle([x + 11 + tilt, y + 9, x + 19 + tilt, y + 12], fill=P_ZOMBIE_DARK)
            if row != 1:
                d_draw.point([x + 13 + tilt, y + 14], fill=P_ZOMBIE_EYE_Y)
                d_draw.point([x + 17 + tilt, y + 14], fill=P_ZOMBIE_EYE_Y)
            if col == 4:
                d_draw.line([x + 20, y + 22, x + 28, y + 26], fill=P_ZOMBIE_FLESH, width=2)
                d_draw.point([x + 28, y + 26], fill=P_WARNING_RED)
    os.makedirs(os.path.dirname(drifter_path), exist_ok=True)
    d_img.save(drifter_path)

    # Sprinter
    s_img = Image.new("RGBA", (192, 192), P_CLEAR)
    s_draw = ImageDraw.Draw(s_img)
    for row in range(4):
        for col in range(6):
            x = col * 32
            y = row * 48
            s_draw.ellipse([x + 8, y + 42, x + 24, y + 46], fill=P_SHADOW_ALPHA)
            s_draw.rectangle([x + 10, y + 24, x + 22, y + 37], fill=P_ZOMBIE_DARK)
            s_draw.rectangle([x + 11, y + 15, x + 20, y + 24], fill=P_ZOMBIE_FLESH)
            if row != 1:
                s_draw.point([x + 13, y + 18], fill=P_ZOMBIE_EYE_R)
                s_draw.point([x + 18, y + 18], fill=P_ZOMBIE_EYE_R)
            if col in [1, 2, 4]:
                s_draw.line([x + 21, y + 28, x + 27, y + 34], fill=P_STEEL_GREY)
    os.makedirs(os.path.dirname(sprinter_path), exist_ok=True)
    s_img.save(sprinter_path)
    print(f"Generated clean infected sheets: {drifter_path}, {sprinter_path}")

if __name__ == "__main__":
    generate_tileset("assets/tilesets/farm_tiles.png")
    generate_farm_props("assets/props/farm_props.png")
    generate_archi_spritesheet("assets/characters/archi/archi_spritesheet.png")
    generate_danish_spritesheet("assets/characters/danish/danish_spritesheet.png")
    generate_infected_sheets(
        "assets/characters/infected/drifter_spritesheet.png",
        "assets/characters/infected/sprinter_spritesheet.png"
    )
    print("Master pixel assets generated successfully!")
