def draw_scene(draw, t, duration, w, h):
    import math

    INK    = (42, 40, 50)
    PAPER  = (248, 244, 233)
    WALL   = (238, 230, 214)
    BLUE   = (152, 192, 230)
    BLUE_D = (108, 148, 194)
    WOOD   = (206, 166, 122)
    WOOD_D = (168, 130, 92)
    WHITE  = (253, 252, 248)
    MOONC  = (255, 226, 140)
    NIGHT  = (88, 106, 158)
    PINK   = (246, 198, 198)
    GREY   = (203, 194, 180)

    # ---------------- tiny drawing helpers (ink doodle style) ----------------
    def line(pts, width=5, fill=INK):
        draw.line(pts, fill=fill, width=width, joint="curve")

    def circ(cx, cy, r, width=5, fill=None, outline=INK):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=fill, outline=outline, width=width)

    def poly(pts, fill=None, outline=INK, width=5):
        draw.polygon(pts, fill=fill)
        if outline is not None:
            line(list(pts) + [pts[0]], width=width, fill=outline)

    def wake_at(tt):
        p = (tt / duration) if duration else 0.0
        v = (p - 0.35) / 0.30
        v = max(0.0, min(1.0, v))
        return v * v * (3.0 - 2.0 * v)

    wake = wake_at(t)

    # =========================================================
    # 1. ROOM  (wall + floor)
    # =========================================================
    draw.rectangle([0, 0, w, h], fill=PAPER)
    draw.rectangle([0, 1040, w, h], fill=WALL)
    line([(0, 1040), (w, 1040)], width=5)
    for x in range(20, w, 86):
        line([(x, 1082), (x + 44, 1082)], width=3, fill=GREY)
    for x in range(48, w, 86):
        line([(x, 1136), (x + 54, 1136)], width=3, fill=GREY)

    # ---------------- WINDOW (night sky) ----------------
    wx0, wy0, wx1, wy1 = 66, 150, 316, 440
    draw.rectangle([wx0, wy0, wx1, wy1], fill=NIGHT, outline=INK, width=5)

    stars = [(104, 196), (152, 248), (252, 184), (282, 302),
             (124, 336), (204, 392), (272, 404), (92, 288)]
    for i, (sx, sy) in enumerate(stars):
        r = 4 + 2.5 * math.sin(t * 2.2 + i * 1.7)
        line([(sx - r, sy), (sx + r, sy)], width=3, fill=WHITE)
        line([(sx, sy - r), (sx, sy + r)], width=3, fill=WHITE)

    draw.ellipse([222, 176, 290, 244], fill=MOONC)
    draw.ellipse([238, 170, 306, 238], fill=NIGHT)

    line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], width=5)
    line([(wx0, (wy0 + wy1) // 2), (wx1, (wy0 + wy1) // 2)], width=5)

    # ---------------- CURTAINS ----------------
    line([(20, 132), (364, 132)], width=6)

    pts = [(30, 136), (88, 136)]
    for i in range(1, 12):
        yy = 136 + (470 - 136) * i / 11.0
        pts.append((88 + 9 * math.sin(i * 0.9 + t * 1.6), yy))
    pts.append((30, 470))
    poly(pts, fill=PINK)

    pts = [(354, 136), (296, 136)]
    for i in range(1, 12):
        yy = 136 + (470 - 136) * i / 11.0
        pts.append((296 - 9 * math.sin(i * 0.9 + t * 1.6 + 1.0), yy))
    pts.append((354, 470))
    poly(pts, fill=PINK)

    # =========================================================
    # 2. NIGHTSTAND + VIBRATING ALARM CLOCK
    # =========================================================
    draw.rectangle([545, 890, 705, 1005], fill=WOOD, outline=INK, width=5)
    line([(545, 932), (705, 932)], width=4)
    circ(625, 911, 6, width=4)

    vib = math.sin(t * 34.0)
    cx = 625 + 7 * vib
    cy = 838 + 3 * math.sin(t * 34.0 + 1.1)

    # clock legs
    line([(cx - 26, cy + 44), (cx - 34, cy + 62)], width=5)
    line([(cx + 26, cy + 44), (cx + 34, cy + 62)], width=5)
    # bells
    circ(cx - 30, cy - 44, 13, width=4, fill=PINK)
    circ(cx + 30, cy - 44, 13, width=4, fill=PINK)
    # body
    circ(cx, cy, 50, width=6, fill=WHITE)
    # clock hands (spinning fast = alarm)
    ha = t * 9.0
    line([(cx, cy), (cx + 24 * math.sin(ha), cy - 24 * math.cos(ha))], width=4)
    line([(cx, cy), (cx + 15 * math.sin(ha * 2 + 1), cy - 15 * math.cos(ha * 2 + 1))], width=4)
    circ(cx, cy, 4, width=3, fill=INK)

    # ring lines
    amp = abs(vib)
    for k in range(4):
        ang = -1.9 + k * 1.25
        r0 = 62
        r1 = 62 + 12 + 16 * amp
        x0 = cx + r0 * math.cos(ang)
        y0 = cy + r0 * math.sin(ang)
        x1 = cx + r1 * math.cos(ang)
        y1 = cy + r1 * math.sin(ang)
        line([(x0, y0), (x1, y1)], width=4)

    # =========================================================
    # 3. BED
    # =========================================================
    # headboard
    draw.rectangle([30, 780, 72, 1010], fill=WOOD_D, outline=INK, width=5)
    # legs
    line([(84, 1008), (84, 1042)], width=6)
    line([(484, 1008), (484, 1042)], width=6)
    # mattress
    draw.rectangle([50, 890, 510, 1008], fill=WHITE, outline=INK, width=5)
    line([(50, 960), (510, 960)], width=3, fill=GREY)

    # ---------------- STICKMAN geometry ----------------
    hx = 150 + 34 * wake
    hy = 795 - 108 * wake

    # torso (only visible once he sits up)
    if wake > 0.02:
        line([(hx, hy + 52), (hx, hy + 52 + 150 * wake)], width=7)

    # pillow
    draw.ellipse([150 - 92, 872 - 46, 150 + 92, 872 + 46],
                 fill=WHITE, outline=INK, width=5)

    # ---------------- BLANKET ----------------
    b_top = 842 + 34 * wake
    b_pts = []
    bx = 200
    while bx <= 508:
        by = b_top + 8 * math.sin(bx * 0.045 - t * 3.0)
        b_pts.append((bx, by))
        bx += 12
    b_pts.append((508, 1000))
    b_pts.append((200, 1000))
    poly(b_pts, fill=BLUE)

    # blanket folds
    for fx in (255, 320, 390, 455):
        fy0 = b_top + 8 * math.sin(fx * 0.045 - t * 3.0) + 24
        line([(fx, fy0), (fx + 6, 985)], width=3, fill=BLUE_D)

    # ---------------- ARMS (flailing) ----------------
    sx, sy = hx, hy + 58
    for side in (-1, 1):
        ph = 0.0 if side > 0 else math.pi * 0.85
        up_len = 64 * wake
        fo_len = 56 * wake
        a1 = side * 0.55 + 1.15 * math.sin(t * 10 + ph)
        ex = sx + up_len * math.sin(a1)
        ey = sy + up_len * math.cos(a1)
        a2 = a1 + 0.9 * math.sin(t * 10 + ph + 1.2)
        hx2 = ex + fo_len * math.sin(a2)
        hy2 = ey + fo_len * math.cos(a2)
        if wake > 0.05:
            line([(sx, sy), (ex, ey), (hx2, hy2)], width=6)
            circ(ex, ey, 5, width=4, fill=WHITE)
            circ(hx2, hy2, 7, width=4, fill=WHITE)

    # ---------------- HEAD ----------------
    circ(hx, hy, 55, width=6, fill=WHITE)

    # hair scribbles
    for k in range(3):
        ang = -2.5 + k * 0.32
        x0 = hx + 50 * math.cos(ang)
        y0 = hy + 50 * math.sin(ang)
        line([(x0, y0), (x0 - 8 + 4 * math.sin(t * 6 + k), y0 - 16)], width=5)

    # eyes
    eye_y = hy - 10
    if wake < 0.45:
        for ex_ in (hx - 20, hx + 20):
            draw.arc([ex_ - 15, eye_y - 9, ex_ + 15, eye_y + 9],
                     200, 340, fill=INK, width=5)
    else:
        blink = 0.5 + 0.5 * math.sin(t * 12)
        for ex_ in (hx - 20, hx + 20):
            circ(ex_, eye_y, 14, width=4, fill=WHITE)
            pr = 5 + 2 * blink
            circ(ex_ + 3, eye_y + 1, pr, width=0, fill=INK)
        # eyebrows (surprised)
        line([(hx - 34, eye_y - 26), (hx - 8, eye_y - 32)], width=4)
        line([(hx + 8, eye_y - 32), (hx + 34, eye_y - 26)], width=4)

    # mouth
    if wake < 0.45:
        line([(hx - 14, hy + 26), (hx + 14, hy + 26)], width=4)
    else:
        draw.ellipse([hx - 16, hy + 16, hx + 16, hy + 46],
                     fill=INK, outline=INK, width=3)

    # ---------------- Zzz (sleeping) ----------------
    def draw_z(zx, zy, s):
        line([(zx - s, zy - s), (zx + s, zy - s)], width=4)
        line([(zx + s, zy - s), (zx - s, zy + s)], width=4)
        line([(zx - s, zy + s), (zx + s, zy + s)], width=4)

    if wake < 0.6:
        for k in range(3):
            prog = (t * 0.5 + k / 3.0) % 1.0
            zx = hx + 72 + 34 * prog + 10 * math.sin(t * 3 + k)
            zy = hy - 66 - 96 * prog
            draw_z(zx, zy, 8 + 10 * prog)

    # ---------------- motion lines when flailing ----------------
    if wake > 0.55:
        for k in range(3):
            yy = sy - 30 + k * 26
            off = 8 * math.sin(t * 10 + k)
            line([(hx - 92 - off, yy), (hx - 66 - off, yy)], width=3, fill=GREY)
            line([(hx + 92 + off, yy), (hx + 66 + off, yy)], width=3, fill=GREY)

    # ---------------- floor shadow ----------------
    draw.ellipse([60, 1030, 520, 1062], fill=(224, 214, 198))