import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Exact colors from Canva template screenshot
    COLOR_LIME = RGBColor(126, 217, 87)       # #7ED957 (Canva bright lime green)
    COLOR_ROYAL_BLUE = RGBColor(18, 34, 157)  # #12229D (Canva royal blue)
    COLOR_WHITE = RGBColor(255, 255, 255)     # #FFFFFF
    COLOR_LIGHT_LIME = RGBColor(190, 242, 160)# #BEF2A0
    COLOR_DARK_TEXT = RGBColor(15, 23, 42)    # #0F172A

    FONT_TITLE = "Anton"
    FONT_BODY = "Inter"

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
        bar.line.fill.background()

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
        tb = slide.shapes.add_textbox(Inches(0.6), Inches(1.1), Inches(12.133), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0)
        tf.margin_top = Inches(0)
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title_text.upper()
        run.font.name = FONT_TITLE
        run.font.size = Pt(36)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 1: COVER SLIDE (Exact Canva Slide 1)
    # -------------------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)
    add_top_bar(s1, "01", "NEXUS MESHLINK ECOSYSTEM")

    # Left Dark Blue Box
    left_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.8), Inches(4.9))
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    left_box.line.fill.background()
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
    lrun2.font.color.rgb = COLOR_LIGHT_LIME

    # Right Giant White Title (Like "UI/UX" in Canva template)
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

    # Bottom Pill / URL Bar
    url_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.35), Inches(5.8), Inches(0.7))
    url_box.fill.solid()
    url_box.fill.fore_color.rgb = COLOR_LIGHT_LIME
    url_box.line.fill.background()
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
    # SLIDE 2: WHAT IS NEXUS MESHLINK? (Left Card + Right Feature Box)
    # -------------------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_top_bar(s2, "02")
    add_slide_header(s2, "WHAT IS NEXUS MESHLINK?")

    c2_left = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.0), Inches(6.4), Inches(5.1))
    c2_left.fill.solid()
    c2_left.fill.fore_color.rgb = COLOR_WHITE
    c2_left.line.color.rgb = COLOR_ROYAL_BLUE
    c2_left.line.width = Pt(3)
    c2_ltf = c2_left.text_frame
    c2_ltf.word_wrap = True
    c2_ltf.margin_left = Inches(0.4)
    c2_ltf.margin_right = Inches(0.4)
    c2_ltf.margin_top = Inches(0.35)
    
    p = c2_ltf.paragraphs[0]
    r = p.add_run()
    r.text = "THE REVOLUTIONARY PLATFORM"
    r.font.name = FONT_TITLE
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = COLOR_ROYAL_BLUE

    pts2 = [
        "100% decentralized P2P Wi-Fi mesh connecting phones directly up to 250 Mbps.",
        "Zero dependency on cellular towers, internet backbones, or Wi-Fi routers.",
        "Equipped with embedded offline Qwen AI intelligence and encrypted calling."
    ]
    for pt in pts2:
        p = c2_ltf.add_paragraph()
        p.space_before = Pt(12)
        r = p.add_run()
        r.text = "• " + pt
        r.font.name = FONT_BODY
        r.font.size = Pt(25)
        r.font.color.rgb = COLOR_DARK_TEXT

    # Right Feature Card
    c2_right = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.2), Inches(2.0), Inches(5.5), Inches(5.1))
    c2_right.fill.solid()
    c2_right.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    c2_right.line.fill.background()
    c2_rtf = c2_right.text_frame
    c2_rtf.word_wrap = True
    c2_rtf.margin_left = Inches(0.4)
    c2_rtf.margin_right = Inches(0.4)
    c2_rtf.margin_top = Inches(0.4)

    p = c2_rtf.paragraphs[0]
    r = p.add_run()
    r.text = "CORE CAPABILITIES"
    r.font.name = FONT_TITLE
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = COLOR_LIGHT_LIME

    r_pts2 = [
        "Instant Wi-Fi Direct Peer Discovery",
        "Autonomous Group Owner Negotiation",
        "Multi-Hop Gossip Packet Forwarding",
        "Store & Forward Disconnected Sync"
    ]
    for pt in r_pts2:
        p = c2_rtf.add_paragraph()
        p.space_before = Pt(14)
        r = p.add_run()
        r.text = "✓ " + pt
        r.font.name = FONT_BODY
        r.font.size = Pt(25)
        r.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 3: INFRASTRUCTURE FAILURES (2 Side-by-Side Cards)
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
        c = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.fill.background()
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_LIGHT_LIME

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 4: EXISTING APPS ANALYSIS (3 White Cards)
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
        c = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.1), Inches(2.0), Inches(3.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.25)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(26)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 5: WHY OUR APP IS BEST (2 White Cards)
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
        c = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 6: PHASE 1 RECAP (2 Blue Cards)
    # -------------------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_top_bar(s6, "06")
    add_slide_header(s6, "PHASE 1 RECAP: CORE FOUNDATION")

    cards_s6 = [
        ("AUTONOMOUS P2P MESH CORE", [
            "Built Wi-Fi Direct auto-discovery without routers or cellular data.",
            "Implemented dynamic Group Owner negotiation & multi-hop message forwarding."
        ]),
        ("STORE & FORWARD PROTOCOL", [
            "Local Room database queues encrypted packets during disconnections.",
            "Automatic synchronization and delivery receipts once peer nodes reconnect."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s6):
        c = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.fill.background()
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_LIGHT_LIME

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 7: SECTION BREAK (Canva Slide 7 Style with Green Canvas)
    # -------------------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_top_bar(s7, "07")

    break_box = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.5), Inches(5.8), Inches(5.2))
    break_box.fill.solid()
    break_box.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    break_box.line.fill.background()
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

    # Right Card with list
    r_break = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.6), Inches(1.5), Inches(6.1), Inches(5.2))
    r_break.fill.solid()
    r_break.fill.fore_color.rgb = COLOR_WHITE
    r_break.line.color.rgb = COLOR_ROYAL_BLUE
    r_break.line.width = Pt(3)
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
    # SLIDE 8: P2P OFFLINE CALLS (2 White Cards)
    # -------------------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_top_bar(s8, "08")
    add_slide_header(s8, "PHASE 2: ULTRA LOW-LATENCY P2P CALLS")

    cards_s8 = [
        ("48kHz HD AUDIO PIPELINE", [
            "Direct Socket: Real-time peer audio streaming",
            "Acoustic Cancel: Hardware echo elimination",
            "Sub-45ms Latency: Studio duplex voice",
            "Audio Routing: Dynamic speakerphone toggle"
        ]),
        ("720p 30fps VIDEO ENGINE", [
            "H.264 Codec: Hardware-accelerated encoding",
            "Dynamic View: Front & back camera toggling",
            "Adaptive Bitrate: Auto-adjusts to Wi-Fi signal",
            "100% Private: Peer-to-peer encrypted stream"
        ])
    ]
    for idx, (head, points) in enumerate(cards_s8):
        c = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.3)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 9: ON-DEVICE QWEN AI ARCHITECTURE (Card + Real Phone Screenshot)
    # -------------------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_top_bar(s9, "09")
    add_slide_header(s9, "PHASE 2: ON-DEVICE QWEN AI ARCHITECTURE")

    c9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(2.0), Inches(6.8), Inches(5.1))
    c9.fill.solid()
    c9.fill.fore_color.rgb = COLOR_WHITE
    c9.line.color.rgb = COLOR_ROYAL_BLUE
    c9.line.width = Pt(3)
    c9_tf = c9.text_frame
    c9_tf.word_wrap = True
    c9_tf.margin_left = Inches(0.4)
    c9_tf.margin_right = Inches(0.4)
    c9_tf.margin_top = Inches(0.3)

    c9_hp = c9_tf.paragraphs[0]
    c9_hrun = c9_hp.add_run()
    c9_hrun.text = "NATIVE LLAMA.CPP RUNTIME"
    c9_hrun.font.name = FONT_TITLE
    c9_hrun.font.size = Pt(28)
    c9_hrun.font.bold = True
    c9_hrun.font.color.rgb = COLOR_ROYAL_BLUE

    points_s9 = [
        "Embedded libllama C++ core executing on CPU",
        "Qwen3 1.7B Q4_K_M GGUF model runs offline",
        "Unlimited response length (no truncation)",
        "Deep reasoning accordion view for transparency"
    ]
    for pt in points_s9:
        p = c9_tf.add_paragraph()
        p.space_before = Pt(10)
        run = p.add_run()
        run.text = "• " + pt
        run.font.name = FONT_BODY
        run.font.size = Pt(25)
        run.font.color.rgb = COLOR_DARK_TEXT

    shot_path = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\long_answer_complete.png"
    if os.path.exists(shot_path):
        p_frame = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(2.0), Inches(4.9), Inches(5.1))
        p_frame.fill.solid()
        p_frame.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        p_frame.line.fill.background()
        s9.shapes.add_picture(shot_path, Inches(7.95), Inches(2.15), Inches(4.6), Inches(4.8))

    # -------------------------------------------------------------------------
    # SLIDE 10: TRI-MODE AI SELECTOR (3 White Cards)
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
        c = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.1), Inches(2.0), Inches(3.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.25)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(26)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 11: LOCAL WEB GATEWAY (2 Blue Cards)
    # -------------------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_top_bar(s11, "11")
    add_slide_header(s11, "PHASE 2: LOCAL LAPTOP WEB GATEWAY")

    cards_s11 = [
        ("PORT 8080 LOCAL SERVER", [
            "Built-in HTTP daemon serves responsive chat UI directly to laptop browsers.",
            "Real-time WebSocket bridge streams mesh text and alerts in real-time."
        ]),
        ("ZERO-INSTALL RESCUE DESK", [
            "Incident commanders join the mesh immediately without installing any software.",
            "Enables disaster command centers to coordinate teams from laptops."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s11):
        c = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.fill.background()
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_LIGHT_LIME

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 12: PHASE 3 UI/UX DESIGN SYSTEM (2 White Cards)
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
        c = s12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 13: DESIGN TOKENS & VISUAL PALETTE (3 White Cards)
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
        c = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 4.1), Inches(2.0), Inches(3.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.25)
        ctf.margin_right = Inches(0.25)
        ctf.margin_top = Inches(0.25)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(24)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 14: INTERACTIVE POLISH (2 Blue Cards)
    # -------------------------------------------------------------------------
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14)
    add_top_bar(s14, "14")
    add_slide_header(s14, "PHASE 3: INTERACTIVE POLISH")

    cards_s14 = [
        ("THOUGHT ACCORDION", [
            "Users can tap to expand or collapse raw Qwen AI reasoning tokens.",
            "Ensures clean chat flow while giving full inspection into the AI thought chain."
        ]),
        ("FEEDBACK & TOASTS", [
            "Haptic pulses confirm packet transmission over multi-hop mesh links.",
            "Real-time visual toasts show node discovery and call connection states."
        ])
    ]
    for idx, (head, points) in enumerate(cards_s14):
        c = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.fill.background()
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_LIGHT_LIME

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 15: HARDWARE TELEMETRY & BENCHMARKS (2 White Cards)
    # -------------------------------------------------------------------------
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s15)
    add_top_bar(s15, "15")
    add_slide_header(s15, "MULTI-DEVICE HARDWARE BENCHMARKS")

    cards_s15 = [
        ("NOVA 1 5G (DIMENSITY 7050)", [
            "Qwen Inference: 14.2 tokens/second local speed",
            "Call Latency: 38ms end-to-end socket delay",
            "Thermal Stability: 38.4°C peak under sustained load",
            "RAM Consumption: 1.8 GB during full LLM generation"
        ]),
        ("OPPO RENO2 F (HELIO P70)", [
            "Mesh Discovery: Connected in under 2.3 seconds",
            "Packet Delivery: 100% success rate over 1 hour",
            "Battery Impact: <4% per hour active mesh listening",
            "Cross-Device Call: Zero frame loss verified"
        ])
    ]
    for idx, (head, points) in enumerate(cards_s15):
        c = s15.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.3)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(26)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(10)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 16: ZERO-TRUST SECURITY (2 Blue Cards)
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
        c = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_ROYAL_BLUE
        c.line.fill.background()
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_LIGHT_LIME

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------------------
    # SLIDE 17: PHASE 4 ROADMAP (2 White Cards)
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
        c = s17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6 + idx * 6.2), Inches(2.0), Inches(5.9), Inches(5.1))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_WHITE
        c.line.color.rgb = COLOR_ROYAL_BLUE
        c.line.width = Pt(3)
        ctf = c.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.4)
        ctf.margin_right = Inches(0.4)
        ctf.margin_top = Inches(0.35)
        
        hp = ctf.paragraphs[0]
        hrun = hp.add_run()
        hrun.text = head
        hrun.font.name = FONT_TITLE
        hrun.font.size = Pt(28)
        hrun.font.bold = True
        hrun.font.color.rgb = COLOR_ROYAL_BLUE

        for pt in points:
            p = ctf.add_paragraph()
            p.space_before = Pt(14)
            run = p.add_run()
            run.text = "• " + pt
            run.font.name = FONT_BODY
            run.font.size = Pt(25)
            run.font.color.rgb = COLOR_DARK_TEXT

    # -------------------------------------------------------------------------
    # SLIDE 18: THANK YOU & CONCLUSION (Exact Canva Slide 10 Style)
    # -------------------------------------------------------------------------
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s18)
    add_top_bar(s18, "18", "CONCLUSION & Q&A")

    # Left Blue Box
    left_ty = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.3), Inches(5.8), Inches(4.9))
    left_ty.fill.solid()
    left_ty.fill.fore_color.rgb = COLOR_ROYAL_BLUE
    left_ty.line.fill.background()
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
    r2.font.color.rgb = COLOR_LIGHT_LIME

    # Right Giant White "THANK YOU"
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

    # Bottom Pill
    b_pill = s18.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.35), Inches(5.8), Inches(0.7))
    b_pill.fill.solid()
    b_pill.fill.fore_color.rgb = COLOR_LIGHT_LIME
    b_pill.line.fill.background()
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
    out_path = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Canva_LimeBlue_Presentation.pptx"
    prs.save(out_path)
    print("SUCCESS: Deck created at", out_path)

if __name__ == "__main__":
    build_deck()
