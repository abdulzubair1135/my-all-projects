"""
Procedural Pixel Art Asset Generator for Evergreen: After the Fall
Generates authentic 32x32 and 32x48 pixel-art sprites, tiles, props, and UI.
"""
import os
import math
from PIL import Image, ImageDraw

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def make_icon():
    img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Background circle
    draw.ellipse([4, 4, 123, 123], fill=hex_to_rgb("#1e3f20"), outline=hex_to_rgb("#e0a944"), width=4)
    # Sunset sky gradient in upper half
    for y in range(8, 64):
        t = (y - 8) / 56.0
        r = int(220 * (1 - t) + 240 * t)
        g = int(140 * (1 - t) + 180 * t)
        b = int(70 * (1 - t) + 90 * t)
        draw.line([(24, y), (103, y)], fill=(r, g, b, 255))
    # Sun
    draw.ellipse([48, 28, 79, 59], fill=hex_to_rgb("#ffea75"))
    # Mountains
    draw.polygon([(16, 80), (52, 44), (78, 80)], fill=hex_to_rgb("#3a5948"))
    draw.polygon([(56, 80), (84, 52), (112, 80)], fill=hex_to_rgb("#2d4838"))
    # Big Evergreen Pine Tree in front
    # Trunk
    draw.rectangle([60, 80, 67, 108], fill=hex_to_rgb("#4a2c16"))
    # Pine layers
    draw.polygon([(64, 46), (42, 70), (86, 70)], fill=hex_to_rgb("#1c6b32"))
    draw.polygon([(64, 58), (36, 86), (92, 86)], fill=hex_to_rgb("#145224"))
    draw.polygon([(64, 72), (30, 102), (98, 102)], fill=hex_to_rgb("#0e3d1a"))
    # Golden border glow
    draw.ellipse([2, 2, 125, 125], outline=hex_to_rgb("#ffd369"), width=2)
    os.makedirs("assets/ui", exist_ok=True)
    img.save("assets/ui/icon.png")
    print("Created assets/ui/icon.png")

def make_tileset():
    # 8 columns x 4 rows of 32x32 tiles => 256 x 128 px
    img = Image.new('RGBA', (256, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Palette
    c_grass_base = hex_to_rgb("#4b8f36")
    c_grass_dark = hex_to_rgb("#3c732b")
    c_grass_light = hex_to_rgb("#5fa845")
    c_grass_blade = hex_to_rgb("#72bf54")
    c_flower_white = hex_to_rgb("#ffffff")
    c_flower_yellow = hex_to_rgb("#ffdb4d")
    c_flower_red = hex_to_rgb("#d64040")

    c_soil_dry = hex_to_rgb("#664326")
    c_soil_dark = hex_to_rgb("#4a311c")
    c_soil_ridge = hex_to_rgb("#78502f")
    c_soil_wet = hex_to_rgb("#3d2817")
    c_soil_wet_dark = hex_to_rgb("#281a0f")

    c_path_base = hex_to_rgb("#99856b")
    c_path_light = hex_to_rgb("#ab987e")
    c_path_dark = hex_to_rgb("#7a6750")

    c_wood_base = hex_to_rgb("#85542b")
    c_wood_dark = hex_to_rgb("#633d1c")
    c_wood_light = hex_to_rgb("#a36a38")

    c_stone_base = hex_to_rgb("#6e7378")
    c_stone_dark = hex_to_rgb("#515559")
    c_stone_light = hex_to_rgb("#8c9299")

    c_water_base = hex_to_rgb("#3b7899")
    c_water_dark = hex_to_rgb("#2b5973")
    c_water_light = hex_to_rgb("#539ec7")

    # Tile 0: Plain Grass
    for x in range(32):
        for y in range(32):
            val = ((x * 7 + y * 13) % 17)
            col = c_grass_base
            if val < 3:
                col = c_grass_dark
            elif val > 14:
                col = c_grass_light
            draw.point((x, y), fill=col)
    # Grass tufts
    draw.line([(6, 12), (6, 9)], fill=c_grass_blade)
    draw.line([(7, 12), (8, 10)], fill=c_grass_blade)
    draw.line([(22, 24), (22, 20)], fill=c_grass_blade)
    draw.line([(21, 24), (20, 21)], fill=c_grass_blade)

    # Tile 1: Grass with wildflowers
    for x in range(32):
        for y in range(32):
            val = ((x * 11 + y * 5) % 19)
            col = c_grass_base
            if val < 4:
                col = c_grass_dark
            elif val > 15:
                col = c_grass_light
            draw.point((32 + x, y), fill=col)
    # Flowers
    draw.point((32 + 8, 10), fill=c_flower_white)
    draw.point((32 + 7, 10), fill=c_flower_yellow)
    draw.point((32 + 24, 20), fill=c_flower_red)
    draw.point((32 + 25, 20), fill=c_flower_yellow)
    draw.point((32 + 16, 26), fill=c_flower_white)

    # Tile 2: Tilled Soil (Dry)
    for x in range(32):
        for y in range(32):
            draw.point((64 + x, y), fill=c_soil_dry)
    # Soil furrows
    for furrow_y in [4, 12, 20, 28]:
        for x in range(32):
            draw.point((64 + x, furrow_y - 1), fill=c_soil_ridge)
            draw.point((64 + x, furrow_y), fill=c_soil_dark)
            draw.point((64 + x, furrow_y + 1), fill=c_soil_dark)
            if (x % 4) == 0:
                draw.point((64 + x, furrow_y), fill=c_soil_ridge)

    # Tile 3: Tilled Soil (Watered)
    for x in range(32):
        for y in range(32):
            draw.point((96 + x, y), fill=c_soil_wet)
    for furrow_y in [4, 12, 20, 28]:
        for x in range(32):
            draw.point((96 + x, furrow_y), fill=c_soil_wet_dark)
            draw.point((96 + x, furrow_y + 1), fill=c_soil_wet_dark)
            if (x % 6) == 2:
                draw.point((96 + x, furrow_y - 1), fill=hex_to_rgb("#593b22"))

    # Tile 4: Cobble Stone Path
    for x in range(32):
        for y in range(32):
            draw.point((128 + x, y), fill=c_path_base)
    # Cobble stones
    for r in range(4):
        for c in range(4):
            sx = 128 + c * 8 + (2 if r % 2 == 1 else 0)
            sy = r * 8
            draw.rectangle([sx, sy, sx + 6, sy + 6], fill=c_path_light, outline=c_path_dark)

    # Tile 5: Wood Planks (Floor)
    for x in range(32):
        for y in range(32):
            draw.point((160 + x, y), fill=c_wood_base)
    for py in [0, 8, 16, 24]:
        draw.line([(160, py), (191, py)], fill=c_wood_dark)
        draw.line([(160, py + 1), (191, py + 1)], fill=c_wood_light)
    # Nail heads & seams
    for px in [160 + 8, 160 + 22]:
        for py in [4, 12, 20, 28]:
            draw.point((px, py), fill=c_wood_dark)

    # Tile 6: Stone Brick Wall
    for x in range(32):
        for y in range(32):
            draw.point((192 + x, y), fill=c_stone_base)
    for py in [0, 8, 16, 24]:
        draw.line([(192, py), (223, py)], fill=c_stone_dark)
        draw.line([(192, py + 7), (223, py + 7)], fill=c_stone_light)
    for row in range(4):
        offset = 8 if (row % 2 == 1) else 0
        for col in [8, 16, 24]:
            cx = 192 + (col + offset) % 32
            draw.line([(cx, row * 8), (cx, row * 8 + 7)], fill=c_stone_dark)

    # Tile 7: Water
    for x in range(32):
        for y in range(32):
            wval = math.sin(x * 0.4) + math.cos(y * 0.4)
            col = c_water_base if wval > 0 else c_water_dark
            draw.point((224 + x, y), fill=col)
    # Water ripples
    draw.line([(224 + 6, 8), (224 + 14, 8)], fill=c_water_light)
    draw.line([(224 + 18, 20), (224 + 28, 20)], fill=c_water_light)

    # Row 1: Fences and props
    # Tile 8 (x:0, y:32): Wooden Fence Horizontal
    for x in range(32):
        for y in range(32):
            draw.point((x, 32 + y), fill=(0, 0, 0, 0))
    # Posts on left and right
    draw.rectangle([2, 32 + 8, 7, 32 + 28], fill=c_wood_base, outline=c_wood_dark)
    draw.rectangle([24, 32 + 8, 29, 32 + 28], fill=c_wood_base, outline=c_wood_dark)
    # Rails
    draw.rectangle([0, 32 + 12, 31, 32 + 16], fill=c_wood_base, outline=c_wood_dark)
    draw.rectangle([0, 32 + 22, 31, 32 + 26], fill=c_wood_base, outline=c_wood_dark)

    # Tile 9 (x:32, y:32): Wooden Fence Vertical
    for x in range(32):
        for y in range(32):
            draw.point((32 + x, 32 + y), fill=(0, 0, 0, 0))
    draw.rectangle([32 + 12, 32, 32 + 18, 32 + 31], fill=c_wood_base, outline=c_wood_dark)
    # Post cap
    draw.rectangle([32 + 10, 32 + 4, 32 + 20, 32 + 12], fill=c_wood_light, outline=c_wood_dark)
    draw.rectangle([32 + 10, 32 + 20, 32 + 20, 32 + 28], fill=c_wood_light, outline=c_wood_dark)

    # Tile 10 (x:64, y:32): Dirt Path
    for x in range(32):
        for y in range(32):
            val = ((x * 13 + y * 9) % 11)
            col = hex_to_rgb("#85623e")
            if val < 2:
                col = hex_to_rgb("#705030")
            elif val > 8:
                col = hex_to_rgb("#997249")
            draw.point((64 + x, 32 + y), fill=col)

    # Save tileset
    os.makedirs("assets/tilesets", exist_ok=True)
    img.save("assets/tilesets/farm_tiles.png")
    print("Created assets/tilesets/farm_tiles.png")

def make_character_sheet(name, hair_color, clothes_color, pants_color, skin_color, output_path):
    # 6 columns x 4 rows
    # Columns: Idle 1, Idle 2, Walk 1, Walk 2, Walk 3, Walk 4
    # Rows: 0: Down, 1: Up, 2: Left, 3: Right
    # Frame size: 32 x 48 px => Total sheet: 192 x 192 px
    sheet = Image.new('RGBA', (192, 192), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    c_skin = hex_to_rgb(skin_color)
    c_skin_shadow = (max(0, c_skin[0] - 30), max(0, c_skin[1] - 30), max(0, c_skin[2] - 30))
    c_hair = hex_to_rgb(hair_color)
    c_hair_hi = (min(255, c_hair[0] + 30), min(255, c_hair[1] + 30), min(255, c_hair[2] + 20))
    c_hair_sh = (max(0, c_hair[0] - 35), max(0, c_hair[1] - 35), max(0, c_hair[2] - 35))
    c_cloth = hex_to_rgb(clothes_color)
    c_cloth_sh = (max(0, c_cloth[0] - 30), max(0, c_cloth[1] - 30), max(0, c_cloth[2] - 30))
    c_cloth_hi = (min(255, c_cloth[0] + 25), min(255, c_cloth[1] + 25), min(255, c_cloth[2] + 25))
    c_pants = hex_to_rgb(pants_color)
    c_pants_sh = (max(0, c_pants[0] - 25), max(0, c_pants[1] - 25), max(0, c_pants[2] - 25))
    c_boots = hex_to_rgb("#30241b")
    c_eyes = hex_to_rgb("#241c16")
    c_belt = hex_to_rgb("#664228")
    c_buckle = hex_to_rgb("#d6a74b")

    for dir_idx, direction in enumerate(["down", "up", "left", "right"]):
        row_y = dir_idx * 48
        for frame_idx in range(6):
            col_x = frame_idx * 32
            # Offset for bounce
            bounce = 0
            leg_step = 0
            if frame_idx == 1: # idle 2 (gentle breathing)
                bounce = 0
            elif frame_idx == 2: # walk 1
                bounce = -1
                leg_step = -2
            elif frame_idx == 3: # walk 2
                bounce = 0
                leg_step = 0
            elif frame_idx == 4: # walk 3
                bounce = -1
                leg_step = 2
            elif frame_idx == 5: # walk 4
                bounce = 0
                leg_step = 0

            cx = col_x + 16
            cy = row_y + 24 + bounce

            # Head (center at cx, cy - 10)
            # Legs & feet first (drawn under body)
            foot_y = row_y + 42
            if direction == "down":
                # Left leg, right leg
                draw.rectangle([cx - 5, foot_y - 10, cx - 2, foot_y - 2 + leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx + 2, foot_y - 10, cx + 5, foot_y - 2 - leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx - 6, foot_y - 2 + leg_step, cx - 1, foot_y + leg_step], fill=c_boots)
                draw.rectangle([cx + 1, foot_y - 2 - leg_step, cx + 6, foot_y - leg_step], fill=c_boots)

                # Torso
                draw.rectangle([cx - 6, cy - 4, cx + 6, cy + 8], fill=c_cloth, outline=c_cloth_sh)
                # Collar / Neck
                draw.rectangle([cx - 2, cy - 6, cx + 2, cy - 4], fill=c_skin)
                # Belt
                draw.rectangle([cx - 6, cy + 6, cx + 6, cy + 8], fill=c_belt)
                draw.rectangle([cx - 1, cy + 6, cx + 1, cy + 8], fill=c_buckle)

                # Arms
                draw.rectangle([cx - 8, cy - 3 - leg_step, cx - 6, cy + 4 - leg_step], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx - 8, cy + 5 - leg_step, cx - 6, cy + 7 - leg_step], fill=c_skin)
                draw.rectangle([cx + 6, cy - 3 + leg_step, cx + 8, cy + 4 + leg_step], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx + 6, cy + 5 + leg_step, cx + 8, cy + 7 + leg_step], fill=c_skin)

                # Head
                draw.rectangle([cx - 6, cy - 18, cx + 6, cy - 7], fill=c_skin, outline=c_skin_shadow)
                # Hair
                draw.rectangle([cx - 7, cy - 20, cx + 7, cy - 14], fill=c_hair)
                draw.rectangle([cx - 7, cy - 14, cx - 5, cy - 10], fill=c_hair)
                draw.rectangle([cx + 5, cy - 14, cx + 7, cy - 10], fill=c_hair)
                draw.line([(cx - 4, cy - 19), (cx + 3, cy - 19)], fill=c_hair_hi)
                # Ponytail for Archi
                if name == "Archi":
                    draw.rectangle([cx + 5, cy - 18, cx + 8, cy - 11], fill=c_hair_sh)

                # Face eyes
                draw.point((cx - 3, cy - 11), fill=c_eyes)
                draw.point((cx + 3, cy - 11), fill=c_eyes)
                draw.point((cx, cy - 9), fill=c_skin_shadow) # nose

            elif direction == "up":
                # Legs
                draw.rectangle([cx - 5, foot_y - 10, cx - 2, foot_y - 2 - leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx + 2, foot_y - 10, cx + 5, foot_y - 2 + leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx - 6, foot_y - 2 - leg_step, cx - 1, foot_y - leg_step], fill=c_boots)
                draw.rectangle([cx + 1, foot_y - 2 + leg_step, cx + 6, foot_y + leg_step], fill=c_boots)

                # Torso (back)
                draw.rectangle([cx - 6, cy - 4, cx + 6, cy + 8], fill=c_cloth, outline=c_cloth_sh)
                # Belt back
                draw.rectangle([cx - 6, cy + 6, cx + 6, cy + 8], fill=c_belt)

                # Arms
                draw.rectangle([cx - 8, cy - 3 + leg_step, cx - 6, cy + 5 + leg_step], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx + 6, cy - 3 - leg_step, cx + 8, cy + 5 - leg_step], fill=c_cloth, outline=c_cloth_sh)

                # Head (back hair)
                draw.rectangle([cx - 6, cy - 18, cx + 6, cy - 7], fill=c_hair, outline=c_hair_sh)
                draw.rectangle([cx - 7, cy - 20, cx + 7, cy - 14], fill=c_hair)
                draw.line([(cx - 4, cy - 19), (cx + 3, cy - 19)], fill=c_hair_hi)
                if name == "Archi":
                    # Full ponytail down back
                    draw.rectangle([cx - 2, cy - 13, cx + 2, cy - 3], fill=c_hair_sh)

            elif direction == "left":
                # Legs
                draw.rectangle([cx - 3, foot_y - 10, cx + 2, foot_y - 2 + leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx - 5, foot_y - 2 + leg_step, cx + 2, foot_y + leg_step], fill=c_boots)

                # Torso
                draw.rectangle([cx - 5, cy - 4, cx + 4, cy + 8], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx - 5, cy + 6, cx + 4, cy + 8], fill=c_belt)

                # Arm
                draw.rectangle([cx - 2, cy - 3 - leg_step, cx + 2, cy + 4 - leg_step], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx - 2, cy + 5 - leg_step, cx + 1, cy + 7 - leg_step], fill=c_skin)

                # Head
                draw.rectangle([cx - 5, cy - 18, cx + 5, cy - 7], fill=c_skin, outline=c_skin_shadow)
                draw.rectangle([cx - 4, cy - 20, cx + 6, cy - 14], fill=c_hair)
                draw.rectangle([cx + 2, cy - 14, cx + 6, cy - 9], fill=c_hair)
                if name == "Archi":
                    draw.rectangle([cx + 4, cy - 15, cx + 8, cy - 8], fill=c_hair_sh)
                # Eye
                draw.point((cx - 3, cy - 11), fill=c_eyes)

            elif direction == "right":
                # Legs
                draw.rectangle([cx - 2, foot_y - 10, cx + 3, foot_y - 2 + leg_step], fill=c_pants, outline=c_pants_sh)
                draw.rectangle([cx - 2, foot_y - 2 + leg_step, cx + 5, foot_y + leg_step], fill=c_boots)

                # Torso
                draw.rectangle([cx - 4, cy - 4, cx + 5, cy + 8], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx - 4, cy + 6, cx + 5, cy + 8], fill=c_belt)

                # Arm
                draw.rectangle([cx - 2, cy - 3 - leg_step, cx + 2, cy + 4 - leg_step], fill=c_cloth, outline=c_cloth_sh)
                draw.rectangle([cx - 1, cy + 5 - leg_step, cx + 2, cy + 7 - leg_step], fill=c_skin)

                # Head
                draw.rectangle([cx - 5, cy - 18, cx + 5, cy - 7], fill=c_skin, outline=c_skin_shadow)
                draw.rectangle([cx - 6, cy - 20, cx + 4, cy - 14], fill=c_hair)
                draw.rectangle([cx - 6, cy - 14, cx - 2, cy - 9], fill=c_hair)
                if name == "Archi":
                    draw.rectangle([cx - 8, cy - 15, cx - 4, cy - 8], fill=c_hair_sh)
                # Eye
                draw.point((cx + 3, cy - 11), fill=c_eyes)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sheet.save(output_path)
    print(f"Created {output_path}")

def make_props():
    # Props image: 256 x 256
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Prop 1: Farmhouse (128 x 128 at 0, 0)
    # Timber walls
    c_roof = hex_to_rgb("#85392d")
    c_roof_sh = hex_to_rgb("#66251b")
    c_roof_hi = hex_to_rgb("#a64c3d")
    c_wall = hex_to_rgb("#d6bd94")
    c_beam = hex_to_rgb("#59351e")
    c_stone = hex_to_rgb("#66696b")
    c_glass = hex_to_rgb("#ffd97d") # warm candle glow inside
    c_door = hex_to_rgb("#4a2a16")

    # Stone foundation (y: 100 to 124)
    draw.rectangle([8, 96, 120, 124], fill=c_stone, outline=hex_to_rgb("#47494a"))
    # Walls (y: 48 to 96)
    draw.rectangle([12, 48, 116, 96], fill=c_wall)
    # Vertical and diagonal wooden timber beams
    for bx in [12, 40, 64, 88, 114]:
        draw.rectangle([bx - 2, 48, bx + 2, 96], fill=c_beam)
    draw.rectangle([12, 48, 116, 52], fill=c_beam)
    draw.rectangle([12, 92, 116, 96], fill=c_beam)

    # Windows with warm glow
    # Left window
    draw.rectangle([20, 60, 34, 76], fill=c_glass, outline=c_beam, width=2)
    draw.line([(27, 60), (27, 76)], fill=c_beam)
    draw.line([(20, 68), (34, 68)], fill=c_beam)
    # Right window
    draw.rectangle([94, 60, 108, 76], fill=c_glass, outline=c_beam, width=2)
    draw.line([(101, 60), (101, 76)], fill=c_beam)
    draw.line([(94, 68), (108, 68)], fill=c_beam)

    # Doorway in center
    draw.rectangle([54, 70, 74, 110], fill=c_door, outline=c_beam, width=2)
    draw.point((70, 92), fill=hex_to_rgb("#d4af37")) # brass knob

    # Chimney on right roof
    draw.rectangle([92, 6, 104, 30], fill=c_stone, outline=hex_to_rgb("#47494a"))
    draw.rectangle([90, 4, 106, 8], fill=hex_to_rgb("#7a7d80"))

    # Roof (pitched triangle)
    draw.polygon([(4, 52), (64, 12), (124, 52)], fill=c_roof, outline=c_roof_sh)
    # Shingle rows
    for sy, sx in [(44, 12), (36, 24), (28, 36), (20, 48)]:
        draw.line([(sx, sy), (128 - sx, sy)], fill=c_roof_hi)

    # Prop 2: Water Well (32 x 48 at 136, 0)
    wx, wy = 136, 0
    # Stone well ring
    draw.ellipse([wx + 2, wy + 26, wx + 30, wy + 46], fill=c_stone, outline=hex_to_rgb("#47494a"), width=2)
    draw.ellipse([wx + 6, wy + 30, wx + 26, wy + 42], fill=hex_to_rgb("#2b4a59")) # deep water inside
    # Well roof posts
    draw.rectangle([wx + 3, wy + 10, wx + 6, wy + 32], fill=c_beam)
    draw.rectangle([wx + 26, wy + 10, wx + 29, wy + 32], fill=c_beam)
    # Well wooden roof
    draw.polygon([(wx, wy + 14), (wx + 16, wy + 2), (wx + 32, wy + 14)], fill=c_roof, outline=c_roof_sh)
    # Bucket & rope
    draw.line([(wx + 16, wy + 8), (wx + 16, wy + 26)], fill=hex_to_rgb("#997f63"))
    draw.rectangle([wx + 13, wy + 22, wx + 19, wy + 28], fill=hex_to_rgb("#593e2b"))

    # Prop 3: Wooden Storage Chest (32 x 32 at 176, 0)
    cx, cy = 176, 12
    draw.rectangle([cx + 3, cy + 4, cx + 29, cy + 24], fill=hex_to_rgb("#6e4221"), outline=hex_to_rgb("#3d220e"))
    # Metal reinforcement corners and latch
    draw.rectangle([cx + 3, cy + 4, cx + 6, cy + 24], fill=hex_to_rgb("#858b91"))
    draw.rectangle([cx + 26, cy + 4, cx + 29, cy + 24], fill=hex_to_rgb("#858b91"))
    draw.rectangle([cx + 3, cy + 12, cx + 29, cy + 14], fill=hex_to_rgb("#3d220e"))
    draw.rectangle([cx + 14, cy + 11, cx + 18, cy + 16], fill=hex_to_rgb("#e0a944")) # gold latch

    # Prop 4: Pine Tree (64 x 96 at 136, 56)
    tx, ty = 136, 56
    # Trunk
    draw.rectangle([tx + 27, ty + 60, tx + 37, ty + 94], fill=c_beam, outline=hex_to_rgb("#382012"))
    # Leaves tiers
    c_pine1 = hex_to_rgb("#1e6933")
    c_pine2 = hex_to_rgb("#165227")
    c_pine3 = hex_to_rgb("#0e3d1c")
    draw.polygon([(tx + 32, ty), (tx + 12, ty + 36), (tx + 52, ty + 36)], fill=c_pine1)
    draw.polygon([(tx + 32, ty + 20), (tx + 6, ty + 60), (tx + 58, ty + 60)], fill=c_pine2)
    draw.polygon([(tx + 32, ty + 42), (tx + 2, ty + 82), (tx + 62, ty + 82)], fill=c_pine3)

    os.makedirs("assets/props", exist_ok=True)
    img.save("assets/props/farm_props.png")
    print("Created assets/props/farm_props.png")

def make_portraits():
    # 64 x 64 Archi portrait
    archi = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d_a = ImageDraw.Draw(archi)
    # Warm oval frame background
    d_a.ellipse([2, 2, 61, 61], fill=hex_to_rgb("#233626"), outline=hex_to_rgb("#d4af37"), width=2)
    # Archi skin
    c_skin = hex_to_rgb("#f5cfb0")
    c_skin_sh = hex_to_rgb("#dba785")
    d_a.ellipse([20, 16, 44, 44], fill=c_skin)
    # Neck and collar
    d_a.rectangle([28, 40, 36, 48], fill=c_skin_sh)
    d_a.polygon([(14, 61), (28, 46), (36, 46), (50, 61)], fill=hex_to_rgb("#3e6b41")) # green tunic
    d_a.polygon([(26, 48), (32, 54), (38, 48)], fill=hex_to_rgb("#f5f1e6")) # white undershirt
    # Auburn hair
    c_hair = hex_to_rgb("#964627")
    c_hair_hi = hex_to_rgb("#bf613b")
    d_a.ellipse([17, 10, 47, 30], fill=c_hair)
    d_a.arc([19, 12, 45, 26], start=180, end=360, fill=c_hair_hi, width=2)
    # Ponytail on side
    d_a.ellipse([43, 20, 52, 42], fill=c_hair)
    # Eyes & smile
    d_a.point((26, 28), fill=hex_to_rgb("#291f16"))
    d_a.point((27, 28), fill=hex_to_rgb("#291f16"))
    d_a.point((37, 28), fill=hex_to_rgb("#291f16"))
    d_a.point((38, 28), fill=hex_to_rgb("#291f16"))
    d_a.line([(29, 36), (35, 36)], fill=c_skin_sh) # smile
    d_a.point((32, 32), fill=c_skin_sh) # nose
    archi.save("assets/ui/portrait_archi.png")
    print("Created assets/ui/portrait_archi.png")

    # 64 x 64 Danish portrait
    danish = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d_d = ImageDraw.Draw(danish)
    d_d.ellipse([2, 2, 61, 61], fill=hex_to_rgb("#262936"), outline=hex_to_rgb("#b57c3e"), width=2)
    # Danish skin
    c_skin_d = hex_to_rgb("#e0b999")
    c_skin_d_sh = hex_to_rgb("#ba8e6c")
    d_d.rectangle([21, 18, 43, 44], fill=c_skin_d)
    # Jawline
    d_d.polygon([(21, 38), (32, 46), (43, 38)], fill=c_skin_d)
    # Neck & clothes
    d_d.rectangle([28, 42, 36, 48], fill=c_skin_d_sh)
    d_d.polygon([(12, 61), (26, 47), (38, 47), (52, 61)], fill=hex_to_rgb("#334454")) # navy jacket
    d_d.rectangle([28, 49, 36, 61], fill=hex_to_rgb("#4a3625")) # leather vest collar
    # Short dark hair
    c_hair_d = hex_to_rgb("#292628")
    c_hair_d_hi = hex_to_rgb("#423e42")
    d_d.rectangle([19, 11, 45, 23], fill=c_hair_d)
    d_d.line([(22, 13), (42, 13)], fill=c_hair_d_hi)
    # Stubble
    for sx in [24, 26, 28, 30, 32, 34, 36, 38, 40]:
        d_d.point((sx, 40), fill=c_skin_d_sh)
        d_d.point((sx + 1, 42), fill=c_skin_d_sh)
    # Eyes & determined brow
    d_d.line([(24, 25), (29, 26)], fill=c_hair_d) # left eyebrow
    d_d.line([(35, 26), (40, 25)], fill=c_hair_d) # right eyebrow
    d_d.point((26, 28), fill=hex_to_rgb("#1c1b1c"))
    d_d.point((27, 28), fill=hex_to_rgb("#1c1b1c"))
    d_d.point((37, 28), fill=hex_to_rgb("#1c1b1c"))
    d_d.point((38, 28), fill=hex_to_rgb("#1c1b1c"))
    d_d.line([(28, 37), (36, 37)], fill=hex_to_rgb("#59372a")) # firm mouth
    danish.save("assets/ui/portrait_danish.png")
    print("Created assets/ui/portrait_danish.png")

def make_ui_icons():
    # Sheet for UI icons (64 x 64)
    ui = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui)

    # Health Heart (32 x 32 at 0, 0)
    # Red heart with highlight
    c_heart = hex_to_rgb("#e02d3c")
    c_heart_sh = hex_to_rgb("#991a25")
    c_heart_hi = hex_to_rgb("#ff858f")
    # Left lobe, right lobe, point
    draw.polygon([(16, 24), (6, 14), (6, 9), (10, 6), (15, 8), (16, 10), (17, 8), (22, 6), (26, 9), (26, 14)], fill=c_heart, outline=c_heart_sh)
    draw.point((10, 8), fill=c_heart_hi)
    draw.point((11, 9), fill=c_heart_hi)

    # Stamina Bolt (32 x 32 at 32, 0)
    c_bolt = hex_to_rgb("#ffd024")
    c_bolt_sh = hex_to_rgb("#b88f04")
    c_bolt_hi = hex_to_rgb("#fff099")
    draw.polygon([(48, 6), (38, 16), (44, 16), (40, 26), (54, 14), (47, 14)], fill=c_bolt, outline=c_bolt_sh)
    draw.line([(46, 8), (42, 14)], fill=c_bolt_hi)

    # Clock / Sun icon (32 x 32 at 64, 0)
    draw.ellipse([70, 6, 90, 26], fill=hex_to_rgb("#ffaa00"), outline=hex_to_rgb("#d47800"), width=2)
    draw.ellipse([73, 9, 87, 23], fill=hex_to_rgb("#ffe066"))
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = 80 + int(11 * math.cos(rad))
        y1 = 16 + int(11 * math.sin(rad))
        x2 = 80 + int(14 * math.cos(rad))
        y2 = 16 + int(14 * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=hex_to_rgb("#ffaa00"), width=2)

    # Key prompt "E" (32 x 32 at 96, 0)
    draw.rectangle([98, 6, 122, 26], fill=hex_to_rgb("#ffffff"), outline=hex_to_rgb("#404040"), width=2)
    draw.rectangle([100, 24, 120, 25], fill=hex_to_rgb("#cccccc")) # 3D key button drop
    # Draw letter E
    draw.line([(106, 10), (106, 22)], fill=hex_to_rgb("#222222"), width=2)
    draw.line([(106, 10), (114, 10)], fill=hex_to_rgb("#222222"), width=2)
    draw.line([(106, 16), (112, 16)], fill=hex_to_rgb("#222222"), width=2)
    draw.line([(106, 22), (114, 22)], fill=hex_to_rgb("#222222"), width=2)

    # Quickslot frame (32 x 32 at 0, 32)
    draw.rectangle([1, 33, 30, 62], fill=hex_to_rgb("#282d33"), outline=hex_to_rgb("#5c6673"), width=2)
    draw.rectangle([3, 35, 28, 60], outline=hex_to_rgb("#1b1e21"))

    # Tool Icons: Hoe, Watering Can, Sword
    # Hoe (32 x 32 at 32, 32)
    draw.line([(38, 56), (56, 38)], fill=hex_to_rgb("#7a5230"), width=2)
    draw.polygon([(54, 36), (60, 40), (58, 44), (52, 40)], fill=hex_to_rgb("#879199"))

    # Watering can (32 x 32 at 64, 32)
    draw.rectangle([70, 42, 86, 56], fill=hex_to_rgb("#40758a"), outline=hex_to_rgb("#254857"))
    draw.line([(86, 44), (92, 38)], fill=hex_to_rgb("#40758a"), width=2) # spout
    draw.arc([66, 38, 76, 56], start=90, end=270, fill=hex_to_rgb("#254857"), width=2) # handle

    # Machete / Sword (32 x 32 at 96, 32)
    draw.line([(100, 58), (104, 54)], fill=hex_to_rgb("#573823"), width=3) # grip
    draw.line([(102, 53), (107, 57)], fill=hex_to_rgb("#b08f43"), width=2) # crossguard
    draw.polygon([(104, 52), (120, 36), (122, 38), (106, 54)], fill=hex_to_rgb("#ccd6db")) # blade

    ui.save("assets/ui/ui_elements.png")
    print("Created assets/ui/ui_elements.png")

if __name__ == "__main__":
    make_icon()
    make_tileset()
    # Archi: Auburn hair, green field clothes, tan pants, light skin
    make_character_sheet("Archi", "#964627", "#3e6b41", "#876c4f", "#f5cfb0", "assets/characters/archi/archi_spritesheet.png")
    # Danish: Dark hair, navy jacket, dark denim, tanned skin
    make_character_sheet("Danish", "#292628", "#334454", "#243242", "#e0b999", "assets/characters/danish/danish_spritesheet.png")
    make_props()
    make_portraits()
    make_ui_icons()
    print("All pixel assets generated successfully!")
