import struct
import zlib

def create_png(width, height, pixels, filepath):
    """
    pixels: list of (r, g, b, a) tuples of length width * height
    """
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    raw_lines = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            r, g, b, a = pixels[y * width + x]
            row.extend((r, g, b, a))
        raw_lines.append(bytes(row))
    raw_data = b''.join(raw_lines)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw_data, 9)) + chunk(b'IEND', b'')
    with open(filepath, 'wb') as f:
        f.write(png)

# Palette
CLR_TRANSPARENT = (0, 0, 0, 0)
CLR_OUTLINE     = (22, 20, 28, 255)
CLR_HOOD_SHADOW = (40, 28, 52, 255)
CLR_HOOD_MID    = (68, 46, 84, 255)
CLR_HOOD_LIGHT  = (102, 70, 122, 255)
CLR_SKIN_SHADOW = (168, 124, 102, 255)
CLR_SKIN_MID    = (214, 168, 142, 255)
CLR_SKIN_LIGHT  = (238, 204, 180, 255)
CLR_ARMOR_DARK  = (38, 44, 52, 255)
CLR_ARMOR_MID   = (65, 74, 88, 255)
CLR_ARMOR_LIGHT = (110, 122, 142, 255)
CLR_LEATHER     = (84, 54, 38, 255)
CLR_GOLD        = (198, 150, 48, 255)
CLR_STEEL_DARK  = (90, 96, 108, 255)
CLR_STEEL_LIGHT = (180, 190, 205, 255)
CLR_BOOTS       = (32, 24, 20, 255)

def draw_player_down(frame, is_walking=False):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 1 if (is_walking and (frame == 1 or frame == 3)) else 0
    step_l = -2 if (is_walking and frame == 1) else (1 if (is_walking and frame == 3) else 0)
    step_r = 1 if (is_walking and frame == 1) else (-2 if (is_walking and frame == 3) else 0)

    # Shadow under player
    for sx in range(10, 22):
        set_p(sx, 30, (15, 15, 20, 120))
        set_p(sx, 31, (15, 15, 20, 70))

    # Feet / Boots
    # Left boot
    by_l = 27 + bob + step_l
    for bx in range(11, 14):
        set_p(bx, by_l, CLR_BOOTS)
        set_p(bx, by_l + 1, CLR_BOOTS)
    # Right boot
    by_r = 27 + bob + step_r
    for bx in range(18, 21):
        set_p(bx, by_r, CLR_BOOTS)
        set_p(bx, by_r + 1, CLR_BOOTS)

    # Legs / Pants
    for y in range(24 + bob, 27 + bob):
        for x in range(12, 15):
            set_p(x, y, CLR_ARMOR_DARK)
        for x in range(17, 20):
            set_p(x, y, CLR_ARMOR_DARK)

    # Cloak & Tunic Body
    for y in range(14 + bob, 25 + bob):
        for x in range(9, 23):
            # Outline border
            if x == 9 or x == 22 or y == 24 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif 12 <= x <= 19 and 15 + bob <= y <= 21 + bob:
                # Breastplate
                if y == 15 + bob or y == 16 + bob:
                    set_p(x, y, CLR_ARMOR_LIGHT if x in (13, 14, 17, 18) else CLR_ARMOR_MID)
                elif y == 21 + bob:
                    set_p(x, y, CLR_GOLD if 14 <= x <= 17 else CLR_LEATHER) # Belt
                else:
                    set_p(x, y, CLR_ARMOR_MID if 14 <= x <= 17 else CLR_ARMOR_DARK)
            else:
                # Cloak sides
                set_p(x, y, CLR_HOOD_LIGHT if (x == 10 or x == 21) else CLR_HOOD_MID)

    # Broken Sword on hip (left side)
    set_p(8, 19 + bob, CLR_LEATHER)
    set_p(8, 20 + bob, CLR_GOLD)
    set_p(8, 21 + bob, CLR_STEEL_DARK)
    set_p(8, 22 + bob, CLR_STEEL_LIGHT)

    # Hood & Head
    hy = 5 + bob
    # Outline
    for y in range(hy, hy + 10):
        for x in range(10, 22):
            if (x in (10, 21) and hy + 1 <= y <= hy + 8) or (y == hy and 12 <= x <= 19):
                set_p(x, y, CLR_OUTLINE)
            elif hy + 1 <= y <= hy + 9 and 11 <= x <= 20:
                set_p(x, y, CLR_HOOD_MID)
                if y == hy + 1 or x == 11:
                    set_p(x, y, CLR_HOOD_LIGHT)

    # Face cutout inside hood
    for y in range(hy + 3, hy + 8):
        for x in range(13, 19):
            set_p(x, y, CLR_SKIN_MID)
            if y == hy + 3:
                set_p(x, y, CLR_HOOD_SHADOW) # Hood shadow over forehead
            elif y == hy + 5 and x in (14, 17):
                set_p(x, y, CLR_OUTLINE) # Eyes
            elif y == hy + 7 and 15 <= x <= 16:
                set_p(x, y, CLR_SKIN_SHADOW) # Mouth/chin shadow

    return canvas

def draw_player_up(frame, is_walking=False):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 1 if (is_walking and (frame == 1 or frame == 3)) else 0
    step_l = -2 if (is_walking and frame == 1) else (1 if (is_walking and frame == 3) else 0)
    step_r = 1 if (is_walking and frame == 1) else (-2 if (is_walking and frame == 3) else 0)

    # Shadow
    for sx in range(10, 22):
        set_p(sx, 30, (15, 15, 20, 120))
        set_p(sx, 31, (15, 15, 20, 70))

    # Feet
    by_l = 27 + bob + step_l
    for bx in range(11, 14):
        set_p(bx, by_l, CLR_BOOTS)
        set_p(bx, by_l + 1, CLR_BOOTS)
    by_r = 27 + bob + step_r
    for bx in range(18, 21):
        set_p(bx, by_r, CLR_BOOTS)
        set_p(bx, by_r + 1, CLR_BOOTS)

    # Cloak back (covers entire back)
    for y in range(13 + bob, 26 + bob):
        for x in range(9, 23):
            if x == 9 or x == 22 or y == 25 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif 13 <= x <= 18:
                set_p(x, y, CLR_HOOD_MID)
            else:
                set_p(x, y, CLR_HOOD_SHADOW)

    # Sword scabbard strap across back
    for i in range(7):
        set_p(11 + i, 16 + bob + i, CLR_LEATHER)

    # Hood back
    hy = 5 + bob
    for y in range(hy, hy + 9):
        for x in range(10, 22):
            if (x in (10, 21) and hy + 1 <= y <= hy + 7) or (y == hy and 12 <= x <= 19):
                set_p(x, y, CLR_OUTLINE)
            elif 11 <= x <= 20:
                if y == hy + 1 or x in (11, 12):
                    set_p(x, y, CLR_HOOD_LIGHT)
                else:
                    set_p(x, y, CLR_HOOD_MID)

    return canvas

def draw_player_side(frame, is_walking=False):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 1 if (is_walking and (frame == 1 or frame == 3)) else 0
    step_front = -2 if (is_walking and frame == 1) else (2 if (is_walking and frame == 3) else 0)
    step_back  = 2 if (is_walking and frame == 1) else (-2 if (is_walking and frame == 3) else 0)

    # Shadow
    for sx in range(10, 22):
        set_p(sx, 30, (15, 15, 20, 120))
        set_p(sx, 31, (15, 15, 20, 70))

    # Feet
    for bx in range(15 + step_front, 19 + step_front):
        set_p(bx, 27 + bob, CLR_BOOTS)
        set_p(bx, 28 + bob, CLR_BOOTS)
    for bx in range(11 + step_back, 15 + step_back):
        set_p(bx, 27 + bob, CLR_BOOTS)
        set_p(bx, 28 + bob, CLR_BOOTS)

    # Legs
    for y in range(24 + bob, 27 + bob):
        for x in range(13, 18):
            set_p(x, y, CLR_ARMOR_DARK)

    # Torso & Cloak
    for y in range(14 + bob, 25 + bob):
        for x in range(9, 21):
            if x == 9 or x == 20 or y == 24 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif x <= 13:
                set_p(x, y, CLR_HOOD_MID) # Cape trailing back
            elif 14 <= x <= 18:
                if y == 21 + bob:
                    set_p(x, y, CLR_LEATHER) # Belt
                else:
                    set_p(x, y, CLR_ARMOR_MID)
            else:
                set_p(x, y, CLR_ARMOR_LIGHT)

    # Broken sword hanging at side
    for sy in range(18 + bob, 24 + bob):
        set_p(12, sy, CLR_STEEL_LIGHT if sy > 20 + bob else CLR_GOLD)

    # Hood & Profile
    hy = 5 + bob
    for y in range(hy, hy + 9):
        for x in range(11, 22):
            if y == hy and 13 <= x <= 19:
                set_p(x, y, CLR_OUTLINE)
            elif x == 11 or (x == 21 and y >= hy + 4):
                set_p(x, y, CLR_OUTLINE)
            elif 12 <= x <= 17:
                set_p(x, y, CLR_HOOD_LIGHT if y <= hy + 2 else CLR_HOOD_MID)
            elif 18 <= x <= 20 and hy + 3 <= y <= hy + 7:
                # Face profile
                if y == hy + 4 and x == 19:
                    set_p(x, y, CLR_OUTLINE) # Eye
                elif y == hy + 3:
                    set_p(x, y, CLR_HOOD_SHADOW)
                else:
                    set_p(x, y, CLR_SKIN_MID)

    return canvas

CLR_SLASH_WHITE = (245, 248, 255, 255)
CLR_SLASH_CYAN  = (170, 215, 250, 240)
CLR_SLASH_GOLD  = (255, 210, 90, 255)
CLR_HURT_FLASH  = (255, 120, 120, 255)

def draw_player_attack_down(frame):
    canvas = draw_player_down(0, is_walking=False)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    if frame == 1: # Slash strike
        for x in range(6, 26):
            set_p(x, 24, CLR_SLASH_WHITE)
            set_p(x, 25, CLR_SLASH_CYAN)
        set_p(25, 23, CLR_SLASH_WHITE)
        set_p(26, 22, CLR_SLASH_CYAN)
    elif frame == 2: # Recovery
        for x in range(10, 22):
            set_p(x, 26, CLR_SLASH_CYAN)
    return canvas

def draw_player_attack_up(frame):
    canvas = draw_player_up(0, is_walking=False)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    if frame == 1:
        for x in range(6, 26):
            set_p(x, 4, CLR_SLASH_WHITE)
            set_p(x, 3, CLR_SLASH_CYAN)
    elif frame == 2:
        for x in range(10, 22):
            set_p(x, 5, CLR_SLASH_CYAN)
    return canvas

def draw_player_attack_side(frame):
    canvas = draw_player_side(0, is_walking=False)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    if frame == 1: # Slash arc forward
        for y in range(10, 26):
            set_p(25, y, CLR_SLASH_WHITE)
            set_p(26, y, CLR_SLASH_CYAN)
        for x in range(21, 26):
            set_p(x, 18, CLR_SLASH_WHITE)
    elif frame == 2:
        for y in range(14, 24):
            set_p(27, y, CLR_SLASH_CYAN)
    return canvas

def draw_player_heavy_down(frame):
    canvas = draw_player_down(0, is_walking=False)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    if frame == 0: # Raise weapon overhead
        for y in range(2, 8):
            set_p(15, y, CLR_GOLD if y > 5 else CLR_STEEL_LIGHT)
            set_p(16, y, CLR_STEEL_LIGHT)
    elif frame == 1 or frame == 2: # Heavy Impact
        for x in range(4, 28):
            set_p(x, 26, CLR_SLASH_GOLD)
            set_p(x, 27, CLR_SLASH_WHITE)
            if x % 3 == 0:
                set_p(x, 25, CLR_SLASH_GOLD)
    return canvas

def draw_player_heavy_side(frame):
    canvas = draw_player_side(0, is_walking=False)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    if frame == 0:
        for y in range(6, 14):
            set_p(6, y, CLR_STEEL_LIGHT)
    elif frame == 1 or frame == 2:
        for y in range(6, 28):
            set_p(26, y, CLR_SLASH_GOLD)
            set_p(27, y, CLR_SLASH_WHITE)
    return canvas

def draw_player_dodge(frame):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    # Dust trail and rolled body
    oy = 14 + (2 if frame in (1, 2) else 0)
    for y in range(oy, oy + 12):
        for x in range(8 + frame * 3, 20 + frame * 3):
            if x < 31 and y < 31:
                set_p(x, y, CLR_HOOD_MID)
    # Ghost trail
    for tx in range(2, 10):
        set_p(tx, 27, (140, 160, 190, 100))
    return canvas

def draw_player_hurt(frame):
    canvas = draw_player_down(0, is_walking=False)
    # Tint reddish
    for i in range(len(canvas)):
        if canvas[i][3] > 0:
            r, g, b, a = canvas[i]
            canvas[i] = (min(255, r + 100), max(0, g - 40), max(0, b - 40), a)
    return canvas

def draw_player_death(frame):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    # Collapsed on ground
    for y in range(23, 29):
        for x in range(6, 26):
            if y == 28:
                set_p(x, y, CLR_OUTLINE)
            elif x in (6, 25):
                set_p(x, y, CLR_OUTLINE)
            elif x <= 14:
                set_p(x, y, CLR_HOOD_MID)
            else:
                set_p(x, y, CLR_ARMOR_DARK)
    # Fallen sword
    for x in range(21, 27):
        set_p(x, 29, CLR_STEEL_LIGHT if x < 25 else CLR_GOLD)
    return canvas

def generate_player_spritesheet():
    sheet_w, sheet_h = 128, 416 # 4 cols x 13 rows of 32x32
    full_pixels = [CLR_TRANSPARENT] * (sheet_w * sheet_h)

    def blit(frame_canvas, col, row):
        ox = col * 32
        oy = row * 32
        for y in range(32):
            for x in range(32):
                full_pixels[(oy + y) * sheet_w + (ox + x)] = frame_canvas[y * 32 + x]

    # Row 0: Idle Down
    for f in range(4): blit(draw_player_down(f, False), f, 0)
    # Row 1: Idle Up
    for f in range(4): blit(draw_player_up(f, False), f, 1)
    # Row 2: Idle Side
    for f in range(4): blit(draw_player_side(f, False), f, 2)
    # Row 3: Walk Down
    for f in range(4): blit(draw_player_down(f, True), f, 3)
    # Row 4: Walk Up
    for f in range(4): blit(draw_player_up(f, True), f, 4)
    # Row 5: Walk Side
    for f in range(4): blit(draw_player_side(f, True), f, 5)
    # Row 6: Attack Down
    for f in range(4): blit(draw_player_attack_down(f), f, 6)
    # Row 7: Attack Up
    for f in range(4): blit(draw_player_attack_up(f), f, 7)
    # Row 8: Attack Side
    for f in range(4): blit(draw_player_attack_side(f), f, 8)
    # Row 9: Heavy Down
    for f in range(4): blit(draw_player_heavy_down(f), f, 9)
    # Row 10: Heavy Side
    for f in range(4): blit(draw_player_heavy_side(f), f, 10)
    # Row 11: Dodge
    for f in range(4): blit(draw_player_dodge(f), f, 11)
    # Row 12: Hurt (0,1) & Death (2,3)
    blit(draw_player_hurt(0), 0, 12)
    blit(draw_player_hurt(1), 1, 12)
    blit(draw_player_death(0), 2, 12)
    blit(draw_player_death(1), 3, 12)

    create_png(sheet_w, sheet_h, full_pixels, "assets/characters/player_placeholder.png")
    print("Generated assets/characters/player_placeholder.png (128x416)")

# --- ZOMBIE ASSETS ---
CLR_ZOMBIE_FLESH_DARK = (45, 62, 45, 255)
CLR_ZOMBIE_FLESH_MID  = (72, 95, 68, 255)
CLR_ZOMBIE_FLESH_LGT  = (108, 138, 102, 255)
CLR_ZOMBIE_EYE_RED    = (210, 40, 40, 255)
CLR_ZOMBIE_RAGS_DARK  = (40, 36, 42, 255)
CLR_ZOMBIE_RAGS_MID   = (65, 58, 68, 255)

def draw_zombie(frame, action="idle"):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 1 if (action == "walk" and frame % 2 == 1) else 0
    lunge = 3 if (action == "attack" and frame in (1, 2)) else 0

    # Shadow
    for sx in range(10, 22):
        set_p(sx, 30, (10, 15, 10, 100))

    # Feet
    for bx in range(11, 14):
        set_p(bx, 27 + bob, CLR_BOOTS)
    for bx in range(18, 21):
        set_p(bx, 27 + bob, CLR_BOOTS)

    # Legs & Rags
    for y in range(23 + bob, 27 + bob):
        for x in range(11, 21):
            set_p(x, y, CLR_ZOMBIE_RAGS_DARK)

    # Torso (decayed, ribs visible)
    for y in range(14 + bob, 24 + bob):
        for x in range(10, 22):
            if x == 10 or x == 21 or y == 23 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif x in (13, 14, 17, 18) and y in (16 + bob, 18 + bob):
                set_p(x, y, CLR_ZOMBIE_FLESH_LGT) # Exposed bone/rib
            else:
                set_p(x, y, CLR_ZOMBIE_RAGS_MID)

    # Arms / Claws reaching forward
    if action == "attack" and frame in (1, 2):
        for ax in range(7, 25):
            set_p(ax, 19 + bob + lunge, CLR_ZOMBIE_FLESH_MID)
            set_p(ax, 20 + bob + lunge, CLR_ZOMBIE_FLESH_LGT)
        # Claw tips
        set_p(6, 19 + bob + lunge, CLR_OUTLINE)
        set_p(25, 19 + bob + lunge, CLR_OUTLINE)
    else:
        for y in range(16 + bob, 22 + bob):
            set_p(9, y, CLR_ZOMBIE_FLESH_MID)
            set_p(22, y, CLR_ZOMBIE_FLESH_MID)

    # Head (hunched forward)
    hy = 6 + bob + (1 if action == "walk" else 0)
    for y in range(hy, hy + 9):
        for x in range(11, 21):
            if y == hy or x == 11 or x == 20:
                set_p(x, y, CLR_OUTLINE)
            else:
                set_p(x, y, CLR_ZOMBIE_FLESH_MID)

    # Glowing red plague eyes
    set_p(13, hy + 4, CLR_ZOMBIE_EYE_RED)
    set_p(18, hy + 4, CLR_ZOMBIE_EYE_RED)

    # Hurt tint
    if action == "hurt":
        for i in range(len(canvas)):
            if canvas[i][3] > 0:
                r, g, b, a = canvas[i]
                canvas[i] = (min(255, r + 130), max(0, g - 20), max(0, b - 20), a)

    # Death collapse
    if action == "death":
        canvas = [CLR_TRANSPARENT] * (32 * 32)
        for y in range(25, 30):
            for x in range(8, 24):
                if y == 29 or x in (8, 23):
                    set_p(x, y, CLR_OUTLINE)
                else:
                    set_p(x, y, CLR_ZOMBIE_FLESH_DARK if (x + y) % 2 == 0 else CLR_ZOMBIE_RAGS_DARK)

    return canvas

def generate_zombie_spritesheet():
    sheet_w, sheet_h = 128, 160 # 4 cols x 5 rows
    full_pixels = [CLR_TRANSPARENT] * (sheet_w * sheet_h)

    def blit(frame_canvas, col, row):
        ox = col * 32
        oy = row * 32
        for y in range(32):
            for x in range(32):
                full_pixels[(oy + y) * sheet_w + (ox + x)] = frame_canvas[y * 32 + x]

    # Row 0: Idle (4 frames)
    for f in range(4): blit(draw_zombie(f, "idle"), f, 0)
    # Row 1: Walk / Chase (4 frames)
    for f in range(4): blit(draw_zombie(f, "walk"), f, 1)
    # Row 2: Attack Claw (4 frames)
    for f in range(4): blit(draw_zombie(f, "attack"), f, 2)
    # Row 3: Hurt (4 frames)
    for f in range(4): blit(draw_zombie(f, "hurt"), f, 3)
    # Row 4: Death (4 frames)
    for f in range(4): blit(draw_zombie(f, "death"), f, 4)

    create_png(sheet_w, sheet_h, full_pixels, "assets/enemies/zombie_training.png")
    print("Generated assets/enemies/zombie_training.png (128x160)")

def generate_tiles():
    # 4 columns x 2 rows of 32x32 = 128 x 64 px
    sheet_w, sheet_h = 128, 64
    pixels = [CLR_TRANSPARENT] * (sheet_w * sheet_h)

    def blit_tile(tile_pixels, col, row):
        ox = col * 32
        oy = row * 32
        for y in range(32):
            for x in range(32):
                pixels[(oy + y) * sheet_w + (ox + x)] = tile_pixels[y * 32 + x]

    # Tile (0, 0): Corrupted dark earth & dead moss
    earth = []
    for y in range(32):
        for x in range(32):
            # subtle texture variation
            v = ((x * 7 + y * 13) % 17)
            if (x + y) % 9 == 0 or (x * 3 + y * 5) % 23 == 0:
                earth.append((42, 54, 38, 255)) # dead moss speck
            elif v < 4:
                earth.append((24, 28, 24, 255))
            elif v < 12:
                earth.append((32, 38, 30, 255))
            else:
                earth.append((38, 46, 36, 255))
    blit_tile(earth, 0, 0)

    # Tile (1, 0): Ruined stone floor flagstone
    stone = []
    for y in range(32):
        for x in range(32):
            # mortar / crack lines at x=15 and y=15
            is_mortar = (x == 15 or y == 15 or x == 31 or y == 31 or ((x - 8) == (y - 8) and 10 <= x <= 14))
            if is_mortar:
                stone.append((24, 26, 36, 255))
            else:
                h = ((x * 11 + y * 17) % 7)
                if h == 0:
                    stone.append((70, 75, 95, 255)) # subtle highlight
                elif h < 4:
                    stone.append((54, 58, 76, 255))
                else:
                    stone.append((44, 48, 64, 255))
    blit_tile(stone, 1, 0)

    # Tile (2, 0): Rubble / dirt path
    path = []
    for y in range(32):
        for x in range(32):
            r = ((x * 19 + y * 23) % 11)
            if r < 2:
                path.append((68, 50, 36, 255))
            elif r < 6:
                path.append((52, 38, 28, 255))
            else:
                path.append((40, 28, 20, 255))
    blit_tile(path, 2, 0)

    # Tile (3, 0): Dark corrupted water / puddle
    water = []
    for y in range(32):
        for x in range(32):
            w = ((x * 5 + y * 9) % 8)
            if w == 0:
                water.append((28, 48, 56, 255))
            else:
                water.append((16, 28, 36, 255))
    blit_tile(water, 3, 0)

    # Tile (0, 1): Ruined stone wall (solid stone masonry)
    wall = []
    for y in range(32):
        for x in range(32):
            if y < 6: # wall top edge
                wall.append((88, 96, 118, 255) if (x % 6 != 0) else (40, 44, 58, 255))
            elif y == 6 or y == 19 or y == 31 or x == 0 or x == 31: # mortar lines
                wall.append((22, 24, 34, 255))
            elif (y < 19 and (x == 16)) or (y >= 19 and (x == 8 or x == 24)):
                wall.append((22, 24, 34, 255))
            else:
                s = ((x * 13 + y * 7) % 9)
                if s == 0:
                    wall.append((74, 82, 102, 255))
                elif s < 4:
                    wall.append((56, 62, 78, 255))
                else:
                    wall.append((44, 48, 62, 255))
    blit_tile(wall, 0, 1)

    # Tile (1, 1): Ruined stone pillar / altar
    pillar = [CLR_TRANSPARENT] * (32 * 32)
    def set_pil(px, py, c):
        if 0 <= px < 32 and 0 <= py < 32:
            pillar[py * 32 + px] = c
    for py in range(4, 28):
        for px in range(6, 26):
            if px in (6, 25) or py in (4, 27):
                set_pil(px, py, (22, 24, 34, 255))
            elif py in (5, 6, 25, 26):
                set_pil(px, py, (92, 100, 120, 255) if px in (7, 8, 23, 24) else (64, 70, 88, 255))
            else:
                # Carving / center emblem
                if (13 <= px <= 18) and (13 <= py <= 18):
                    set_pil(px, py, (130, 60, 50, 255) if px == 15 or py == 15 else (70, 40, 40, 255))
                else:
                    set_pil(px, py, (50, 56, 72, 255))
    # Shadow under pillar
    for sx in range(4, 28):
        set_pil(sx, 29, (15, 15, 20, 120))
        set_pil(sx, 30, (15, 15, 20, 70))
    blit_tile(pillar, 1, 1)

    # Tile (2, 1): Ruined wooden barricade
    wood = [CLR_TRANSPARENT] * (32 * 32)
    def set_wood(px, py, c):
        if 0 <= px < 32 and 0 <= py < 32:
            wood[py * 32 + px] = c
    for py in range(8, 28):
        for px in range(4, 28):
            # Planks angled
            if (px + py) % 7 in (0, 1):
                set_wood(px, py, (30, 20, 14, 255))
            elif (px + py) % 7 in (2, 3):
                set_wood(px, py, (78, 52, 34, 255))
            else:
                set_wood(px, py, (58, 38, 24, 255))
    # Iron nails
    for nx, ny in [(8, 12), (22, 14), (10, 22), (24, 24)]:
        set_wood(nx, ny, (140, 145, 155, 255))
        set_wood(nx + 1, ny, (30, 30, 35, 255))
    blit_tile(wood, 2, 1)

    # Tile (3, 1): Torch / Brazier on stone stand
    brazier = [CLR_TRANSPARENT] * (32 * 32)
    def set_brz(px, py, c):
        if 0 <= px < 32 and 0 <= py < 32:
            brazier[py * 32 + px] = c
    # Stone pedestal
    for py in range(18, 28):
        for px in range(10, 22):
            if px in (10, 21) or py in (18, 27):
                set_brz(px, py, (22, 24, 34, 255))
            else:
                set_brz(px, py, (55, 60, 75, 255))
    # Iron bowl
    for px in range(7, 25):
        set_brz(px, 16, (30, 32, 40, 255))
        set_brz(px, 17, (45, 48, 60, 255))
    # Fire flame
    for fy in range(7, 16):
        for fx in range(11, 21):
            dist = abs(fx - 15.5) + (16 - fy) * 0.7
            if dist < 2.5:
                set_brz(fx, fy, (255, 220, 100, 255)) # bright yellow center
            elif dist < 4.2:
                set_brz(fx, fy, (240, 130, 40, 255)) # orange flame
            elif dist < 5.8:
                set_brz(fx, fy, (180, 50, 20, 255)) # ember edge
    blit_tile(brazier, 3, 1)

    create_png(sheet_w, sheet_h, pixels, "assets/tiles/test_tiles.png")
    print("Generated assets/tiles/test_tiles.png (128x64)")

if __name__ == "__main__":
    generate_player_spritesheet()
    generate_zombie_spritesheet()
    generate_tiles()
