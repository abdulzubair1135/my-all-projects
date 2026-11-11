import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import win32com.client

def create_clean_polished_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Exact palette from user's Canva template
    COLOR_LIME = RGBColor(126, 217, 87)       # #7ED957 (Canva bright lime green)
    COLOR_ROYAL_BLUE = RGBColor(18, 34, 157)  # #12229D (Canva royal blue)
    COLOR_WHITE = RGBColor(255, 255, 255)     # #FFFFFF
    COLOR_LIGHT_LIME = RGBColor(190, 242, 160)# #BEF2A0
    COLOR_BLACK_TEXT = RGBColor(15, 23, 42)    # #0F172A (Deep bold black)

    FONT_TITLE = "Anton"
    FONT_BODY = "Inter"

    mock_dir = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\scratch\polished_mockups"

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_LIME
        bg.line.fill.background()
        return bg

    def add_top_bar(slide, num_str, brand="NEXUS MESHLINK"):
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.35), Inches(12.133), Inches(0.65))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        bar.line.color.rgb = COLOR_WHITE
        bar.line.width = Pt(2.5)

        tf = bar.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.05)

        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = brand.upper()
        run.font.name = FONT_TITLE
        run.font.size = Pt(22)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE

        # Number on right (#01, #02...)
        num_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.35), Inches(2.0), Inches(0.65))
        ntf = num_box.text_frame
        ntf.margin_top = Inches(0.12)
        ntf.margin_right = Inches(0.3)
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        nrun = np.add_run()
        nrun.text = f"#{num_str}"
        nrun.font.name = FONT_TITLE
        nrun.font.size = Pt(22)
        nrun.font.bold = True
        nrun.font.color.rgb = COLOR_WHITE

    def add_slide_header(slide, title_text):
        h_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.1), Inches(12.133), Inches(0.72))
        h_box.fill.solid()
        h_box.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        h_box.line.color.rgb = COLOR_WHITE
        h_box.line.width = Pt(2.5)

        tf = h_box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.1)
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title_text.upper()
        run.font.name = FONT_TITLE
        run.font.size = Pt(30)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE

    def add_head_outline_box(slide, left, top, width, height, title_text, is_blue_card=False):
        badge = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_LIME if is_blue_card else COLOR_ROYAL_BLUE
        badge.line.color.rgb = COLOR_WHITE if is_blue_card else COLOR_WHITE
        badge.line.width = Pt(2)
        
        btf = badge.text_frame
        btf.word_wrap = True
        btf.margin_top = Inches(0.08)
        btf.margin_left = Inches(0.2)
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        brun = bp.add_run()
        brun.text = title_text.upper()
        brun.font.name = FONT_TITLE
        brun.font.size = Pt(23)
        brun.font.bold = True
        brun.font.color.rgb = COLOR_ROYAL_BLUE if is_blue_card else COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 1: HERO COVER
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)
    add_top_bar(s1, "01", "NEXUS MESHLINK ECOSYSTEM")

    left_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.8), Inches(4.9))
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    left_box.line.color.rgb = COLOR_WHITE
    left_box.line.width = Pt(3.5)
    ltf = left_box.text_frame
    ltf.word_wrap = True
    ltf.margin_left = Inches(0.5)
    ltf.margin_right = Inches(0.5)
    ltf.margin_top = Inches(0.6)
    
    lp1 = ltf.paragraphs[0]
    lrun1 = lp1.add_run()
    lrun1.text = "OFFLINE AI NETWORKING"
    lrun1.font.name = FONT_TITLE
    lrun1.font.size = Pt(32)
    lrun1.font.bold = True
    lrun1.font.color.rgb = COLOR_WHITE

    lp2 = ltf.add_paragraph()
    lp2.space_before = Pt(20)
    lrun2 = lp2.add_run()
    lrun2.text = "Phase 2 & Phase 3 Master Architecture: Zero-cellular mesh, on-device Qwen AI, duplex calls & web portal."
    lrun2.font.name = FONT_BODY
    lrun2.font.size = Pt(25)
    lrun2.font.bold = True
    lrun2.font.color.rgb = COLOR_LIGHT_LIME

    right_box = s1.shapes.add_textbox(Inches(6.6), Inches(1.5), Inches(6.1), Inches(4.5))
    rtf = right_box.text_frame
    rtf.word_wrap = True
    rp1 = rtf.paragraphs[0]
    rrun1 = rp1.add_run()
    rrun1.text = "NEXUS\nMESHLINK"
    rrun1.font.name = FONT_TITLE
    rrun1.font.size = Pt(80)
    rrun1.font.bold = True
    rrun1.font.color.rgb = COLOR_WHITE

    url_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.35), Inches(5.8), Inches(0.7))
    url_box.fill.solid()
    url_box.fill.fore_color.rgb = COLOR_LIGHT_LIME
    url_box.line.color.rgb = COLOR_ROYAL_BLUE
    url_box.line.width = Pt(2.5)
    utf = url_box.text_frame
    up = utf.paragraphs[0]
    up.alignment = PP_ALIGN.CENTER
    urun = up.add_run()
    urun.text = "WWW.NEXUSAPP.OFFLINE"
    urun.font.name = FONT_TITLE
    urun.font.size = Pt(22)
    urun.font.bold = True
    urun.font.color.rgb = COLOR_ROYAL_BLUE

    # -------------------------------------------------------------------------
    # SLIDE 2: WHAT IS NEXUS MESHLINK? (Left Card + Right Real Phone Chat Mockup)
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_top_bar(s2, "02")
    add_slide_header(s2, "WHAT IS NEXUS MESHLINK?")

    c2 = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c2.fill.solid()
    c2.fill.fore_color.rgb = COLOR_WHITE
    c2.line.color.rgb = COLOR_ROYAL_BLUE
    c2.line.width = Pt(3.5)

    add_head_outline_box(s2, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "AUTONOMOUS P2P MESH", False)

    c2_tf = c2.text_frame
    c2_tf.word_wrap = True
    c2_tf.margin_left = Inches(0.4)
    c2_tf.margin_right = Inches(0.4)
    c2_tf.margin_top = Inches(1.0)

    pts2 = [
        "100% decentralized Wi-Fi Direct mesh connecting phones up to 250 Mbps.",
        "Zero dependency on cell towers, internet backbones, or routers.",
        "Built-in offline Qwen AI intelligence and encrypted calling."
    ]
    for idx, pt in enumerate(pts2):
        p = c2_tf.paragraphs[0] if idx == 0 else c2_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(14)
        r = p.add_run()
        r.text = "• " + pt
        r.font.name = FONT_BODY
        r.font.size = Pt(25)
        r.font.bold = True
        r.font.color.rgb = COLOR_BLACK_TEXT

    chat_img = os.path.join(mock_dir, "phone_chat.png")
    if os.path.exists(chat_img):
        s2.shapes.add_picture(chat_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 3: INFRASTRUCTURE FAILURES (2 Blue Cards with Outlines)
    # -------------------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_top_bar(s3, "03")
    add_slide_header(s3, "CRITICAL INFRASTRUCTURE FAILURES")

    cards_s3 = [
        ("CENTRALIZED VULNERABILITY", [
            "Cellular base stations require grid power & physical fiber backhauls.",
            "Floods, earthquakes and storms take down entire regional telecom networks."
        ]),
        ("PRIVACY & CENSORSHIP", [
            "Central cloud servers track location metadata and user identities.",
            "Internet kill-switches completely isolate citizens and rescue workers."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s3):
        c = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.25), Inches(1.95), Inches(5.85), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.color.rgb = COLOR_WHITE
        c.line.width = Pt(3.5)

        add_head_outline_box(s3, Inches(0.9 + idx * 6.25), Inches(2.2), Inches(5.25), Inches(0.6), head, True)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(16)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 4: EXISTING APPS ANALYSIS (3 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_top_bar(s4, "04")
    add_slide_header(s4, "EXISTING APPS & INDUSTRY LANDSCAPE")

    competitors = [
        ("BRIDGEFY", [
            "Bluetooth mesh only",
            "Proprietary protocol",
            "No voice/video calls",
            "Zero local AI intelligence"
        ]),
        ("BRIAR MESSENGER", [
            "Heavy Tor dependency",
            "Severe battery/CPU drain",
            "Sluggish sync speed",
            "Text-only communication"
        ]),
        ("MESHTASTIC", [
            "Requires $60 LoRa radio",
            "Tiny bandwidth (<1 KB/s)",
            "Cannot stream voice/video",
            "Complex hardware pairing"
        ])
    ]
    for idx, (head, points) in enumerate(competitors):
        c = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.15), Inches(1.95), Inches(3.8), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s4, Inches(0.85 + idx * 4.15), Inches(2.2), Inches(3.3), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 5: WHY OUR APP IS BEST (2 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_top_bar(s5, "05")
    add_slide_header(s5, "WHY NEXUS MESHLINK IS BEST")

    cards_s5 = [
        ("ZERO HARDWARE & HIGH SPEED", [
            "Uses ordinary Android phones without any external dongles or radios.",
            "High-speed Wi-Fi Direct socket throughput reaches 250 Mbps for instant HD media."
        ]),
        ("ALL-IN-ONE MULTIMODAL MESH", [
            "Combines mesh text, full-duplex voice & video, and embedded local Qwen LLM.",
            "Zero installation web portal allows any laptop to join the mesh in seconds."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s5):
        c = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.25), Inches(1.95), Inches(5.85), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s5, Inches(0.9 + idx * 6.25), Inches(2.2), Inches(5.25), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(16)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 6: PHASE 1 RECAP (Left Blue Card + Right Real Phone Radar Mockup)
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_top_bar(s6, "06")
    add_slide_header(s6, "PHASE 1 RECAP: CORE FOUNDATION")

    c6 = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c6.fill.solid()
    c6.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    c6.line.color.rgb = COLOR_WHITE
    c6.line.width = Pt(3.5)

    add_head_outline_box(s6, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "AUTONOMOUS P2P MESH CORE", True)

    c6_tf = c6.text_frame
    c6_tf.word_wrap = True
    c6_tf.margin_left = Inches(0.4)
    c6_tf.margin_right = Inches(0.4)
    c6_tf.margin_top = Inches(1.0)

    pts6 = [
        "Built Wi-Fi Direct auto-discovery without routers or cellular data.",
        "Implemented dynamic Group Owner negotiation & multi-hop message forwarding.",
        "Local Room database queues encrypted packets during disconnections.",
        "Automatic synchronization and delivery receipts once peer nodes reconnect."
    ]
    for idx, pt in enumerate(pts6):
        p = c6_tf.paragraphs[0] if idx == 0 else c6_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(12)
        r = p.add_run()
        r.text = "• " + pt
        r.font.name = FONT_BODY
        r.font.size = Pt(25)
        r.font.bold = True
        r.font.color.rgb = COLOR_WHITE

    radar_img = os.path.join(mock_dir, "phone_radar.png")
    if os.path.exists(radar_img):
        s6.shapes.add_picture(radar_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 7: SECTION BREAK
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_top_bar(s7, "07")

    break_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5.2))
    break_box.fill.solid()
    break_box.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    break_box.line.color.rgb = COLOR_WHITE
    break_box.line.width = Pt(4)
    btf = break_box.text_frame
    btf.word_wrap = True
    btf.margin_left = Inches(0.5)
    btf.margin_top = Inches(0.6)
    bp1 = btf.paragraphs[0]
    brun1 = bp1.add_run()
    brun1.text = "PHASE 2\nPILLARS"
    brun1.font.name = FONT_TITLE
    brun1.font.size = Pt(56)
    brun1.font.bold = True
    brun1.font.color.rgb = COLOR_WHITE

    r_break = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.6), Inches(1.5), Inches(6.1), Inches(5.2))
    r_break.fill.solid()
    r_break.fill.fore_color.rgb = COLOR_WHITE
    r_break.line.color.rgb = COLOR_ROYAL_BLUE
    r_break.line.width = Pt(4)
    rtf2 = r_break.text_frame
    rtf2.word_wrap = True
    rtf2.margin_left = Inches(0.5)
    rtf2.margin_top = Inches(0.6)

    pillars = [
        "1. 100% Offline Qwen LLM",
        "2. Real-Time Voice & Video",
        "3. Zero-Install Web Portal"
    ]
    for idx, pill in enumerate(pillars):
        p = rtf2.paragraphs[0] if idx == 0 else rtf2.add_paragraph()
        if idx > 0:
            p.space_before = Pt(28)
        r = p.add_run()
        r.text = pill
        r.font.name = FONT_BODY
        r.font.size = Pt(28)
        r.font.bold = True
        r.font.color.rgb = COLOR_ROYAL_BLUE

    # -------------------------------------------------------------------------
    # SLIDE 8: P2P OFFLINE CALLS (Left Card + Right Real Phone Call Mockup)
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_top_bar(s8, "08")
    add_slide_header(s8, "PHASE 2: ULTRA LOW-LATENCY P2P CALLS")

    c8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c8.fill.solid()
    c8.fill.fore_color.rgb = COLOR_WHITE
    c8.line.color.rgb = COLOR_ROYAL_BLUE
    c8.line.width = Pt(3.5)

    add_head_outline_box(s8, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "HD AUDIO & VIDEO PIPELINE", False)

    c8_tf = c8.text_frame
    c8_tf.word_wrap = True
    c8_tf.margin_left = Inches(0.4)
    c8_tf.margin_right = Inches(0.4)
    c8_tf.margin_top = Inches(1.0)

    points_s8 = [
        "Direct Socket: Real-time peer audio streaming",
        "Acoustic Cancel: Hardware echo elimination",
        "Sub-45ms Latency: Studio duplex voice",
        "Adaptive Bitrate: H.264 hardware encoding"
    ]
    for idx, pt in enumerate(points_s8):
        p = c8_tf.paragraphs[0] if idx == 0 else c8_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(12)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLACK_TEXT

    call_img = os.path.join(mock_dir, "phone_call.png")
    if os.path.exists(call_img):
        s8.shapes.add_picture(call_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 9: ON-DEVICE QWEN AI (Left Card + Right Phone Mockup Qwen AI)
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_top_bar(s9, "09")
    add_slide_header(s9, "PHASE 2: ON-DEVICE QWEN AI ARCHITECTURE")

    c9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c9.fill.solid()
    c9.fill.fore_color.rgb = COLOR_WHITE
    c9.line.color.rgb = COLOR_ROYAL_BLUE
    c9.line.width = Pt(3.5)

    add_head_outline_box(s9, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "NATIVE LLAMA.CPP RUNTIME", False)

    c9_tf = c9.text_frame
    c9_tf.word_wrap = True
    c9_tf.margin_left = Inches(0.4)
    c9_tf.margin_right = Inches(0.4)
    c9_tf.margin_top = Inches(1.0)

    points_s9 = [
        "Embedded libllama C++ core executing on CPU",
        "Qwen3 1.7B Q4_K_M GGUF model runs offline",
        "Unlimited response length (no truncation)",
        "Deep reasoning accordion view for transparency"
    ]
    for idx, pt in enumerate(points_s9):
        p = c9_tf.paragraphs[0] if idx == 0 else c9_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(12)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLACK_TEXT

    qwen_img = os.path.join(mock_dir, "phone_qwen.png")
    if os.path.exists(qwen_img):
        s9.shapes.add_picture(qwen_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 10: TRI-MODE AI SELECTOR (3 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_top_bar(s10, "10")
    add_slide_header(s10, "PHASE 2: DUAL-ENGINE AI SELECTOR")

    modes = [
        ("PURE QWEN AI", [
            "On-Device 1.7B LLM",
            "Complex medical triage",
            "Offline technical advice",
            "Deep multi-step reasoning"
        ]),
        ("DEFAULT INSTANT", [
            "Rule-based smart core",
            "Sub-millisecond speed",
            "Zero CPU & battery drain",
            "Instant command lookup"
        ]),
        ("HYBRID BALANCED", [
            "Dynamic query routing",
            "Auto-escalates to Qwen",
            "Optimizes battery life",
            "Best of both worlds"
        ])
    ]
    for idx, (head, points) in enumerate(modes):
        c = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.15), Inches(1.95), Inches(3.8), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s10, Inches(0.85 + idx * 4.15), Inches(2.2), Inches(3.3), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 11: LOCAL WEB GATEWAY (Left Card + Right Browser Mockup)
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_top_bar(s11, "11")
    add_slide_header(s11, "PHASE 2: LOCAL LAPTOP WEB GATEWAY")

    c11 = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c11.fill.solid()
    c11.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    c11.line.color.rgb = COLOR_WHITE
    c11.line.width = Pt(3.5)

    add_head_outline_box(s11, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "PORT 8080 LOCAL SERVER", True)

    c11_tf = c11.text_frame
    c11_tf.word_wrap = True
    c11_tf.margin_left = Inches(0.4)
    c11_tf.margin_right = Inches(0.4)
    c11_tf.margin_top = Inches(1.0)

    points_s11 = [
        "Built-in HTTP daemon serves chat UI directly to laptop browsers.",
        "Real-time WebSocket bridge streams mesh text and alerts in real-time.",
        "Incident commanders join mesh immediately without installing any software."
    ]
    for idx, pt in enumerate(points_s11):
        p = c11_tf.paragraphs[0] if idx == 0 else c11_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(14)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE

    browser_img = os.path.join(mock_dir, "browser_mockup.png")
    if os.path.exists(browser_img):
        s11.shapes.add_picture(browser_img, Inches(7.9), Inches(1.95), Inches(4.9), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 12: PHASE 3 UI/UX DESIGN SYSTEM (2 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_top_bar(s12, "12")
    add_slide_header(s12, "PHASE 3: UI/UX DESIGN PHILOSOPHY")

    cards_s12 = [
        ("EMERGENCY-FIRST INTERFACE", [
            "High-contrast card containers visible under harsh direct sunlight outdoors.",
            "One-handed thumb-zone layout for emergency calling and messaging."
        ]),
        ("TRANSPARENT SYSTEM STATUS", [
            "Live node count radar pill indicates active peers in current mesh range.",
            "Dedicated model switcher pill shows AI reasoning state and active engine."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s12):
        c = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.25), Inches(1.95), Inches(5.85), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s12, Inches(0.9 + idx * 6.25), Inches(2.2), Inches(5.25), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(16)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 13: DESIGN TOKENS & VISUAL PALETTE (3 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s13)
    add_top_bar(s13, "13")
    add_slide_header(s13, "PHASE 3: DESIGN TOKENS & PALETTE")

    tokens = [
        ("LIME ACCENT #7ED957", [
            "Primary energy accent",
            "Signals mesh connectivity",
            "Maximum outdoor contrast",
            "Eye-catching status badges"
        ]),
        ("ROYAL BLUE #12229D", [
            "Command container surface",
            "Clean content grounding",
            "Professional authority",
            "Zero eye strain readability"
        ]),
        ("SQUARE TYPOGRAPHY", [
            "Anton square block headers",
            "Inter / Segoe UI for body",
            "Minimum 25pt body sizing",
            "Ultra crisp field rendering"
        ])
    ]
    for idx, (head, points) in enumerate(tokens):
        c = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.15), Inches(1.95), Inches(3.8), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s13, Inches(0.85 + idx * 4.15), Inches(2.2), Inches(3.3), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 14: INTERACTIVE POLISH (Left Card + Right Phone Mockup Thought Process)
    # -------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14)
    add_top_bar(s14, "14")
    add_slide_header(s14, "PHASE 3: INTERACTIVE POLISH")

    c14 = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c14.fill.solid()
    c14.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    c14.line.color.rgb = COLOR_WHITE
    c14.line.width = Pt(3.5)

    add_head_outline_box(s14, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "THOUGHT ACCORDION & HAPTICS", True)

    c14_tf = c14.text_frame
    c14_tf.word_wrap = True
    c14_tf.margin_left = Inches(0.4)
    c14_tf.margin_right = Inches(0.4)
    c14_tf.margin_top = Inches(1.0)

    points_s14 = [
        "Users can tap to expand or collapse raw Qwen AI reasoning tokens.",
        "Ensures clean chat flow while giving full inspection into reasoning.",
        "Haptic pulses confirm packet transmission over multi-hop mesh links."
    ]
    for idx, pt in enumerate(points_s14):
        p = c14_tf.paragraphs[0] if idx == 0 else c14_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(14)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE

    thought_img = os.path.join(mock_dir, "phone_thought.png")
    if os.path.exists(thought_img):
        s14.shapes.add_picture(thought_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 15: HARDWARE TELEMETRY & BENCHMARKS (Left Card + Right Phone Oppo Mockup)
    # -------------------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s15)
    add_top_bar(s15, "15")
    add_slide_header(s15, "MULTI-DEVICE HARDWARE BENCHMARKS")

    c15 = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.95), Inches(7.0), Inches(5.15))
    c15.fill.solid()
    c15.fill.fore_color.rgb = COLOR_WHITE
    c15.line.color.rgb = COLOR_ROYAL_BLUE
    c15.line.width = Pt(3.5)

    add_head_outline_box(s15, Inches(0.9), Inches(2.2), Inches(6.4), Inches(0.6), "NOVA 1 5G & OPPO RENO2 F", False)

    c15_tf = c15.text_frame
    c15_tf.word_wrap = True
    c15_tf.margin_left = Inches(0.4)
    c15_tf.margin_right = Inches(0.4)
    c15_tf.margin_top = Inches(1.0)

    points_s15 = [
        "Qwen Inference: 14.2 tokens/second local speed",
        "Call Latency: 38ms end-to-end socket delay",
        "Thermal Stability: 38.4°C peak under sustained load",
        "Delivery Rate: 100% success rate across floors"
    ]
    for idx, pt in enumerate(points_s15):
        p = c15_tf.paragraphs[0] if idx == 0 else c15_tf.add_paragraph()
        if idx > 0:
            p.space_before = Pt(12)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_BLACK_TEXT

    oppo_img = os.path.join(mock_dir, "phone_oppo.png")
    if os.path.exists(oppo_img):
        s15.shapes.add_picture(oppo_img, Inches(8.1), Inches(1.95), Inches(4.6), Inches(5.15))

    # -------------------------------------------------------------------------
    # SLIDE 16: ZERO-TRUST SECURITY (2 Blue Cards with Outlines)
    # -------------------------------------------------------------------------
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s16)
    add_top_bar(s16, "16")
    add_slide_header(s16, "ZERO-TRUST SECURITY ARCHITECTURE")

    cards_s16 = [
        ("END-TO-END CRYPTOGRAPHY", [
            "Curve25519 ephemeral Diffie-Hellman key exchange for every peer session.",
            "AES-GCM-256 authenticated packet encryption protects text, voice & video."
        ]),
        ("ZERO CLOUD FOOTPRINT", [
            "No phone number, email or cloud account required to use the system.",
            "All intelligence runs on-device: zero queries ever leave the user's phone."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s16):
        c = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.25), Inches(1.95), Inches(5.85), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.color.rgb = COLOR_WHITE
        c.line.width = Pt(3.5)

        add_head_outline_box(s16, Inches(0.9 + idx * 6.25), Inches(2.2), Inches(5.25), Inches(0.6), head, True)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(16)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 17: PHASE 4 ROADMAP (2 White Cards with Outlines)
    # -------------------------------------------------------------------------
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s17)
    add_top_bar(s17, "17")
    add_slide_header(s17, "PHASE 4: FUTURE ROADMAP")

    cards_s17 = [
        ("LONG-RANGE LORA BRIDGE", [
            "Integrate sub-GHz LoRa modules to extend mesh range up to 10+ kilometers.",
            "Bridge high-speed Wi-Fi Direct clusters across mountains and valleys."
        ]),
        ("CROSS-PLATFORM ECOSYSTEM", [
            "Bring Nexus MeshLink to iOS devices using Multipeer Connectivity.",
            "Drone-mounted relay nodes for high-altitude disaster coverage."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s17):
        c = s17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.25), Inches(1.95), Inches(5.85), Inches(5.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3.5)

        add_head_outline_box(s17, Inches(0.9 + idx * 6.25), Inches(2.2), Inches(5.25), Inches(0.6), head, False)

        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(1.0)

        for p_idx, pt in enumerate(points):
            p = ctf.paragraphs[0] if p_idx == 0 else ctf.add_paragraph()
            if p_idx > 0:
                p.space_before = Pt(16)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.bold = True
            run.font.color.rgb = COLOR_BLACK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 18: THANK YOU & CONCLUSION
    # -------------------------------------------------------------------------
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s18)
    add_top_bar(s18, "18", "CONCLUSION & Q&A")

    left_ty = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.8), Inches(4.9))
    left_ty.fill.solid()
    left_ty.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    left_ty.line.color.rgb = COLOR_WHITE
    left_ty.line.width = Pt(3.5)
    ly_tf = left_ty.text_frame
    ly_tf.word_wrap = True
    ly_tf.margin_left = Inches(0.5)
    ly_tf.margin_right = Inches(0.5)
    ly_tf.margin_top = Inches(0.6)

    p1 = ly_tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = "PROJECT NEXUS"
    r1.font.name = FONT_TITLE
    r1.font.size = Pt(32)
    r1.font.bold = True
    r1.font.color.rgb = COLOR_WHITE

    p2 = ly_tf.add_paragraph()
    p2.space_before = Pt(16)
    r2 = p2.add_run()
    r2.text = "Phase 2 & Phase 3 Accomplished.\n\n100% On-Device AI • Low-Latency Duplex Calls • Production Canva UI/UX Architecture."
    r2.font.name = FONT_BODY
    r2.font.size = Pt(25)
    r2.font.bold = True
    r2.font.color.rgb = COLOR_LIGHT_LIME

    right_ty = s18.shapes.add_textbox(Inches(6.6), Inches(1.5), Inches(6.1), Inches(4.5))
    rtf_ty = right_ty.text_frame
    rtf_ty.word_wrap = True
    rp_ty = rtf_ty.paragraphs[0]
    rr_ty = rp_ty.add_run()
    rr_ty.text = "THANK\nYOU"
    rr_ty.font.name = FONT_TITLE
    rr_ty.font.size = Pt(80)
    rr_ty.font.bold = True
    rr_ty.font.color.rgb = COLOR_WHITE

    b_pill = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.35), Inches(5.8), Inches(0.7))
    b_pill.fill.solid()
    b_pill.fill.fore_color.rgb = COLOR_LIGHT_LIME
    b_pill.line.color.rgb = COLOR_ROYAL_BLUE
    b_pill.line.width = Pt(2.5)
    bptf = b_pill.text_frame
    bp = bptf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bprun = bp.add_run()
    bprun.text = "WWW.NEXUSAPP.OFFLINE"
    bprun.font.name = FONT_TITLE
    bprun.font.size = Pt(22)
    bprun.font.bold = True
    bprun.font.color.rgb = COLOR_ROYAL_BLUE

    # Save presentation
    out_path = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Canva_LimeBlue_Master_Final.pptx"
    prs.save(out_path)
    print("SUCCESS: Clean polished presentation saved to", out_path)

    # Apply SIMPLE, ELEGANT FADE TRANSITION (No crazy effects!)
    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
        pres = app.Presentations.Open(os.path.abspath(out_path), False, False, False)
        for idx in range(1, pres.Slides.Count + 1):
            slide = pres.Slides(idx)
            slide.SlideShowTransition.EntryEffect = 1025 # ppEffectFade (Clean, subtle fade)
            slide.SlideShowTransition.Duration = 0.35   # Fast, smooth 0.35s
            slide.SlideShowTransition.AdvanceOnClick = True
        pres.Save()
        pres.Close()
        app.Quit()
        print("SUCCESS: Clean subtle fade transitions applied!")
    except Exception as e:
        print("COM error:", e)

if __name__ == "__main__":
    create_clean_polished_deck()
