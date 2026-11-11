The user wants a Python function using PIL ImageDraw to draw a funny 2D cartoon scene. Let me write clean code.

Requirements:

def draw_scene(draw, t, duration, w, h)

w=720, h=1280

Background: bedroom with window, alarm clock vibrating

Stickman: sleeping under blanket or waking up with funny expressions and moving limbs based on math.sin(t * 10)

Clean ink doodle aesthetic

Let me design:

Background: cream/off-white paper color, sketchy lines (ink doodle style). Window with curtains, moon/stars. Alarm clock on nightstand vibrating with sin-based offset.

Stickman: sleeping under blanket, head on pillow, eyes closed, Zzz floating. As t progresses, maybe he wakes up: eyes open, limbs flail based on sin(t*10).

Let me write helper functions inside or outside.

I'll use math.sin(t*10) for limb movement.

Structure:

background fill

floor line

window with crossbars, curtains, stars/moon

nightstand with alarm clock (vibrating)

bed frame

pillow

stickman head (circle), body, arms/legs

blanket (rounded rectangle polygon)

Zzz text or lines

speech bubble? no, just aesthetic

Let's write.

Ink doodle aesthetic: use black lines, slightly varying, round joints. Colors: soft pastel. Outline width ~4-6.

Let me carefully compute coordinates for 720x1280.

Floor line at y = 1050 maybe. Bed occupies lower half.

Let me lay out:

Window: x 60-300, y 120-420

Nightstand: x 480-680, y 880-1060

Alarm clock on nightstand top y ~ 800-880

Bed: headboard at left, bed from y 900 to 1150, x 80-640

Pillow at left of bed, head at x ~ 200, y ~ 950

Blanket covering from x 250 to 640

Actually stickman sleeping: head on pillow near left, body under blanket extending right. Head circle radius 55 at (200, 940). Blanket lump from x 260 to 620, top y ~ 900.

Wake up phase: after some fraction of duration, he sits up. Keep it simple: blend parameter wake = clamp((t/duration - 0.4)/0.3, 0, 1). When awake, head moves up, eyes open, arms flail.

Maybe simpler: continuous animation. Let's do a wake-up progression plus sin-based flailing always.

Let me define:
p = t / duration
wake = smoothstep from 0.3 to 0.7

Head position: lerp between (200, 940) and (240, 800).

Arms: when sleeping, hidden under blanket. When awake, arms flail: angle = sin(t*10).

Legs: hidden.

Also blanket shifts down when he sits up.

Let me implement with helper draw functions:

def ink_line(draw, pts, width=5, fill=(30,30,35)): draw.line(pts, fill=fill, width=width, joint="curve")

Use round joints.

For circles: draw.ellipse with outline and width.

Colors:

paper: (247, 243, 233)

ink: (35, 33, 40)

accent blue (blanket): (120, 165, 210) fill with ink outline

pillow: (250, 250, 250)

nightstand wood: (200, 160, 120)

window glass: (200, 225, 240)

moon: (255, 235, 150)

Draw order: background, floor, window, stars, moon, curtains, nightstand, alarm clock, bed frame, pillow, blanket, stickman, Zzz, speech lines.

Alarm clock vibrating: offset = sin(t40)4 for whole clock; also little vibration lines.

Let me write the code.

For the stickman:

Head circle radius r=58 at (hx, hy).
Face: eyes as arcs (closed) when sleeping -> two small arcs. When awake: eyes as circles with dot, wide; mouth open O.

Blend: use wake factor. For eyes, draw closed arcs with alpha proportional... easier: if wake > 0.5 draw open eyes else closed. But smooth is nicer; use draw arcs anyway.

Let's do: eye_open = wake. If wake < 0.5 -> draw "u" arcs (closed eyes). Else draw circles with pupils sized by wake.

Simplify: draw closed-eye arcs when wake < 0.5 else big eyes.

Mouth: sleeping -> small line; awake -> oval (yawning).

Hair: a few scribble lines on top of head.

Body: neck to shoulder line down to y ~ hy + 130, but covered by blanket.

When awake: torso line visible above blanket, arms flailing with sin(t*10).

Arms: shoulder at (hx, hy + 70). Arm angle = base + sin(t10)40 degrees. Draw upper arm and forearm with elbow bend.

Legs: not visible (under blanket). Fine.

Blanket: polygon with wavy top edge. Points: from (bx0, by0) ... use a curve: for x in range, y = topY + sin(x0.05 + t2)*6.

Blanket covers from x=250 to x=680, top y = 900 (sleeping) -> 980 (awake, lower). Actually if he sits up, the blanket top goes lower at the head end.

Let's just have blanket top y = 900 + wake*60.

Hmm but head sits up above blanket. Fine.

Let me set bed: mattress top y = 940. Blanket drapes.

Actually let's place head resting ON pillow which is on mattress top y=940. Head center y = 940 - 55 = 885 when lying. When sitting up, head center y = 800.

Blanket covers body from x=270 to 660, top edge ~ 900.

Zzz: floating "Z" characters rising with time. Draw text with default font — PIL default font is tiny. Use draw.text with font=None -> default bitmap font, small. Could scale... Better draw Z as lines manually. Let's draw Z using line segments: three strokes. Size scaled.

Z position: x = 300 + 40sin(...), y = 860 - ((t60) % 120). Draw 3 Zs with different phases.

Also "ink doodle" - add some sketchy hatching lines maybe.

Window: night sky with moon and stars. Curtains on sides.

Let me now write the code.

python
Copy
Download
import math
from PIL import Image, ImageDraw

def draw_scene(draw, t, duration, w, h):
    INK = (38, 36, 44)
    ...

I need to be careful: draw is an ImageDraw object. Font not needed.

Helper inside function:

python
Copy
Download
def L(pts, width=5, fill=INK):
    draw.line(pts, fill=fill, width=width, joint="curve")

But for smooth curves I'd need many points. I'll generate with list comprehension.

Let me write out full code.

python
Copy
Download
def draw_scene(draw, t, duration, w, h):
    import math
    INK = (40, 38, 46)
    PAPER = (248, 244, 234)
    BLUE = (139, 180, 220)
    BLUE_D = (104, 146, 190)
    WOOD = (196, 158, 118)
    WOOD_D = (168, 130, 92)
    WHITE = (252, 252, 250)
    MOON = (255, 232, 150)
    PINK = (245, 190, 190)

    def line(pts, width=5, fill=INK):
        draw.line(pts, fill=fill, width=width, joint="curve")

    def circle(cx, cy, r, outline=INK, width=5, fill=None):
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=outline, width=width, fill=fill)

    def poly(pts, fill=None, outline=INK, width=5):
        draw.polygon(pts, fill=fill)
        if outline:
            draw.line(list(pts) + [pts[0]], fill=outline, width=width, joint="curve")

    # ---- background
    draw.rectangle([0, 0, w, h], fill=PAPER)

Wall/floor: floor line at y = 1060. Draw a subtle floor with a horizontal line and a few hatch strokes.

Window: x0=70,y0=140,x1=310,y1=430.

Draw window frame: rect outline. Inside night sky fill (dark blue 40,50,90) maybe lighter for doodle: (70,90,140).

Stars: small crosses.

Moon: circle crescent.

Curtains: on left and right of window, drawn as wavy vertical shapes.

Nightstand: x 470-680, top y=880, bottom y=1060.

Alarm clock: center (575, 830), r=52. Vibrating: dx = math.sin(t38)6, dy = math.sin(t*38+1.3)*3. Also rotation-ish—skip.

Clock face: white circle, two hands, two little legs, two bells on top. Vibration lines around when ringing.

Ring intensity: maybe ring only in first part? Let's keep ringing always with amplitude modulated by sin.

Bed: headboard at left x 60-120? Actually let's have bed with headboard on left.

Bed frame: x from 70 to 660, mattress top y=940, bottom y=1080. Legs at 100 and 630 down to 1130.

Pillow: rounded rect (ellipse-ish) at x 130-290, y 880-945, white with pink tint.

Head center: (215, 880) lying. Hmm head should be on pillow: pillow top y ~ 880, head center y = 880 - 55 = 825. Let's put head center (210, 820), r=56.

Then body extends right under blanket. Blanket from x=250 to 650, top y ≈ 850.

Actually a person lying: head at left on pillow, body under blanket going right. Blanket top around y=870 covering body.

Let me set:

mattress top y = 900

pillow: ellipse centered (215, 880), rx 95, ry 48 → top at 832.

head center lying: (215, 790)? That puts head above pillow. Hmm, head resting on pillow means head center around pillow center y - something.

Simplify: head center lying = (215, 800), r = 56 → bottom of head at 856, sits on pillow whose top is ~832. Slight overlap fine. Looks like head on pillow.

Blanket: covers x from 265 to 655, top edge y = 830 with wave. So head pokes out at left. Good.

When awake (wake=1): head center (250, 690), body torso visible from (250, 746) down to (250, 830)... then blanket.

Hmm, sitting up: head up, shoulders up, blanket around chest.

Let's define:
hy = 800 - 110wake
hx = 215 + 30wake

Torso: from (hx, hy+56) to (hx, hy+56+ (120 - 40*wake))... Actually when lying, no torso visible (blanket covers). When awake, torso line from head bottom down to blanket top.

Torso bottom y = hy + 56 + 130. With hy=690 → 876. Blanket top ~ 840. So torso goes under blanket. Fine.

Blanket top y when awake: 850. When lying: 830. Let's do blanket_top = 830 + 30*wake.

Hmm but if head at y=800 with r=56, bottom at 856, and blanket top 830, the blanket covers the chin. That's fine for sleeping.

When awake head at 690, bottom 746, blanket top 860. Torso visible 746→860. Good.

Arms when awake: from shoulder (hx, hy+70) flailing.

Actually shoulder should be near head bottom: (hx, hy+60).

Arm:

text
Copy
Download
a1 = math.sin(t*10) * 0.9

Upper arm length 70, forearm 60.

Compute elbow:
ex = hx + 70*math.cos(angle1)... but angle measured from downward direction.

Let's do: angle from vertical downward, positive = to the right.
elbow = (hx + 70math.sin(a1), shoulder_y + 70math.cos(a1))

forearm angle a2 = a1 + something.
hand = (ex + 60math.sin(a2), ey + 60math.cos(a2))

Two arms with opposite phases.

When sleeping (wake=0), arms hidden under blanket. Blend by only drawing arms if wake > 0.15, with length scaled by wake.

Actually simpler: draw arms always but scale length by wake. When wake=0 length 0 → invisible.

Legs: hidden. Skip.

Also when waking, add motion lines.

Face:

Eyes: when wake < 0.4 → closed arcs (sleeping). When wake >= 0.4 → open circles with pupils, plus eyebrows.

Mouth: sleeping → small line/oval; awake → big oval "O" (yawning).

Let's just do:
eye_y = hy - 8
eye_dx = 20
if wake < 0.45:
closed arcs: draw.arc([cx-14, eye_y-8, cx+14, eye_y+8], 200, 340, fill=INK, width=5)
else:
circle(cx, eye_y, 13) fill white, then pupil circle r 6 offset by sin.

Mouth: at (hx, hy+26). If wake<0.45: small horizontal line. Else ellipse.

Also add a "yawn" star burst? Keep simple.

Hair: 3-4 short strokes on top of head.

Zzz: only when wake < 0.5, fade out. Draw at (hx+70, hy-70) drifting up.

Z drawing function: given center and size s, draw three lines:
top horizontal from (-s, -s) to (s, -s)
diagonal from (s,-s) to (-s, s)
bottom from (-s, s) to (s, s)

Use size 14.

Let's add 3 Zs with offsets.

Alarm clock vibration lines around it.

Also add sketchy "hatching" shading lines for doodle feel — maybe short diagonal strokes under bed.

Also a small rug? Not needed.

Let me also add a poster or lamp? Keep simple but rich enough.

Let's write the final code carefully.

Order:

paper rect

floor band

window (sky, stars, moon, frame, curtains)

wall hatching (light)

nightstand + alarm clock

bed frame, mattress, pillow

stickman head+torso+arms (behind blanket? head in front of blanket top, torso behind)

Draw torso first, then blanket, then head? Head is above blanket anyway. Draw: torso, arms, then blanket, then head... but arms should be in front of blanket when awake. Draw blanket first then arms. But blanket covers torso bottom.

Order: mattress → pillow → torso → blanket → arms → head.

Wait head is at top, no conflict.

Zzz

motion lines

Let me write it.

For the blanket wavy top: build points from x=265 to x=655 step 12:
y = blanket_top + 7math.sin(x0.045 - t*3)

Then close polygon down to bottom.

Blanket color BLUE fill with ink outline.

Also add a fold line or two on the blanket.

Bed frame: draw rectangle for mattress: [70, 900, 660, 1010] rounded. Use draw.rounded_rectangle available in PIL ≥ 8.2. Might be risky; I'll use polygon manually or just rectangle with lines.

Actually draw.rounded_rectangle exists in Pillow 8.2+. Likely fine. But to be safe use draw.rectangle + outline.

Hmm, ImageDraw.rounded_rectangle is fine in modern Pillow. I'll use it with try/except? No—keep it simple, use plain rectangles and lines.

Let me code.

python
Copy
Download
    # ---------- floor
    fy = 1010
    line([(0, fy), (w, fy)], width=5)
    for i in range(0, w, 60):
        line([(i, fy + 20), (i + 40, fy + 20)], width=3, fill=(210, 200, 188))

Hmm hatch lines maybe lighter.

Let me write the whole thing now.

Also need wavy curtain function.

I'll write it out.

Final code:

python
Copy
Download
def draw_scene(draw, t, duration, w, h):
    import math

    INK     = (40, 38, 48)
    PAPER   = (248, 244, 233)
    WALL    = (240, 233, 218)
    BLUE    = (150, 190, 228)
    BLUE_D  = (110, 150, 196)
    WOOD    = (204, 165, 122)
    WOOD_D  = (166, 128, 92)
    WHITE   = (253, 252, 248)
    MOON    = (255, 226, 140)
    NIGHT   = (86, 104, 156)
    PINK    = (247, 198, 198)
    GREY    = (206, 198, 186)

    def line(pts, width=5, fill=INK):
        draw.line(pts, fill=fill, width=width, joint="curve")

    def circ(cx, cy, r, outline=INK, width=5, fill=None):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=outline, width=width, fill=fill)

    def arc(box, a0, a1, width=5, fill=INK):
        draw.arc(box, a0, a1, fill=fill, width=width)

    def poly(pts, fill=None, outline=INK, width=5):
        draw.polygon(pts, fill=fill)
        if outline:
            line(list(pts) + [pts[0]], width=width, fill=outline)

    # ---------------- wall + floor
    draw.rectangle([0, 0, w, h], fill=PAPER)
    line([(0, 1000), (w, 1000)], width=5)
    draw.rectangle([0, 1000, w, h], fill=WALL)
    line([(0, 1000), (w, 1000)], width=5)
    for x in range(30, w, 90):
        line([(x, 1030), (x + 45, 1030)], width=3, fill=GREY)

Hmm floor fill after line — reorder. Fine.

Wall texture: light vertical dashes.

Continue.

Window:

python
Copy
Download
    wx0, wy0, wx1, wy1 = 66, 150, 316, 440
    draw.rectangle([wx0, wy0, wx1, wy1], fill=NIGHT, outline=INK, width=5)
    # stars
    stars = [(100,190),(150,240),(250,180),(280,300),(120,330),(200,390),(270,400)]
    for i,(sx,sy) in enumerate(stars):
        ph = math.sin(t*2 + i)
        r = 4 + 2*ph
        line([(sx-r, sy), (sx+r, sy)], width=3, fill=WHITE)
        line([(sx, sy-r), (sx, sy+r)], width=3, fill=WHITE)
    # moon
    circ(255, 210, 34, outline=MOON, width=0, fill=MOON)

draw.ellipse with width=0 outline=MOON works: fill=MOON, outline=None. Let me do draw.ellipse([...], fill=MOON).

Then a shadow circle to make crescent? Skip, full moon.

Window frame cross:

python
Copy
Download
    line([((wx0+wx1)//2, wy0), ((wx0+wx1)//2, wy1)], width=5)
    line([(wx0, (wy0+wy1)//2), (wx1, (wy0+wy1)//2)], width=5)

Curtains: left curtain from (40,130) to (100,470) wavy.
Draw as polygon:

python
Copy
Download
    def curtain(x0, x1, y0, y1, flip):
        pts = []
        ...

Simplify: draw a wavy-edged rectangle.

Left curtain:

python
Copy
Download
    cpts = [(x0, y0), (x1, y0)]
    for i in range(0, 11):
        yy = y0 + (y1-y0)*i/10
        cpts.append((x1 + 10*math.sin(i*1.1 + t*1.5), yy))
    cpts.append((x0, y1))
    poly(cpts, fill=PINK)

Good.

Alarm clock vibration:

python
Copy
Download
    vib = math.sin(t * 34.0)
    cx = 578 + 7*vib
    cy = 812 + 3*math.sin(t*34.0 + 1.1)

Clock: body circle r=54, bells: two small arcs/circles at top left and right, legs two lines down, face hands.

Ringing lines: 4 short strokes radiating, length varying with |vib|.

Nightstand:

python
Copy
Download
    ns_x0, ns_y0, ns_x1, ns_y1 = 486, 880, 686, 1000
    draw.rectangle([ns_x0, ns_y0, ns_x1, ns_y1], fill=WOOD, outline=INK, width=5)
    line([(ns_x0, ns_y0+40), (ns_x1, ns_y0+40)], width=4)
    circ((ns_x0+ns_x1)//2, ns_y0+20, 6, width=4)

Hmm nightstand top y=880 but clock center 812 with r 54 → bottom 866. OK sits on top. Good.

Legs of nightstand: from y=1000 to 1010 — floor line is 1000. Fine, no legs.

Bed:

Headboard: rectangle x 60-110, y 800-1000? Actually headboard on left. Let's have bed along x.

Mattress: [110, 900, 680, 1000]? But nightstand is at x 486-686, overlapping.

Hmm. Let me restructure: put the nightstand on the right at x 520-700, and bed from x=40 to x=500. Then head at left ~ 150.

But then the stickman's body extends right to x=490, and the alarm clock at ~610.

Let's do that.

Bed: mattress [40, 895, 505, 1005]. Headboard: [20, 800, 60, 1005]? Draw headboard behind at left.

Hmm, headboard at left: vertical panel x 20-55, y 790-1005.

Pillow: ellipse center (135, 878), rx 88, ry 45.

Head: lying center (140, 800), r 55.

Blanket from x=190 to x=500, top y=845 wavy, bottom to 1000.

Nightstand: x 545-700, y 890-1000. Clock center (622, 822), r 52.

Ok. But then the bed right edge at 505 and nightstand at 545 — small gap. Fine.

Bed legs: at x=60 and x=480, from y=1005 to 1030.

Floor line at y=1010? Bed legs extend to 1030, below floor line. Put floor line at y=1000 and legs go to 1030 — legs would be in the "floor" region, fine visually (foreground). Actually let's set floor line at y=1015 and bed bottom at 1005, legs to 1035.

Simplify: floor line y = 1010. Bed legs from 1005 to 1035 — slightly below floor line, acceptable as foreground.

Hmm, let me just put floor line at 1040 and everything above. Nightstand bottom 1000, legs 1000-1040.

Ok: floor line y=1040. Bed frame bottom 1005, legs 1005→1040.

Now heights: total 1280, so below 1040 there's 240px of empty floor. Maybe add a rug or shadow. Add a simple ellipse shadow under bed. And the floor hatching.

Actually maybe move everything down a bit... it's fine, add rug.

Let me add a simple rug ellipse under the bed area? Or just hatching lines. I'll add a few horizontal hatch lines.

Let me finalize coordinates:

Floor line: y = 1040.

Bed:

headboard: rect [30, 780, 72, 1010]

mattress: rect [50, 890, 510, 1008], fill WHITE

legs: (80, 1008)-(80,1040), (480,1008)-(480,1040)

pillow: ellipse center (150, 872), rx 90, ry 46 → spans x 60-240, y 826-918

head lying: (150, 795), r 55 → bottom 850, sits on pillow top 826. ok

blanket: x from 205 to 505, top y 840, wavy

Nightstand: rect [545, 890, 705, 1005], wood.
Clock: center (625, 820), r 50 → bottom 870, sits on 890. Hmm gap. Move clock center to 840 → bottom 890. Good. cy = 838.

Wait top of clock = 788. Fine.

Alarm bells on top of clock at y ~ 790.

Now head at (150,795) and clock at (625,838) — no overlap.

Good.

Now, the arms when awake: shoulder at (hx, hy+58). hx=150+30wake, hy=795-105wake.

Arms flail with sin(t*10).

Let's write the arm drawing:

python
Copy
Download
    for side in (-1, 1):
        a1 = side * (0.55 + 0.85 * math.sin(t * 10 + (0 if side > 0 else math.pi)))
        ...

Hmm, want flailing. Let's do:

python
Copy
Download
        ph = 0.0 if side > 0 else math.pi * 0.8
        a1 = side * (0.35 + 0.9 * math.sin(t * 10 + ph))
        ex = sx + side * 62 * math.sin(abs(a1)) ... 

Simpler: use angles measured from straight down.

upper_len = 62 * wake
fore_len = 54 * wake

angle1 = 1.1 * math.sin(t10 + ph) + side0.55
elbow = (sx + upper_lenmath.sin(angle1), sy + upper_lenmath.cos(angle1))
angle2 = angle1 + 0.9math.sin(t10 + ph + 1.2)
hand = (ex + fore_lenmath.sin(angle2), ey + fore_lenmath.cos(angle2))

Draw line shoulder→elbow→hand with round caps (draw circles at joints).

Also head circle drawn last so it's on top.

Since arms are drawn at the shoulder point which is inside the head circle bottom... shoulder at hy+58 with head r=55, so just below head. Fine.

Now Zzz when sleeping.

Let me write a Z helper:

python
Copy
Download
    def draw_z(cx, cy, s, alpha_col):
        line([(cx-s, cy-s), (cx+s, cy-s)], width=4, fill=alpha_col)
        line([(cx+s, cy-s), (cx-s, cy+s)], width=4, fill=alpha_col)
        line([(cx-s, cy+s), (cx+s, cy+s)], width=4, fill=alpha_col)

Position: base (hx+70, hy-70), rising with t.

for k in range(3):
prog = (t*0.55 + k/3) % 1.0
zx = hx + 60 + 35*prog + 10math.sin(t3 + k)
zy = hy - 70 - 90prog
s = 8 + 10prog
draw_z(zx, zy, s)

Only if wake < 0.6, and fade... just draw when wake < 0.6.

OK. Also motion lines when awake.

Motion lines: short arcs near arms.

Let me also add "!" or sweat drop? Keep it.

Now let's assemble the whole function and be careful about syntax.

One more: the poly helper with list(pts) + [pts[0]] — if pts is a list of tuples fine.

For the blanket, points list.

Also I should add a fold/wrinkle line on blanket.

Let me write final code.

Also need wake smoothstep:

python
Copy
Download
    p = t / duration if duration else 0
    raw = (p - 0.35) / 0.30
    raw = max(0.0, min(1.0, raw))
    wake = raw * raw * (3 - 2 * raw)

Good.

Now writing.

For the window, the fill NIGHT rect. And stars drawn on top.

Note: draw.rectangle with width param supported in Pillow ≥ 5.3 for outline width. Yes, ImageDraw.rectangle(xy, fill, outline, width) — width added in Pillow 5.3. Fine.

draw.arc with width — supported.

Let's write.

One concern: draw.line with joint="curve" requires at least 3 points? It works with 2 as well.

Ok final.

Also add slight jitter to ink lines for hand-drawn feel? Could do but risky. Skip.

Actually a small touch: use draw.line width 5 for main outlines and 3-4 for details.

Write the code now.

python
Copy
Download
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
    GREY   = (205, 196, 182)

    # ...

Ok writing everything out.

I'll be careful that all helper functions defined before use.

Let me write the final answer.

Also the stickman head: add hair strokes.

And ear? no.

Final code:

python
Copy
Download
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

    def line(pts, width=5, fill=INK):
        draw.line(pts, fill=fill, width=width, joint="curve")

    def circ(cx, cy, r, width=5, fill=None, outline=INK):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

    def poly(pts, fill=None, outline=INK, width=5):
        draw.polygon(pts, fill=fill)
        if outline is not None:
            line(list(pts) + [pts[0]], width=width, fill=outline)

    def wake_at(tt):
        p = (tt / duration) if duration else 0.0
        v = (p - 0.35) / 0.30
        v = max(0.0, min(1.0, v))
        return v * v * (3 - 2 * v)

    wake = wake_at(t)

    # ---------- room ----------
    draw.rectangle([0, 0, w, h], fill=PAPER)
    draw.rectangle([0, 1040, w, h], fill=WALL)
    line([(0, 1040), (w, 1040)], width=5)
    for x in range(20, w, 86):
        line([(x, 1080), (x + 44, 1080)], width=3, fill=GREY)
    for x in range(48, w, 86):
        line([(x, 1130), (x + 52, 1130)], width=3, fill=GREY)

Fine.

Then window etc.

Let me finalize and output.

I'll write it all out now in the answer.

One detail: the poly with a list that ends near start — fine.

For the curtain, need points forming a closed shape.

Left curtain x0=40, x1=96, y0=140, y1=470.
Points: [(40,140), (96,140)] then down the right edge with wave, then [(40,470)].
But that creates a shape only 56 wide; the wave adds. Fine.

Right curtain mirrored around window right edge: x0=286, x1=342.

Wait window is x 66..316. Left curtain covers 40-96 (overlapping window left edge by 30). Right curtain 286-342.

Hmm, curtains should be outside the window mostly. Let's do left curtain 30-88, right 296-354. Window 66-316 so curtains overlap edges slightly. Good.

Curtain rod: line from 20 to 364 at y=132.

Ok, writing.

For the wavy right edge of left curtain:

python
Copy
Download
    pts = [(30, 136), (88, 136)]
    for i in range(1, 12):
        yy = 136 + (470 - 136) * i / 11.0
        pts.append((88 + 9 * math.sin(i * 0.9 + t * 1.6), yy))
    pts.append((30, 470))
    poly(pts, fill=PINK)

Good.

Right curtain mirrored:

python
Copy
Download
    pts = [(354, 136), (296, 136)]
    for i in range(1, 12):
        yy = 136 + (470 - 136) * i / 11.0
        pts.append((296 - 9 * math.sin(i * 0.9 + t * 1.6 + 1.0), yy))
    pts.append((354, 470))
    poly(pts, fill=PINK)

Good.

Now the final assembly.

I think we're ready. Write it out.