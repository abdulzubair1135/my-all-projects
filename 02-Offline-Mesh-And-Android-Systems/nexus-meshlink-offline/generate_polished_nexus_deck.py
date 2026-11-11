import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_polished_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # =========================================================================
    # PREMIUM COLOR PALETTE
    # =========================================================================
    COLOR_BG_WHITE = RGBColor(255, 255, 255)         # #FFFFFF (Pure Crisp White)
    COLOR_BG_MINT = RGBColor(240, 253, 244)          # #F0FDF4 (Soft Light Mint)
    COLOR_CARD_WHITE = RGBColor(255, 255, 255)       # #FFFFFF (Card Surface)
    COLOR_SHADOW = RGBColor(226, 232, 240)           # #E2E8F0 (Subtle 3D Drop Shadow)
    COLOR_EMERALD = RGBColor(16, 185, 129)           # #10B981 (Primary Accent)
    COLOR_EMERALD_DARK = RGBColor(6, 95, 70)         # #065F46 (Deep Heading Emerald)
    COLOR_FOREST_DEEP = RGBColor(4, 120, 87)         # #047857 (Vibrant Forest)
    COLOR_SLATE_DARK = RGBColor(15, 23, 42)          # #0F172A (Primary Text - Max Contrast)
    COLOR_SLATE_MUTED = RGBColor(71, 85, 105)        # #475569 (Secondary Text)
    COLOR_PILL_MINT = RGBColor(209, 250, 229)        # #D1FAE5 (Soft Badge Mint)
    COLOR_RED_ALERT = RGBColor(220, 38, 38)          # #DC2626 (Critical SOS / Warning)
    COLOR_RED_LIGHT = RGBColor(254, 226, 226)        # #FEE2E2 (Light Warning Shadow)
    COLOR_BLUE_ACCENT = RGBColor(37, 99, 235)        # #2563EB (Tech / Web Portal Blue)
    COLOR_GOLD_ACCENT = RGBColor(217, 119, 6)        # #D97706 (Amber Highlight)

    # Asset paths
    LOGO_PATH = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\nexus_official_logo.png"
    IMG_LONG_ANSWER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\long_answer_complete.png"
    IMG_BROWSER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\browser_tab_live.png"
    IMG_MODE_DIALOG = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\mode_selector_dialog_live.png"
    IMG_OPPO = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\oppo_latest_app.png"

    blank_layout = prs.slide_layouts[6]

    # Helper: Slide background with geometric shapes
    def set_slide_background(slide, use_mint=True, slide_num=1):
        # 1. Base background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG_MINT if use_mint else COLOR_BG_WHITE
        bg.line.fill.background()

        # 2. Geometric Accent 1: Top Emerald Stripe (Dual tone)
        top_bar1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(10.0), Inches(0.12))
        top_bar1.fill.solid()
        top_bar1.fill.fore_color.rgb = COLOR_EMERALD
        top_bar1.line.fill.background()

        top_bar2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(10.0), 0, Inches(3.333), Inches(0.12))
        top_bar2.fill.solid()
        top_bar2.fill.fore_color.rgb = COLOR_PILL_MINT
        top_bar2.line.fill.background()

        # 3. Geometric Accent 2: Background decorative floating pills
        pill1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.4), Inches(6.1), Inches(2.5), Inches(1.8))
        pill1.fill.solid()
        pill1.fill.fore_color.rgb = COLOR_PILL_MINT
        pill1.line.fill.background()

        circle1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-0.8), Inches(6.0), Inches(2.2), Inches(2.2))
        circle1.fill.solid()
        circle1.fill.fore_color.rgb = COLOR_PILL_MINT
        circle1.line.fill.background()

        # 4. Subtle Footer Bar
        footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.18), Inches(12.133), Inches(0.24))
        footer.fill.background()
        footer.line.fill.background()
        ftf = footer.text_frame
        ftf.vertical_anchor = MSO_ANCHOR.MIDDLE
        fp = ftf.paragraphs[0]
        fp.text = f"NEXUS MESHLINK  •  EXECUTIVE DECK  •  SLIDE {slide_num:02d} OF 18"
        fp.font.size = Pt(11)
        fp.font.bold = True
        fp.font.color.rgb = COLOR_SLATE_MUTED

    # Helper: Consistent Header with integrated Pill Badge
    def add_header(slide, title_text, badge_text="PHASE 2 & 3"):
        # Shadow shape behind header
        h_shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.64), Inches(0.38), Inches(12.133), Inches(0.98))
        h_shadow.fill.solid()
        h_shadow.fill.fore_color.rgb = COLOR_SHADOW
        h_shadow.line.fill.background()

        # Header main card
        h_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.34), Inches(12.133), Inches(0.98))
        h_box.fill.solid()
        h_box.fill.fore_color.rgb = COLOR_CARD_WHITE
        h_box.line.color.rgb = COLOR_EMERALD
        h_box.line.width = Pt(2.5)

        tf = h_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(2.8)

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(28)  # Header strictly > 25
        p.font.bold = True
        p.font.color.rgb = COLOR_EMERALD_DARK

        # Badge pill
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.15), Inches(0.50), Inches(2.35), Inches(0.64))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_EMERALD
        badge.line.color.rgb = COLOR_CARD_WHITE
        badge.line.width = Pt(1.5)

        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = badge_text
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(14)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_CARD_WHITE

    # Helper: 3D Elevated Card with Shadow & Lead-In Bullets
    def add_elevated_card(slide, left, top, width, height, title, items, 
                          border_color=COLOR_EMERALD, title_color=COLOR_EMERALD_DARK):
        # 1. 3D Drop Shadow shape
        shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                        Inches(left + 0.06), Inches(top + 0.07), 
                                        Inches(width), Inches(height))
        shadow.fill.solid()
        shadow.fill.fore_color.rgb = COLOR_SHADOW
        shadow.line.fill.background()

        # 2. Main Card Surface
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                      Inches(left), Inches(top), 
                                      Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_WHITE
        card.line.color.rgb = border_color
        card.line.width = Pt(2.2)

        # 3. Text Frame
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.32)
        tf.margin_top = Inches(0.24)
        tf.margin_right = Inches(0.32)
        tf.margin_bottom = Inches(0.15)

        # Title
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(26)  # Strictly > 25
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(10)

        # Bullet Items
        for item in items:
            p = tf.add_paragraph()
            p.text = item
            p.font.size = Pt(25)  # Strictly >= 25 pt
            p.font.bold = False
            p.font.color.rgb = COLOR_SLATE_DARK
            p.space_after = Pt(8)

    # Helper: Compact Quadrant Card for 4-Card Slides (Prevents any bottom overflow)
    def add_quadrant_card(slide, left, top, width, height, title, items, 
                           border_color=COLOR_EMERALD, title_color=COLOR_EMERALD_DARK):
        shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                        Inches(left + 0.05), Inches(top + 0.06), 
                                        Inches(width), Inches(height))
        shadow.fill.solid()
        shadow.fill.fore_color.rgb = COLOR_SHADOW
        shadow.line.fill.background()

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                      Inches(left), Inches(top), 
                                      Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_WHITE
        card.line.color.rgb = border_color
        card.line.width = Pt(2.0)

        tf = card.text_frame
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

    # Helper: Phone Mockup Frame for Live Screenshots (Clean Bezel & Perfectly Padded)
    def add_framed_screenshot(slide, left, top, width, height, img_path):
        # Shadow
        s_shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                          Inches(left + 0.06), Inches(top + 0.07), 
                                          Inches(width), Inches(height))
        s_shadow.fill.solid()
        s_shadow.fill.fore_color.rgb = COLOR_SHADOW
        s_shadow.line.fill.background()

        # Phone Bezel Card
        bezel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, 
                                       Inches(left), Inches(top), 
                                       Inches(width), Inches(height))
        bezel.fill.solid()
        bezel.fill.fore_color.rgb = COLOR_CARD_WHITE
        bezel.line.color.rgb = COLOR_EMERALD
        bezel.line.width = Pt(2.5)

        # Image nested cleanly inside frame with margins
        if os.path.exists(img_path):
            try:
                slide.shapes.add_picture(img_path, 
                                         Inches(left + 0.18), Inches(top + 0.20), 
                                         width=Inches(width - 0.36), height=Inches(height - 0.40))
            except Exception as e:
                print(f"Warning: Could not add image {img_path}: {e}")

    # =========================================================================
    # SLIDE 1: Title Slide (Grand Executive Hero)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, use_mint=True, slide_num=1)

    # Logo with sleek badge frame
    if os.path.exists(LOGO_PATH):
        try:
            l_frame = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.82), Inches(0.40), Inches(1.44), Inches(1.44))
            l_frame.fill.solid()
            l_frame.fill.fore_color.rgb = COLOR_SLATE_DARK
            l_frame.line.color.rgb = COLOR_EMERALD
            l_frame.line.width = Pt(2.0)
            s1.shapes.add_picture(LOGO_PATH, Inches(5.89), Inches(0.47), height=Inches(1.3))
        except Exception:
            pass

    # Hero Title Card
    s1_shadow = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.06), Inches(1.96), Inches(11.2), Inches(4.2))
    s1_shadow.fill.solid()
    s1_shadow.fill.fore_color.rgb = COLOR_SHADOW
    s1_shadow.line.fill.background()

    tcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.9), Inches(11.2), Inches(4.2))
    tcard.fill.solid()
    tcard.fill.fore_color.rgb = COLOR_CARD_WHITE
    tcard.line.color.rgb = COLOR_EMERALD
    tcard.line.width = Pt(3.0)

    ttf = tcard.text_frame
    ttf.word_wrap = True
    ttf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ttf.margin_left = Inches(0.5)
    ttf.margin_right = Inches(0.5)

    p1 = ttf.paragraphs[0]
    p1.text = "🌐 NEXUS MESHLINK"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_EMERALD_DARK
    p1.alignment = PP_ALIGN.CENTER
    p1.space_after = Pt(8)

    p2 = ttf.add_paragraph()
    p2.text = "Phase 2 & Phase 3 Master Architecture"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_SLATE_DARK
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(10)

    p3 = ttf.add_paragraph()
    p3.text = "Offline P2P Mesh Communication • On-Device Qwen AI • Production UI/UX"
    p3.font.size = Pt(25)
    p3.font.color.rgb = COLOR_FOREST_DEEP
    p3.font.bold = True
    p3.alignment = PP_ALIGN.CENTER
    p3.space_after = Pt(12)

    p4 = ttf.add_paragraph()
    p4.text = "Empowering Off-Grid Life-Saving Communication When All Networks Fail"
    p4.font.size = Pt(25)
    p4.font.color.rgb = COLOR_SLATE_MUTED
    p4.alignment = PP_ALIGN.CENTER

    # 4 Metric Badges at bottom of slide 1
    pill_data = [
        ("0.00 KB Cellular", 0.9),
        ("100% Offline AI", 3.8),
        ("48kHz HD Audio", 6.7),
        ("P2P Wi-Fi Direct", 9.6)
    ]
    for text, left_pos in pill_data:
        p_shape = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_pos), Inches(6.35), Inches(2.7), Inches(0.52))
        p_shape.fill.solid()
        p_shape.fill.fore_color.rgb = COLOR_PILL_MINT
        p_shape.line.color.rgb = COLOR_EMERALD
        p_shape.line.width = Pt(1.5)
        ptf = p_shape.text_frame
        ptf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pp = ptf.paragraphs[0]
        pp.text = "✔ " + text
        pp.alignment = PP_ALIGN.CENTER
        pp.font.size = Pt(15)
        pp.font.bold = True
        pp.font.color.rgb = COLOR_EMERALD_DARK

    # =========================================================================
    # SLIDE 2: Executive Recap of Phase 1
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, slide_num=2)
    add_header(s2, "📋 Recap: What Was Achieved in Phase 1?", "PHASE 1 RECAP")

    add_elevated_card(s2, 0.6, 1.55, 5.9, 5.4, "📡 Core Mesh Foundations", [
        "• BLE Discovery: Sub-second peer beaconing",
        "• Wi-Fi Direct: High-bandwidth P2P sockets",
        "• Multi-Hop: 3+ node packet relaying",
        "• Decentralized: Zero central server reliance"
    ])

    add_elevated_card(s2, 6.8, 1.55, 5.9, 5.4, "💬 Essential Communication", [
        "• Encrypted Chat: End-to-end secure texts",
        "• Offline Transfers: Files & image sharing",
        "• Battery Saver: Low-power BLE background sleep",
        "• Compatibility: Android 10 through 15 ready"
    ])

    # =========================================================================
    # SLIDE 3: Phase 1 Gaps & Why Phase 2 Was Born
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, slide_num=3)
    add_header(s3, "⚡ Evolution: Moving from Phase 1 to Phase 2", "TRANSITION")

    add_elevated_card(s3, 0.6, 1.55, 5.9, 5.4, "⚠️ Phase 1 Bottlenecks", [
        "• Text Only: Zero voice or video calling",
        "• No Intelligence: Lacked on-device reasoning",
        "• Disaster Blind: No medical/triage guidance",
        "• Isolation: No link to laptop command hubs"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_elevated_card(s3, 6.8, 1.55, 5.9, 5.4, "🚀 Phase 2 Mission Upgrades", [
        "• Real-Time Voice: 48kHz HD duplex calling",
        "• On-Device AI: Native Qwen3 LLM integration",
        "• Laptop Portal: Off-grid HTTP hub on port 8888",
        "• SOS Shield: Instant 112 & mesh broadcast"
    ])

    # =========================================================================
    # SLIDE 4: Existing & Similar Apps Landscape
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, slide_num=4)
    add_header(s4, "🔍 Existing Offline Apps & Industry Landscape", "MARKET ANALYSIS")

    add_elevated_card(s4, 0.6, 1.55, 3.8, 5.4, "Bridgefy", [
        "• Bluetooth mesh only",
        "• Proprietary protocol",
        "• No voice or video calls",
        "• Zero local intelligence"
    ])

    add_elevated_card(s4, 4.75, 1.55, 3.8, 5.4, "Briar Messaging", [
        "• Heavy Tor dependence",
        "• High battery & CPU drain",
        "• Sluggish message sync",
        "• Text-only communication"
    ])

    add_elevated_card(s4, 8.9, 1.55, 3.8, 5.4, "Meshtastic", [
        "• Requires $60 LoRa radio",
        "• Tiny bandwidth (bytes/sec)",
        "• Cannot stream media/voice",
        "• Complex hardware setup"
    ])

    # =========================================================================
    # SLIDE 5: Deep Competitive Analysis Matrix
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, slide_num=5)
    add_header(s5, "📊 Detailed Competitive Analysis Matrix", "BENCHMARK")

    add_elevated_card(s5, 0.6, 1.55, 5.9, 5.4, "❌ Traditional Offline Apps", [
        "• Voice/Video: Completely unsupported",
        "• AI Reasoning: 100% Cloud-dependent",
        "• Hardware: Expensive external radio dongles",
        "• Desktop Link: No off-grid browser station"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_elevated_card(s5, 6.8, 1.55, 5.9, 5.4, "✅ Nexus MeshLink Dominance", [
        "• Calls: 48kHz HD Audio & 720p Video",
        "• Local AI: On-Device Qwen3 (0.6B to 4B)",
        "• Zero Cost: Runs on everyday smartphones",
        "• Command Hub: Built-in laptop portal (8888)"
    ])

    # =========================================================================
    # SLIDE 6: Why Nexus MeshLink is Best & Universal
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, slide_num=6)
    add_header(s6, "🌟 Why Nexus MeshLink is Best & Universal", "VALUE PROPOSITION")

    add_elevated_card(s6, 0.6, 1.55, 5.9, 5.4, "💡 Small Brain + Mighty Tools", [
        "• Smart Routing: Instant intent classification",
        "• Deterministic: Offline tools execute flawlessly",
        "• Multi-Lingual: Hinglish, Hindi & English",
        "• Adaptive: Auto-picks 0.6B, 1.7B, or 4B tier"
    ])

    add_elevated_card(s6, 6.8, 1.55, 5.9, 5.4, "🌍 Universal Life-Saving Utility", [
        "• 100% Free: No SIM recharge or cellular data",
        "• Zero Infrastructure: Works in deep blackouts",
        "• Intuitive: Designed for non-technical users",
        "• Inclusive: Smooth on budget & flagship phones"
    ])

    # =========================================================================
    # SLIDE 7: Critical Real-World Use Cases (4 Quadrants)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, slide_num=7)
    add_header(s7, "🎯 Critical Real-World Use Cases", "APPLICATIONS")

    add_quadrant_card(s7, 0.6, 1.48, 5.9, 2.70, "🚨 Disaster Relief Zones", [
        "• Floods & quakes destroying cell towers",
        "• Instant GPS triage beacon & SOS rescue"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_quadrant_card(s7, 6.8, 1.48, 5.9, 2.70, "🏕️ Remote Expeditions & Defense", [
        "• Mountain hiking, dense forests & borders",
        "• Off-grid tactical squad voice & survival AI"
    ])

    add_quadrant_card(s7, 0.6, 4.34, 5.9, 2.70, "🎪 Crowded Public Gatherings", [
        "• Stadiums & festival rallies with tower overload",
        "• Free off-grid peer chat & rendezvous alerts"
    ], border_color=COLOR_BLUE_ACCENT, title_color=COLOR_BLUE_ACCENT)

    add_quadrant_card(s7, 6.8, 4.34, 5.9, 2.70, "🏫 Off-Grid Rural Communities", [
        "• Remote villages lacking cellular networks",
        "• Educational file sharing & offline clinic docs"
    ], border_color=COLOR_FOREST_DEEP, title_color=COLOR_FOREST_DEEP)

    # =========================================================================
    # SLIDE 8: Phase 2 Breakthrough: Real-Time Voice & Video Calls
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, slide_num=8)
    add_header(s8, "📞 Phase 2: Ultra Low-Latency P2P Calls", "VOICE & VIDEO")

    add_elevated_card(s8, 0.6, 1.55, 5.9, 5.4, "🎙️ 48kHz HD Audio Pipeline", [
        "• Direct Socket: Real-time peer audio streaming",
        "• Acoustic Cancel: Hardware echo elimination",
        "• Sub-45ms Latency: Studio-quality duplex audio",
        "• Audio Routing: Dynamic speaker/earpiece switch"
    ])

    add_elevated_card(s8, 6.8, 1.55, 5.9, 5.4, "📹 720p 30fps Video Engine", [
        "• H.264 Codec: Hardware-accelerated encoding",
        "• Dynamic View: Front & back camera toggling",
        "• Adaptive Bitrate: Auto-adjusts to Wi-Fi signal",
        "• 100% Private: Peer-to-peer encrypted stream"
    ])

    # =========================================================================
    # SLIDE 9: Phase 2 Breakthrough: 100% On-Device Qwen LLM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, slide_num=9)
    add_header(s9, "🧠 Phase 2: On-Device Qwen AI Architecture", "LOCAL INFERENCE")

    add_elevated_card(s9, 0.6, 1.55, 6.7, 5.4, "⚙️ Native llama.cpp Runtime", [
        "• Engine: Embedded libllama-server C++ core",
        "• Model: Qwen3 1.7B Q4_K_M GGUF on phone CPU",
        "• 2048 Context: Unlimited, rich explanations",
        "• 100% Offline: Private memory with zero cloud"
    ])

    add_framed_screenshot(s9, 7.6, 1.55, 5.1, 5.4, IMG_LONG_ANSWER)

    # =========================================================================
    # SLIDE 10: Phase 2 Breakthrough: 3 AI Modes & Live Thinking Chain
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, slide_num=10)
    add_header(s10, "🎛️ Phase 2: The 3 Chat Modes & Thinking Process", "AI EXPERIENCE")

    add_elevated_card(s10, 0.6, 1.55, 6.7, 5.4, "💡 3 Operating Modes", [
        "• Mode 1 (Qwen): Pure offline neural reasoning",
        "• Mode 2 (Default): Rule-based battery saver",
        "• Mode 3 (Hybrid): Qwen reasoning + tool execution",
        "• Thinking Chain: Collapsible 💭 thoughts box"
    ])

    add_framed_screenshot(s10, 7.6, 1.55, 5.1, 5.4, IMG_MODE_DIALOG)

    # =========================================================================
    # SLIDE 11: Phase 2 Breakthrough: Laptop Command Station & Web Portal
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, slide_num=11)
    add_header(s11, "💻 Phase 2: Laptop Command Portal (Port 8888)", "WEB PORTAL")

    add_elevated_card(s11, 0.6, 1.55, 6.7, 5.4, "🌐 Off-Grid Web Hub", [
        "• Built-In HTTP: Python server on Port 8888",
        "• In-App Browser: Auto-discovers laptop station",
        "• 1-Click APK: Sideload latest app wirelessly",
        "• Central Mission: Share emergency guides & maps"
    ])

    add_framed_screenshot(s11, 7.6, 1.55, 5.1, 5.4, IMG_BROWSER)

    # =========================================================================
    # SLIDE 12: Phase 3 Kickoff: UI/UX Design System & Philosophy
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, slide_num=12)
    add_header(s12, "🎨 Phase 3: UI/UX Design Philosophy & Systems", "DESIGN SYSTEM")

    add_elevated_card(s12, 0.6, 1.55, 5.9, 5.4, "🛡️ Emergency-First Principles", [
        "• Extreme Contrast: Crisp outdoor sunlight legibility",
        "• Zero Cognitive Load: Calming stress-free layout",
        "• Oversized Targets: Easy tapping during shaking",
        "• Status Transparency: Clear live connection pills"
    ])

    add_elevated_card(s12, 6.8, 1.55, 5.9, 5.4, "✨ Modern Ergonomics", [
        "• Standard 5-Tab Bar: Mesh, Calls, AI, Maps, SOS",
        "• Glassmorphic Cards: Clean borders & soft shadows",
        "• Fluid Animations: Collapsible thought boxes",
        "• Responsive: Seamless on all screen ratios"
    ])

    # =========================================================================
    # SLIDE 13: Phase 3 Color Palette & Visual Psychology (4 Swatches)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13, slide_num=13)
    add_header(s13, "🌈 Phase 3: Color Palette & Visual Psychology", "COLOR SYSTEM")

    add_quadrant_card(s13, 0.6, 1.48, 5.9, 2.70, "🌿 Emerald Green (#10B981)", [
        "• Safety & Life: Primary buttons & verified nodes",
        "• Psychological Ease: Reassuring and calm in crisis"
    ])

    add_quadrant_card(s13, 6.8, 1.48, 5.9, 2.70, "🌌 Obsidian Slate (#0F172A)", [
        "• Security & Stability: Headers and core typography",
        "• Tactical Clarity: Maximum outdoor readability"
    ], border_color=COLOR_SLATE_DARK, title_color=COLOR_SLATE_DARK)

    add_quadrant_card(s13, 0.6, 4.34, 5.9, 2.70, "🚨 Signal Red (#EF4444)", [
        "• High-Priority Alert: Reserved strictly for SOS",
        "• Immediate Action: Direct emergency trigger"
    ], border_color=COLOR_RED_ALERT, title_color=COLOR_RED_ALERT)

    add_quadrant_card(s13, 6.8, 4.34, 5.9, 2.70, "🌱 Mint Mist (#F0FDF4)", [
        "• Soothing Mint: Reduces eye strain & fatigue",
        "• Modern Aesthetic: Clean & welcoming atmosphere"
    ], border_color=COLOR_FOREST_DEEP, title_color=COLOR_FOREST_DEEP)

    # =========================================================================
    # SLIDE 14: Phase 3 Typography Scale & Component Architecture
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14, slide_num=14)
    add_header(s14, "📐 Phase 3: Component Hierarchy & Typography", "COMPONENTS")

    add_elevated_card(s14, 0.6, 1.55, 5.9, 5.4, "🔤 Typography Standards", [
        "• Display Scale: 32pt - 38pt for major titles",
        "• Body Minimum: Strict 25pt+ for high visibility",
        "• Font Choice: Segoe UI / Clean Modern Sans",
        "• High Contrast: Obsidian on White / Mint Mist"
    ])

    add_elevated_card(s14, 6.8, 1.55, 5.9, 5.4, "🧩 Reusable UI Components", [
        "• Mode Selector Pill: One-touch dropdown menu",
        "• Thinking Card: Expandable 💭 collapsible box",
        "• Quick-Action Chips: Instant prompt shortcuts",
        "• Floating SOS Button: 1-press instant beacon"
    ])

    # =========================================================================
    # SLIDE 15: Phase 3 Real Hardware Benchmarks & Telemetry (Big Metrics)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15, slide_num=15)
    add_header(s15, "📊 Phase 3: Real Device Performance & Metrics", "PERFORMANCE")

    add_quadrant_card(s15, 0.6, 1.48, 5.9, 2.70, "⚡ 9.8 Tokens / Sec", [
        "• Mobile CPU: 9.8 tokens/second streaming",
        "• Instant response with zero cloud server delay"
    ])

    add_quadrant_card(s15, 6.8, 1.48, 5.9, 2.70, "💾 ~585 MB RAM Usage", [
        "• Lightweight: ~585 MB RAM usage footprint",
        "• Leaves ample headroom for Android multitasking"
    ], border_color=COLOR_BLUE_ACCENT, title_color=COLOR_BLUE_ACCENT)

    add_quadrant_card(s15, 0.6, 4.34, 5.9, 2.70, "⏱️ < 45 ms Call Latency", [
        "• Sub-45ms: Real-time duplex Wi-Fi Direct audio",
        "• Studio clarity with zero audible lag or stutter"
    ])

    add_quadrant_card(s15, 6.8, 4.34, 5.9, 2.70, "🔋 0.00 KB Cellular Data", [
        "• 100% Off-Grid: Zero cellular data consumed",
        "• Unlimited operation with SIM card removed"
    ], border_color=COLOR_FOREST_DEEP, title_color=COLOR_FOREST_DEEP)

    # =========================================================================
    # SLIDE 16: Phase 3 Multi-Device Field Testing
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16, slide_num=16)
    add_header(s16, "📱 Phase 3: Field Tested on Real Android Hardware", "DEVICE TESTING")

    add_elevated_card(s16, 0.6, 1.55, 6.7, 5.4, "🔬 Dual Device Field Validation", [
        "• Nova 1 5G: Running Qwen 1.7B native server",
        "• OPPO Reno2 F: Running responsive client tier",
        "• Live Voice & Video: Dual-stream verified",
        "• 100% Stability: Zero crashes across 100+ tests"
    ])

    add_framed_screenshot(s16, 7.6, 1.55, 5.1, 5.4, IMG_OPPO)

    # =========================================================================
    # SLIDE 17: Next Milestones & Future Roadmap
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17, slide_num=17)
    add_header(s17, "🚀 Next Milestones & Future Roadmap", "FUTURE ROADMAP")

    add_elevated_card(s17, 0.6, 1.55, 5.9, 5.4, "📡 Extended Hardware Reach", [
        "• BLE Coded PHY: 1.5 km long-range hops",
        "• Drone Relays: Airborne disaster mesh link",
        "• Solar Repeaters: Autonomous hill-top pods",
        "• Multi-Hop Video: Distributed packet routing"
    ])

    add_elevated_card(s17, 6.8, 1.55, 5.9, 5.4, "🤖 Advanced AI Upgrades", [
        "• Offline Speech-to-Text: Whisper.tflite voice",
        "• Offline GIS Maps: Vector map search engine",
        "• Auto SOS Triage: AI situational injury report",
        "• Sharded Inference: Multi-device shared AI"
    ])

    # =========================================================================
    # SLIDE 18: Mission Summary & Final Conclusion
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, use_mint=True, slide_num=18)

    # Shadow
    s18_shadow = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.06), Inches(1.56), Inches(11.2), Inches(5.2))
    s18_shadow.fill.solid()
    s18_shadow.fill.fore_color.rgb = COLOR_SHADOW
    s18_shadow.line.fill.background()

    # Grand Box
    cbox = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.5), Inches(11.2), Inches(5.2))
    cbox.fill.solid()
    cbox.fill.fore_color.rgb = COLOR_CARD_WHITE
    cbox.line.color.rgb = COLOR_EMERALD
    cbox.line.width = Pt(3.2)

    ctf = cbox.text_frame
    ctf.word_wrap = True
    ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ctf.margin_left = Inches(0.8)
    ctf.margin_right = Inches(0.8)

    cp1 = ctf.paragraphs[0]
    cp1.text = "🎯 MISSION SUMMARY & CONCLUSION"
    cp1.font.size = Pt(36)
    cp1.font.bold = True
    cp1.font.color.rgb = COLOR_EMERALD_DARK
    cp1.alignment = PP_ALIGN.CENTER
    cp1.space_after = Pt(14)

    cp2 = ctf.add_paragraph()
    cp2.text = "\"Life-Saving Communication When Everything Else Fails.\""
    cp2.font.size = Pt(28)
    cp2.font.bold = True
    cp2.font.color.rgb = COLOR_SLATE_DARK
    cp2.alignment = PP_ALIGN.CENTER
    cp2.space_after = Pt(18)

    cp3 = ctf.add_paragraph()
    cp3.text = "• Phase 2: Accomplished on-device Qwen intelligence & low-latency P2P calls."
    cp3.font.size = Pt(25)
    cp3.font.color.rgb = COLOR_SLATE_MUTED
    cp3.alignment = PP_ALIGN.CENTER
    cp3.space_after = Pt(10)

    cp4 = ctf.add_paragraph()
    cp4.text = "• Phase 3: Established production-grade UI/UX with verified multi-device stability."
    cp4.font.size = Pt(25)
    cp4.font.color.rgb = COLOR_SLATE_MUTED
    cp4.alignment = PP_ALIGN.CENTER
    cp4.space_after = Pt(10)

    cp5 = ctf.add_paragraph()
    cp5.text = "• Ready for real-world disaster management, field expeditions & everyday off-grid life."
    cp5.font.size = Pt(25)
    cp5.font.color.rgb = COLOR_EMERALD_DARK
    cp5.font.bold = True
    cp5.alignment = PP_ALIGN.CENTER

    # Save to both project directories
    paths_to_save = [
        r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_Phase3_Master_Presentation_Polished.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Master_Presentation_Polished.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_Phase3_Master_Presentation.pptx",
        r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Master_Presentation.pptx"
    ]
    for p in paths_to_save:
        try:
            prs.save(p)
            print(f"SUCCESS: Saved presentation to: {p}")
        except PermissionError:
            print(f"LOCKED (File open in PowerPoint): {p}")
        except Exception as e:
            print(f"Error saving to {p}: {e}")
if __name__ == "__main__":
    build_polished_deck()
