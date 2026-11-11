import struct
import zlib

def create_png(width, height, pixels, filepath):
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

CLR_TRANSPARENT = (0, 0, 0, 0)
CLR_OUTLINE     = (22, 20, 28, 255)

# --- RUNNER COLORS (feral, bloodied, rapid) ---
CLR_RUNNER_FLESH = (85, 35, 35, 255)
CLR_RUNNER_SINEW = (130, 48, 48, 255)
CLR_RUNNER_EYE   = (255, 30, 30, 255)
CLR_RUNNER_CLAW  = (220, 190, 190, 255)

def draw_runner(frame, action="idle"):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 2 if (action == "walk" and frame % 2 == 1) else 0
    lunge = 4 if (action == "attack" and frame in (1, 2)) else 0

    # Shadow
    for sx in range(10, 22):
        set_p(sx, 30, (15, 5, 5, 100))

    # Feet (elongated claws)
    for bx in range(10, 13):
        set_p(bx, 28 + bob, CLR_RUNNER_FLESH)
    for bx in range(19, 22):
        set_p(bx, 28 + bob, CLR_RUNNER_FLESH)

    # Legs (crouched, agile)
    for y in range(23 + bob, 28 + bob):
        for x in range(11, 21):
            set_p(x, y, CLR_RUNNER_FLESH)

    # Arched Torso
    for y in range(15 + bob, 24 + bob):
        for x in range(11, 21):
            if x == 11 or x == 20 or y == 23 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif y in (17 + bob, 19 + bob):
                set_p(x, y, CLR_RUNNER_SINEW)
            else:
                set_p(x, y, CLR_RUNNER_FLESH)

    # Extended Feral Claws
    if action == "attack" and frame in (1, 2):
        for ax in range(5, 27):
            set_p(ax, 18 + bob + lunge, CLR_RUNNER_SINEW)
        set_p(4, 18 + bob + lunge, CLR_RUNNER_CLAW)
        set_p(27, 18 + bob + lunge, CLR_RUNNER_CLAW)
    else:
        for y in range(17 + bob, 24 + bob):
            set_p(8, y, CLR_RUNNER_SINEW)
            set_p(23, y, CLR_RUNNER_SINEW)

    # Feral Head
    hy = 8 + bob
    for y in range(hy, hy + 8):
        for x in range(12, 20):
            if y == hy or x == 12 or x == 19:
                set_p(x, y, CLR_OUTLINE)
            else:
                set_p(x, y, CLR_RUNNER_FLESH)
    # Glowing predatory eyes
    set_p(14, hy + 3, CLR_RUNNER_EYE)
    set_p(17, hy + 3, CLR_RUNNER_EYE)

    if action == "hurt":
        for i in range(len(canvas)):
            if canvas[i][3] > 0:
                r, g, b, a = canvas[i]
                canvas[i] = (min(255, r + 140), max(0, g - 20), max(0, b - 20), a)

    if action == "death":
        canvas = [CLR_TRANSPARENT] * (32 * 32)
        for y in range(26, 30):
            for x in range(8, 24):
                set_p(x, y, CLR_RUNNER_FLESH if y < 29 else CLR_OUTLINE)

    return canvas

# --- ROYAL ZOMBIE COLORS (faded royal violet, steel plate, sword) ---
CLR_ROYAL_PURPLE = (75, 32, 85, 255)
CLR_ROYAL_GOLD   = (175, 135, 45, 255)
CLR_ROYAL_STEEL  = (105, 115, 130, 255)
CLR_ROYAL_DARK   = (45, 48, 58, 255)
CLR_ROYAL_FLESH  = (60, 75, 65, 255)

def draw_royal_zombie(frame, action="idle"):
    canvas = [CLR_TRANSPARENT] * (32 * 32)
    def set_p(x, y, color):
        if 0 <= x < 32 and 0 <= y < 32:
            canvas[y * 32 + x] = color

    bob = 1 if (action == "walk" and frame % 2 == 1) else 0

    # Shadow
    for sx in range(8, 24):
        set_p(sx, 30, (15, 15, 20, 130))

    # Armored Boots
    for bx in range(10, 14):
        set_p(bx, 27 + bob, CLR_ROYAL_STEEL)
        set_p(bx, 28 + bob, CLR_ROYAL_DARK)
    for bx in range(18, 22):
        set_p(bx, 27 + bob, CLR_ROYAL_STEEL)
        set_p(bx, 28 + bob, CLR_ROYAL_DARK)

    # Greaves / Legs
    for y in range(23 + bob, 27 + bob):
        for x in range(11, 21):
            set_p(x, y, CLR_ROYAL_DARK)

    # Royal Breastplate & Surcoat
    for y in range(13 + bob, 24 + bob):
        for x in range(9, 23):
            if x == 9 or x == 22 or y == 23 + bob:
                set_p(x, y, CLR_OUTLINE)
            elif 12 <= x <= 19 and 14 + bob <= y <= 20 + bob:
                set_p(x, y, CLR_ROYAL_STEEL if y <= 17 + bob else CLR_ROYAL_PURPLE)
                # Crest gold emblem
                if (x in (15, 16) and y in (16 + bob, 17 + bob)):
                    set_p(x, y, CLR_ROYAL_GOLD)
            else:
                set_p(x, y, CLR_ROYAL_PURPLE)

    # Broken Royal Sword in Hand
    if action == "attack" and frame in (1, 2):
        # Big horizontal / overhead cleave with royal blade
        for x in range(16, 31):
            set_p(x, 15 + bob, CLR_ROYAL_STEEL)
            set_p(x, 16 + bob, CLR_ROYAL_GOLD if x < 20 else (240, 245, 255, 255))
    else:
        # Sword held pointing downward
        for sy in range(16 + bob, 27 + bob):
            set_p(23, sy, CLR_ROYAL_GOLD if sy < 19 + bob else CLR_ROYAL_STEEL)

    # Corrupted Guard Helm / Head
    hy = 4 + bob
    for y in range(hy, hy + 9):
        for x in range(10, 22):
            if y == hy or x == 10 or x == 21:
                set_p(x, y, CLR_OUTLINE)
            elif 13 <= x <= 18 and y == hy + 4:
                set_p(x, y, (180, 40, 40, 255)) # Visor slit with red glowing eyes
            else:
                set_p(x, y, CLR_ROYAL_STEEL)

    if action == "hurt":
        for i in range(len(canvas)):
            if canvas[i][3] > 0:
                r, g, b, a = canvas[i]
                canvas[i] = (min(255, r + 130), max(0, g - 20), max(0, b - 20), a)

    if action == "death":
        canvas = [CLR_TRANSPARENT] * (32 * 32)
        for y in range(24, 30):
            for x in range(7, 25):
                set_p(x, y, CLR_ROYAL_STEEL if y < 29 else CLR_OUTLINE)
        # Fallen royal blade
        for x in range(21, 29):
            set_p(x, 29, CLR_ROYAL_GOLD if x < 23 else CLR_ROYAL_STEEL)

    return canvas

def generate_sheets():
    sheet_w, sheet_h = 128, 160 # 4 cols x 5 rows

    # 1. Runner sheet
    pixels_runner = [CLR_TRANSPARENT] * (sheet_w * sheet_h)
    def blit_r(c, col, row):
        ox, oy = col * 32, row * 32
        for y in range(32):
            for x in range(32):
                pixels_runner[(oy + y) * sheet_w + (ox + x)] = c[y * 32 + x]

    for f in range(4): blit_r(draw_runner(f, "idle"), f, 0)
    for f in range(4): blit_r(draw_runner(f, "walk"), f, 1)
    for f in range(4): blit_r(draw_runner(f, "attack"), f, 2)
    for f in range(4): blit_r(draw_runner(f, "hurt"), f, 3)
    for f in range(4): blit_r(draw_runner(f, "death"), f, 4)
    create_png(sheet_w, sheet_h, pixels_runner, "assets/enemies/zombie_runner.png")
    print("Generated assets/enemies/zombie_runner.png")

    # 2. Royal Zombie sheet
    pixels_royal = [CLR_TRANSPARENT] * (sheet_w * sheet_h)
    def blit_ry(c, col, row):
        ox, oy = col * 32, row * 32
        for y in range(32):
            for x in range(32):
                pixels_royal[(oy + y) * sheet_w + (ox + x)] = c[y * 32 + x]

    for f in range(4): blit_ry(draw_royal_zombie(f, "idle"), f, 0)
    for f in range(4): blit_ry(draw_royal_zombie(f, "walk"), f, 1)
    for f in range(4): blit_ry(draw_royal_zombie(f, "attack"), f, 2)
    for f in range(4): blit_ry(draw_royal_zombie(f, "hurt"), f, 3)
    for f in range(4): blit_ry(draw_royal_zombie(f, "death"), f, 4)
    create_png(sheet_w, sheet_h, pixels_royal, "assets/enemies/zombie_royal.png")
    print("Generated assets/enemies/zombie_royal.png")

if __name__ == "__main__":
    generate_sheets()
