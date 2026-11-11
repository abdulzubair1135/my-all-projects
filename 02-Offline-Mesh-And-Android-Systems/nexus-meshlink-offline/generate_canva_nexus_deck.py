import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_canva_nexus_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # =========================================================================
    # CANVA STYLE PALETTE & ASSETS
    # =========================================================================
    COLOR_CARD_WHITE = RGBColor(255, 255, 255)       # Pure crisp card surface
    COLOR_SHADOW = RGBColor(218, 230, 222)           # Soft mint-gray Canva shadow
    COLOR_BORDER_EMERALD = RGBColor(16, 185, 129)    # #10B981 Emerald
    COLOR_BORDER_MINT = RGBColor(167, 243, 208)      # #A7F3D0 Soft Mint
    COLOR_EMERALD_DARK = RGBColor(6, 95, 70)         # #065F46 Deep Emerald
    COLOR_FOREST = RGBColor(4, 120, 87)              # #047857 Forest
    COLOR_SLATE_DARK = RGBColor(15, 23, 42)          # #0F172A Primary obsidian text
    COLOR_SLATE_MUTED = RGBColor(71, 85, 105)        # #475569 Secondary text
    COLOR_PILL_BG = RGBColor(220, 252, 231)          # #DCFCE7 Mint badge pill
    COLOR_RED_ALERT = RGBColor(220, 38, 38)          # #DC2626 Warning
    COLOR_BLUE_ACCENT = RGBColor(37, 99, 235)        # #2563EB Tech Blue

    # Background images generated in Canva aesthetic
    BG_COVER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\canva_cover_bg_1791491116035.jpg"
    BG_CONTENT = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\canva_content_bg_1791491086705.jpg"

    # Screenshot assets
    IMG_LONG_ANSWER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\long_answer_complete.png"
    IMG_BROWSER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\browser_tab_live.png"
    IMG_MODE_DIALOG = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\mode_selector_dialog_live.png"
    IMG_OPPO = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\oppo_latest_app.png"

    blank_layout = prs.slide_layouts[6]

    # Helper: Set Canva Background
    def set_slide_bg(slide, is_cover=False, slide_num=1):
        bg_path = BG_COVER if is_cover else BG_CONTENT
        if os.path.exists(bg_path):
            try:
                slide.shapes.add_picture(bg_path, 0, 0, width=Inches(13.333), height=Inches(7.5))
            except Exception:
                pass

        if not is_cover:
            # Subtle slide indicator at bottom
            foot = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.15), Inches(12.133), Inches(0.25))
            foot.fill.background()
            foot.line.fill.background()
            ftf = foot.text_frame
            fp = ftf.paragraphs[0]
            fp.text = f"NEXUS MESHLINK  •  CANVA MASTER DECK  •  SLIDE {slide_num:02d} / 18"
            fp.font.size = Pt(11)
            fp.font.bold = True
            fp.font.color.rgb = COLOR_SLATE_MUTED

    # Helper: Canva Header (Floating Pill Title Bar)
    def add_canva_header(slide, title_text, category_tag="PHASE 2 & 3"):
        # Shadow
        h_shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.64), Inches(0.36), Inches(12.133), Inches(0.96))
        h_shadow.fill.solid()
        h_shadow.fill.fore_color.rgb = COLOR_SHADOW
        h_shadow.line.fill.background()

        # Main Header Card
        h_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.32), Inches(12.133), Inches(0.96))
        h_card.fill.solid()
        h_card.fill.fore_color.rgb = COLOR_CARD_WHITE
        h_card.line.color.rgb = COLOR_BORDER_EMERALD
        h_card.line.width = Pt(2.2)

        tf = h_card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(2.8)

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(28)  # Strictly > 25 pt
        p.font.bold = True
        p.font.color.rgb = COLOR_EMERALD_DARK

        # Category Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.15), Inches(0.48), Inches(2.35), Inches(0.64))
        pill.fill.solid()
        pill.fill.fore_color.rgb = COLOR_PILL_BG
        pill.line.color.rgb = COLOR_BORDER_EMERALD
        pill.line.width = Pt(1.5)

        ptf = pill.text_frame
        ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = ptf.paragraphs[0]
        pp.text = category_tag
        pp.alignment = PP_ALIGN.CENTER
        pp.font.size = Pt(13)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_EMERALD_DARK

    # Helper: Canva Floating Glassmorphic Card (Font >= 25)
    def add_canva_card(slide, left, top, width, height, title, items, 
                       border_color=COLOR_BORDER_EMERALD, title_color=COLOR_EMERALD_DARK, step_badge=None):
        # 1. Soft Shadow
        s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.06), Inches(top + 0.07), Inches(width), Inches(height))
        s.fill.solid()
        s.fill.fore_color.rgb = COLOR_SHADOW
        s.line.fill.background()

        # 2. Main White Frosted Card
        c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_WHITE
        c.line.color.rgb = border_color
        c.line.width = Pt(2.2)

        # 3. Optional Step Badge Pill (e.g. [ 01 ], [ 02 ])
        if step_badge:
            b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.28), Inches(top + 0.22), Inches(0.9), Inches(0.42))
            b.fill.solid()
            b.fill.fore_color.rgb = COLOR_PILL_BG
            b.line.color.rgb = border_color
            b.line.width = Pt(1.2)
            btf = b.text_frame
            btf.vertical_anchor = MSO_ANCHOR.MIDDLE
            bp = btf.paragraphs[0]
            bp.text = step_badge
            bp.alignment = PP_ALIGN.CENTER
            bp.font.size = Pt(13)
            bp.font.bold = True
            bp.font.color.rgb = title_color

        # 4. Text Frame
        tf = c.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.32)
        tf.margin_top = Inches(0.68 if step_badge else 0.24)
        tf.margin_right = Inches(0.32)
        tf.margin_bottom = Inches(0.15)

        # Title
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(26)  # Strictly > 25 pt
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(10)

        # Bullets (Strictly >= 25 pt)
        for item in items:
            p = tf.add_paragraph()
            p.text = item
            p.font.size = Pt(25)  # Exact constraint >= 25 pt
            p.font.bold = False
            p.font.color.rgb = COLOR_SLATE_DARK
            p.space_after = Pt(8)

    # Helper: Compact Quadrant Card for 4-Card Slides (No overflow)
    def add_canva_quadrant_card(slide, left, top, width, height, title, items, 
                                border_color=COLOR_BORDER_EMERALD, title_color=COLOR_EMERALD_DARK):
        s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.05), Inches(top + 0.06), Inches(width), Inches(height))
        s.fill.solid()
        s.fill.fore_color.rgb = COLOR_SHADOW
        s.line.fill.background()

        c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_WHITE
        c.line.color.rgb = border_color
        c.line.width = Pt(2.0)

        tf = c.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.26)
        tf.margin_top = Inches(0.14)
        tf.margin_right = Inches(0.26)
        tf.margin_bottom = Inches(0.08)

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(25)  # Strictly >= 25 pt
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(4)

        for item in items:
            p = tf.add_paragraph()
            p.text = item
            p.font.size = Pt(25)  # Strictly >= 25 pt
            p.font.bold = False
            p.font.color.rgb = COLOR_SLATE_DARK
            p.space_after = Pt(4)

    # Helper: Sleek Phone Mockup Frame
    def add_canva_phone_mockup(slide, left, top, width, height, img_path):
        s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.06), Inches(top + 0.07), Inches(width), Inches(height))
        s.fill.solid()
        s.fill.fore_color.rgb = COLOR_SHADOW
        s.line.fill.background()

        bezel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        bezel.fill.solid()
        bezel.fill.fore_color.rgb = COLOR_CARD_WHITE
        bezel.line.color.rgb = COLOR_BORDER_EMERALD
        bezel.line.width = Pt(2.5)

        if os.path.exists(img_path):
            try:
                slide.shapes.add_picture(img_path, Inches(left + 0.18), Inches(top + 0.20), width=Inches(width - 0.36), height=Inches(height - 0.40))
            except Exception:
                pass

    # =========================================================================
    # SLIDE 1: Canva Welcome / Cover Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, is_cover=True, slide_num=1)

    # Hero Glass Card on Right side of Cover
    c1_s = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.66), Inches(1.16), Inches(7.1), Inches(5.3))
    c1_s.fill.solid()
    c1_s.fill.fore_color.rgb = COLOR_SHADOW
    c1_s.line.fill.background()

    c1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.6), Inches(1.1), Inches(7.1), Inches(5.3))
    c1.fill.solid()
    c1.fill.fore_color.rgb = COLOR_CARD_WHITE
    c1.line.color.rgb = COLOR_BORDER_EMERALD
    c1.line.width = Pt(3.0)

    c1_tf = c1.text_frame
    c1_tf.word_wrap = True
    c1_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    c1_tf.margin_left = Inches(0.5)
    c1_tf.margin_right = Inches(0.5)

    p1 = c1_tf.paragraphs[0]
    p1.text = "NEXUS MESHLINK"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_SLATE_DARK
    p1.space_after = Pt(8)

    p2 = c1_tf.add_paragraph()
    p2.text = "The Offline AI Networking Ecosystem"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_EMERALD_DARK
    p2.space_after = Pt(10)

    p3 = c1_tf.add_paragraph()
    p3.text = "Phase 2 & Phase 3 Master Architecture"
    p3.font.size = Pt(25)
    p3.font.color.rgb = COLOR_FOREST
    p3.font.bold = True
    p3.space_after = Pt(12)

    p4 = c1_tf.add_paragraph()
    p4.text = "Empowering Off-Grid Life-Saving Communication When All Networks Fail"
    p4.font.size = Pt(25)
    p4.font.color.rgb = COLOR_SLATE_MUTED

    # 4 Feature Badges at bottom
    badges = [
        ("💬 Offline Chat", 5.8),
        ("📞 Secure Calls", 7.6),
        ("🌐 Web Portal", 9.4),
        ("🧠 On-Device AI", 11.2)
    ]
    for b_text, left_pos in badges:
        bp = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_pos), Inches(6.55), Inches(1.7), Inches(0.52))
        bp.fill.solid()
        bp.fill.fore_color.rgb = COLOR_PILL_BG
        bp.line.color.rgb = COLOR_BORDER_EMERALD
        bp.line.width = Pt(1.5)
        btf = bp.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bpp = btf.paragraphs[0]
        bpp.text = b_text
        bpp.alignment = PP_ALIGN.CENTER
        bpp.font.size = Pt(13)
        bpp.font.bold = True
        bpp.font.color.rgb = COLOR_EMERALD_DARK

    # =========================================================================
    # SLIDE 2: Executive Recap of Phase 1
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, slide_num=2)
    add_canva_header(s2, "📋 Recap: What Was Achieved in Phase 1?", "PHASE 1 RECAP")

    add_canva_card(s2, 0.6, 1.55, 5.9, 5.4, "Core Mesh Foundations", [
        "• BLE Discovery: Sub-second peer beaconing",
        "• Wi-Fi Direct: High-bandwidth P2P sockets",
        "• Multi-Hop: 3+ node packet relaying",
        "• Decentralized: Zero central server reliance"
    ], step_badge="STEP 01")

    add_canva_card(s2, 6.8, 1.55, 5.9, 5.4, "Essential Communication", [
        "• Encrypted Chat: End-to-end secure texts",
        "• Offline Transfers: Files & image sharing",
        "• Battery Saver: Low-power BLE background sleep",
        "• Compatibility: Android 10 through 15 ready"
    ], step_badge="STEP 02")

    # =========================================================================
    # SLIDE 3: Phase 1 Gaps & Why Phase 2 Was Born
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, slide_num=3)
    add_canva_header(s3, "⚡ Evolution: Moving from Phase 1 to Phase 2", "TRANSITION")

    add_canva_card(s3, 0.6, 1.55, 5.9, 5.4, "Phase 1 Bottlenecks", [
        "• Text Only: Zero voice or video calling",
        "• No Intelligence: Lacked on-device reasoning",
        "• Disaster Blind: No medical/triage guidance",
        "• Isolation: No link to laptop command hubs"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT, step_badge="LIMITS")

    add_canva_card(s3, 6.8, 1.55, 5.9, 5.4, "Phase 2 Mission Upgrades", [
        "• Real-Time Voice: 48kHz HD duplex calling",
        "• On-Device AI: Native Qwen3 LLM integration",
        "• Laptop Portal: Off-grid HTTP hub on port 8888",
        "• SOS Shield: Instant 112 & mesh broadcast"
    ], step_badge="UPGRADES")

    # =========================================================================
    # SLIDE 4: Existing & Similar Apps Landscape
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, slide_num=4)
    add_canva_header(s4, "🔍 Existing Offline Apps & Industry Landscape", "MARKET ANALYSIS")

    add_canva_card(s4, 0.6, 1.55, 3.8, 5.4, "Bridgefy", [
        "• Bluetooth mesh only",
        "• Proprietary protocol",
        "• No voice or video calls",
        "• Zero local intelligence"
    ], step_badge="APP 01")

    add_canva_card(s4, 4.75, 1.55, 3.8, 5.4, "Briar Messaging", [
        "• Heavy Tor dependence",
        "• High battery & CPU drain",
        "• Sluggish message sync",
        "• Text-only communication"
    ], step_badge="APP 02")

    add_canva_card(s4, 8.9, 1.55, 3.8, 5.4, "Meshtastic", [
        "• Requires $60 LoRa radio",
        "• Tiny bandwidth (bytes/sec)",
        "• Cannot stream media/voice",
        "• Complex hardware setup"
    ], step_badge="APP 03")

    # =========================================================================
    # SLIDE 5: Deep Competitive Analysis Matrix
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, slide_num=5)
    add_canva_header(s5, "📊 Detailed Competitive Analysis Matrix", "BENCHMARK")

    add_canva_card(s5, 0.6, 1.55, 5.9, 5.4, "Traditional Offline Apps", [
        "• Voice/Video: Completely unsupported",
        "• AI Reasoning: 100% Cloud-dependent",
        "• Hardware: Expensive external radio dongles",
        "• Desktop Link: No off-grid browser station"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT, step_badge="LEGACY")

    add_canva_card(s5, 6.8, 1.55, 5.9, 5.4, "Nexus MeshLink Dominance", [
        "• Calls: 48kHz HD Audio & 720p Video",
        "• Local AI: On-Device Qwen3 (0.6B to 4B)",
        "• Zero Cost: Runs on everyday smartphones",
        "• Command Hub: Built-in laptop portal (8888)"
    ], step_badge="NEXUS")

    # =========================================================================
    # SLIDE 6: Why Nexus MeshLink is Best & Universal
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, slide_num=6)
    add_canva_header(s6, "🌟 Why Nexus MeshLink is Best & Universal", "VALUE PROPOSITION")

    add_canva_card(s6, 0.6, 1.55, 5.9, 5.4, "Small Brain + Mighty Tools", [
        "• Smart Routing: Instant intent classification",
        "• Deterministic: Offline tools execute flawlessly",
        "• Multi-Lingual: Hinglish, Hindi & English",
        "• Adaptive: Auto-picks 0.6B, 1.7B, or 4B tier"
    ], step_badge="AI BRAIN")

    add_canva_card(s6, 6.8, 1.55, 5.9, 5.4, "Universal Life-Saving Utility", [
        "• 100% Free: No SIM recharge or cellular data",
        "• Zero Infrastructure: Works in deep blackouts",
        "• Intuitive: Designed for non-technical users",
        "• Inclusive: Smooth on budget & flagship phones"
    ], step_badge="UTILITY")

    # =========================================================================
    # SLIDE 7: Critical Real-World Use Cases (4 Quadrants)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, slide_num=7)
    add_canva_header(s7, "🎯 Critical Real-World Use Cases", "APPLICATIONS")

    add_canva_quadrant_card(s7, 0.6, 1.48, 5.9, 2.70, "🚨 Disaster Relief Zones", [
        "• Floods & quakes destroying cell towers",
        "• Instant GPS triage beacon & SOS rescue"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_canva_quadrant_card(s7, 6.8, 1.48, 5.9, 2.70, "🏕️ Remote Expeditions & Defense", [
        "• Mountain hiking, dense forests & borders",
        "• Off-grid tactical squad voice & survival AI"
    ])

    add_canva_quadrant_card(s7, 0.6, 4.34, 5.9, 2.70, "🎪 Crowded Public Gatherings", [
        "• Stadiums & festival rallies with tower overload",
        "• Free off-grid peer chat & rendezvous alerts"
    ], border_color=COLOR_BLUE_ACCENT, title_color=COLOR_BLUE_ACCENT)

    add_canva_quadrant_card(s7, 6.8, 4.34, 5.9, 2.70, "🏫 Off-Grid Rural Communities", [
        "• Remote villages lacking cellular networks",
        "• Educational file sharing & offline clinic docs"
    ], border_color=COLOR_FOREST, title_color=COLOR_FOREST)

    # =========================================================================
    # SLIDE 8: Phase 2 Breakthrough: Real-Time Voice & Video Calls
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8, slide_num=8)
    add_canva_header(s8, "📞 Phase 2: Ultra Low-Latency P2P Calls", "VOICE & VIDEO")

    add_canva_card(s8, 0.6, 1.55, 5.9, 5.4, "48kHz HD Audio Pipeline", [
        "• Direct Socket: Real-time peer audio streaming",
        "• Acoustic Cancel: Hardware echo elimination",
        "• Sub-45ms Latency: Studio-quality duplex audio",
        "• Audio Routing: Dynamic speaker/earpiece switch"
    ], step_badge="VOICE")

    add_canva_card(s8, 6.8, 1.55, 5.9, 5.4, "720p 30fps Video Engine", [
        "• H.264 Codec: Hardware-accelerated encoding",
        "• Dynamic View: Front & back camera toggling",
        "• Adaptive Bitrate: Auto-adjusts to Wi-Fi signal",
        "• 100% Private: Peer-to-peer encrypted stream"
    ], step_badge="VIDEO")

    # =========================================================================
    # SLIDE 9: Phase 2 Breakthrough: 100% On-Device Qwen LLM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9, slide_num=9)
    add_canva_header(s9, "🧠 Phase 2: On-Device Qwen AI Architecture", "LOCAL INFERENCE")

    add_canva_card(s9, 0.6, 1.55, 6.7, 5.4, "Native llama.cpp Runtime", [
        "• Engine: Embedded libllama-server C++ core",
        "• Model: Qwen3 1.7B Q4_K_M GGUF on phone CPU",
        "• 2048 Context: Unlimited, rich explanations",
        "• 100% Offline: Private memory with zero cloud"
    ], step_badge="LLAMA.CPP")

    add_canva_phone_mockup(s9, 7.6, 1.55, 5.1, 5.4, IMG_LONG_ANSWER)

    # =========================================================================
    # SLIDE 10: Phase 2 Breakthrough: 3 AI Modes & Live Thinking Chain
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10, slide_num=10)
    add_canva_header(s10, "🎛️ Phase 2: The 3 Chat Modes & Thinking Process", "AI EXPERIENCE")

    add_canva_card(s10, 0.6, 1.55, 6.7, 5.4, "3 Operating Modes", [
        "• Mode 1 (Qwen): Pure offline neural reasoning",
        "• Mode 2 (Default): Rule-based battery saver",
        "• Mode 3 (Hybrid): Qwen reasoning + tool execution",
        "• Thinking Chain: Collapsible 💭 thoughts box"
    ], step_badge="MODES")

    add_canva_phone_mockup(s10, 7.6, 1.55, 5.1, 5.4, IMG_MODE_DIALOG)

    # =========================================================================
    # SLIDE 11: Phase 2 Breakthrough: Laptop Command Station & Web Portal
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11, slide_num=11)
    add_canva_header(s11, "💻 Phase 2: Laptop Command Portal (Port 8888)", "WEB PORTAL")

    add_canva_card(s11, 0.6, 1.55, 6.7, 5.4, "Off-Grid Web Hub", [
        "• Built-In HTTP: Python server on Port 8888",
        "• In-App Browser: Auto-discovers laptop station",
        "• 1-Click APK: Sideload latest app wirelessly",
        "• Central Mission: Share emergency guides & maps"
    ], step_badge="PORT 8888")

    add_canva_phone_mockup(s11, 7.6, 1.55, 5.1, 5.4, IMG_BROWSER)

    # =========================================================================
    # SLIDE 12: Phase 3 Kickoff: UI/UX Design System & Philosophy
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12, slide_num=12)
    add_canva_header(s12, "🎨 Phase 3: UI/UX Design Philosophy & Systems", "DESIGN SYSTEM")

    add_canva_card(s12, 0.6, 1.55, 5.9, 5.4, "Emergency-First Principles", [
        "• Extreme Contrast: Crisp outdoor sunlight legibility",
        "• Zero Cognitive Load: Calming stress-free layout",
        "• Oversized Targets: Easy tapping during shaking",
        "• Status Transparency: Clear live connection pills"
    ], step_badge="DESIGN")

    add_canva_card(s12, 6.8, 1.55, 5.9, 5.4, "Modern Ergonomics", [
        "• Standard 5-Tab Bar: Mesh, Calls, AI, Maps, SOS",
        "• Glassmorphic Cards: Clean borders & soft shadows",
        "• Fluid Animations: Collapsible thought boxes",
        "• Responsive: Seamless on all screen ratios"
    ], step_badge="CANVA UI")

    # =========================================================================
    # SLIDE 13: Phase 3 Color Palette & Visual Psychology (4 Swatches)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s13, slide_num=13)
    add_canva_header(s13, "🌈 Phase 3: Color Palette & Visual Psychology", "COLOR SYSTEM")

    add_canva_quadrant_card(s13, 0.6, 1.48, 5.9, 2.70, "🌿 Emerald Green (#10B981)", [
        "• Safety & Life: Primary buttons & verified nodes",
        "• Psychological Ease: Reassuring and calm in crisis"
    ])

    add_canva_quadrant_card(s13, 6.8, 1.48, 5.9, 2.70, "🌌 Obsidian Slate (#0F172A)", [
        "• Security & Stability: Headers and core typography",
        "• Tactical Clarity: Maximum outdoor readability"
    ], border_color=COLOR_SLATE_DARK, title_color=COLOR_SLATE_DARK)

    add_canva_quadrant_card(s13, 0.6, 4.34, 5.9, 2.70, "🚨 Signal Red (#EF4444)", [
        "• High-Priority Alert: Reserved strictly for SOS",
        "• Immediate Action: Direct emergency trigger"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_canva_quadrant_card(s13, 6.8, 4.34, 5.9, 2.70, "🌱 Mint Mist (#F0FDF4)", [
        "• Soothing Mint: Reduces eye strain & fatigue",
        "• Modern Aesthetic: Clean & welcoming atmosphere"
    ], border_color=COLOR_FOREST, title_color=COLOR_FOREST)

    # =========================================================================
    # SLIDE 14: Phase 3 Typography Scale & Component Architecture
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14, slide_num=14)
    add_canva_header(s14, "📐 Phase 3: Component Hierarchy & Typography", "COMPONENTS")

    add_canva_card(s14, 0.6, 1.55, 5.9, 5.4, "Typography Standards", [
        "• Display Scale: 32pt - 38pt for major titles",
        "• Body Minimum: Strict 25pt+ for high visibility",
        "• Font Choice: Segoe UI / Clean Modern Sans",
        "• High Contrast: Obsidian on White / Mint Mist"
    ], step_badge="FONTS")

    add_canva_card(s14, 6.8, 1.55, 5.9, 5.4, "Reusable UI Components", [
        "• Mode Selector Pill: One-touch dropdown menu",
        "• Thinking Card: Expandable 💭 collapsible box",
        "• Quick-Action Chips: Instant prompt shortcuts",
        "• Floating SOS Button: 1-press instant beacon"
    ], step_badge="WIDGETS")

    # =========================================================================
    # SLIDE 15: Phase 3 Real Hardware Benchmarks & Telemetry (Big Metrics)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s15, slide_num=15)
    add_canva_header(s15, "📊 Phase 3: Real Device Performance & Metrics", "PERFORMANCE")

    add_canva_quadrant_card(s15, 0.6, 1.48, 5.9, 2.70, "⚡ 9.8 Tokens / Sec", [
        "• Mobile CPU: 9.8 tokens/second streaming",
        "• Instant response with zero cloud server delay"
    ])

    add_canva_quadrant_card(s15, 6.8, 1.48, 5.9, 2.70, "💾 ~585 MB RAM Usage", [
        "• Lightweight: ~585 MB RAM usage footprint",
        "• Leaves ample headroom for Android multitasking"
    ], border_color=COLOR_BLUE_ACCENT, title_color=COLOR_BLUE_ACCENT)

    add_canva_quadrant_card(s15, 0.6, 4.34, 5.9, 2.70, "⏱️ < 45 ms Call Latency", [
        "• Sub-45ms: Real-time duplex Wi-Fi Direct audio",
        "• Studio clarity with zero audible lag or stutter"
    ])

    add_canva_quadrant_card(s15, 6.8, 4.34, 5.9, 2.70, "🔋 0.00 KB Cellular Data", [
        "• 100% Off-Grid: Zero cellular data consumed",
        "• Unlimited operation with SIM card removed"
    ], border_color=COLOR_FOREST, title_color=COLOR_FOREST)

    # =========================================================================
    # SLIDE 16: Phase 3 Multi-Device Field Testing
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s16, slide_num=16)
    add_canva_header(s16, "📱 Phase 3: Field Tested on Real Android Hardware", "DEVICE TESTING")

    add_canva_card(s16, 0.6, 1.55, 6.7, 5.4, "Dual Device Field Validation", [
        "• Nova 1 5G: Running Qwen 1.7B native server",
        "• OPPO Reno2 F: Running responsive client tier",
        "• Live Voice & Video: Dual-stream verified",
        "• 100% Stability: Zero crashes across 100+ tests"
    ], step_badge="FIELD TEST")

    add_canva_phone_mockup(s16, 7.6, 1.55, 5.1, 5.4, IMG_OPPO)

    # =========================================================================
    # SLIDE 17: Next Milestones & Future Roadmap
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s17, slide_num=17)
    add_canva_header(s17, "🚀 Next Milestones & Future Roadmap", "FUTURE ROADMAP")

    add_canva_card(s17, 0.6, 1.55, 5.9, 5.4, "Extended Hardware Reach", [
        "• BLE Coded PHY: 1.5 km long-range hops",
        "• Drone Relays: Airborne disaster mesh link",
        "• Solar Repeaters: Autonomous hill-top pods",
        "• Multi-Hop Video: Distributed packet routing"
    ], step_badge="HARDWARE")

    add_canva_card(s17, 6.8, 1.55, 5.9, 5.4, "Advanced AI Upgrades", [
        "• Offline Speech-to-Text: Whisper.tflite voice",
        "• Offline GIS Maps: Vector map search engine",
        "• Auto SOS Triage: AI situational injury report",
        "• Sharded Inference: Multi-device shared AI"
    ], step_badge="AI NEXT")

    # =========================================================================
    # SLIDE 18: Canva Closing / Thank You Slide
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s18, slide_num=18)

    # Grand Centered Frosted Glass Card
    s18_s = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.86), Inches(1.26), Inches(9.6), Inches(5.3))
    s18_s.fill.solid()
    s18_s.fill.fore_color.rgb = COLOR_SHADOW
    s18_s.line.fill.background()

    cbox = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.8), Inches(1.2), Inches(9.6), Inches(5.3))
    cbox.fill.solid()
    cbox.fill.fore_color.rgb = COLOR_CARD_WHITE
    cbox.line.color.rgb = COLOR_BORDER_EMERALD
    cbox.line.width = Pt(3.0)

    ctf = cbox.text_frame
    ctf.word_wrap = True
    ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ctf.margin_left = Inches(0.6)
    ctf.margin_right = Inches(0.6)

    cp1 = ctf.paragraphs[0]
    cp1.text = "THANK YOU"
    cp1.font.size = Pt(44)
    cp1.font.bold = True
    cp1.font.color.rgb = COLOR_SLATE_DARK
    cp1.alignment = PP_ALIGN.CENTER
    cp1.space_after = Pt(10)

    cp2 = ctf.add_paragraph()
    cp2.text = "Join the Offline Communication Revolution."
    cp2.font.size = Pt(28)
    cp2.font.bold = True
    cp2.font.color.rgb = COLOR_EMERALD_DARK
    cp2.alignment = PP_ALIGN.CENTER
    cp2.space_after = Pt(16)

    cp3 = ctf.add_paragraph()
    cp3.text = "• Phase 2: Accomplished on-device Qwen AI & P2P duplex voice/video calls."
    cp3.font.size = Pt(25)
    cp3.font.color.rgb = COLOR_SLATE_MUTED
    cp3.alignment = PP_ALIGN.CENTER
    cp3.space_after = Pt(8)

    cp4 = ctf.add_paragraph()
    cp4.text = "• Phase 3: Production-grade Canva UI/UX with verified multi-device stability."
    cp4.font.size = Pt(25)
    cp4.font.color.rgb = COLOR_SLATE_MUTED
    cp4.alignment = PP_ALIGN.CENTER
    cp4.space_after = Pt(14)

    cp5 = ctf.add_paragraph()
    cp5.text = "🌐 www.nexusapp.offline  •  100% Free  •  0.00 KB Cellular Data"
    cp5.font.size = Pt(25)
    cp5.font.bold = True
    cp5.font.color.rgb = COLOR_FOREST
    cp5.alignment = PP_ALIGN.CENTER

    # Save to both project directories
    paths_to_save = [
        r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Canva_Master_Presentation.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Canva_Master_Presentation.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_Phase3_Master_Presentation_Polished.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Master_Presentation_Polished.pptx"
    ]
    for p in paths_to_save:
        try:
            prs.save(p)
            print(f"SUCCESS: Saved Canva presentation to: {p}")
        except PermissionError:
            print(f"LOCKED (File open): {p}")
        except Exception as e:
            print(f"Error saving to {p}: {e}")

if __name__ == "__main__":
    build_canva_nexus_deck()
