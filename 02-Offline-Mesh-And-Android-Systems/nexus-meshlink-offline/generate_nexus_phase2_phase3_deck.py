import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_nexus_master_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Palette: White & Light Green theme (as requested)
    COLOR_BG_WHITE = RGBColor(255, 255, 255)         # #FFFFFF (Pure White)
    COLOR_BG_LIGHT_GREEN = RGBColor(240, 253, 244)   # #F0FDF4 (Light Mint Green)
    COLOR_BG_CARD = RGBColor(255, 255, 255)          # #FFFFFF (Card White)
    COLOR_CARD_BORDER = RGBColor(16, 185, 129)       # #10B981 (Emerald Accent)
    COLOR_CARD_BORDER_SOFT = RGBColor(209, 250, 229) # #D1FAE5 (Soft Border)
    COLOR_EMERALD_DARK = RGBColor(6, 95, 70)         # #065F46 (Deep Forest Green)
    COLOR_TEXT_PRIMARY = RGBColor(15, 23, 42)        # #0F172A (Deep Slate for max contrast)
    COLOR_TEXT_SECONDARY = RGBColor(51, 65, 85)      # #334155 (Sub-bullets)
    COLOR_PILL_BG = RGBColor(220, 252, 231)          # #DCFCE7 (Pill mint background)
    COLOR_DANGER_RED = RGBColor(220, 38, 38)         # #DC2626 (Emergency red)
    COLOR_BLUE_ACCENT = RGBColor(37, 99, 235)        # #2563EB (Tech blue)

    # Real screenshots and assets
    LOGO_PATH = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\nexus_official_logo.png"
    IMG_LONG_ANSWER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\long_answer_complete.png"
    IMG_BROWSER = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\browser_tab_live.png"
    IMG_MODE_DIALOG = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\mode_selector_dialog_live.png"
    IMG_OPPO = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\oppo_latest_app.png"

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide, use_light_green=True):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG_LIGHT_GREEN if use_light_green else COLOR_BG_WHITE
        bg.line.fill.background()

        # Decorative Emerald Top Stripe
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.12))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_CARD_BORDER
        top_bar.line.fill.background()

        # Soft decorative background corner shape
        corner_acc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.8), Inches(6.2), Inches(2.2), Inches(1.8))
        corner_acc.fill.solid()
        corner_acc.fill.fore_color.rgb = COLOR_PILL_BG
        corner_acc.line.fill.background()

    def add_header(slide, title_text, badge_text="PHASE 2 & PHASE 3"):
        # Header banner box
        header_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.35), Inches(12.133), Inches(1.05))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = COLOR_BG_CARD
        header_box.line.color.rgb = COLOR_CARD_BORDER
        header_box.line.width = Pt(2.5)

        tf = header_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(2.8)

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(28) # Font > 25
        p.font.bold = True
        p.font.color.rgb = COLOR_EMERALD_DARK

        # Right badge tag
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.2), Inches(0.55), Inches(2.3), Inches(0.65))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_CARD_BORDER
        badge.line.color.rgb = COLOR_BG_WHITE
        badge.line.width = Pt(1.5)

        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = badge_text
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(14)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_BG_WHITE

    def add_card(slide, left, top, width, height, title, bullet_items, border_color=COLOR_CARD_BORDER, title_color=COLOR_EMERALD_DARK):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_BG_CARD
        card.line.color.rgb = border_color
        card.line.width = Pt(2.0)

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.35)
        tf.margin_top = Inches(0.28)
        tf.margin_right = Inches(0.35)
        tf.margin_bottom = Inches(0.2)

        # Title
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(26) # Font > 25
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(12)

        # Bullets (Font >= 25)
        for item in bullet_items:
            p = tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(25) # Exact >= 25 constraint
            p.font.bold = False
            p.font.color.rgb = COLOR_TEXT_PRIMARY
            p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, use_light_green=True)

    # Logo if available
    if os.path.exists(LOGO_PATH):
        try:
            s1.shapes.add_picture(LOGO_PATH, Inches(5.8), Inches(0.7), height=Inches(1.5))
        except Exception:
            pass

    # Main Title Card
    tcard = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.4), Inches(11.333), Inches(4.5))
    tcard.fill.solid()
    tcard.fill.fore_color.rgb = COLOR_BG_CARD
    tcard.line.color.rgb = COLOR_CARD_BORDER
    tcard.line.width = Pt(3.0)

    ttf = tcard.text_frame
    ttf.word_wrap = True
    ttf.vertical_anchor = MSO_ANCHOR.MIDDLE
    ttf.margin_left = Inches(0.8)
    ttf.margin_right = Inches(0.8)

    p1 = ttf.paragraphs[0]
    p1.text = "🌐 NEXUS MESHLINK"
    p1.font.size = Pt(38)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_EMERALD_DARK
    p1.alignment = PP_ALIGN.CENTER
    p1.space_after = Pt(10)

    p2 = ttf.add_paragraph()
    p2.text = "Phase 2 & Phase 3 Comprehensive Architecture"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_TEXT_PRIMARY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_after = Pt(14)

    p3 = ttf.add_paragraph()
    p3.text = "Offline P2P Mesh Communication • On-Device Qwen AI • Production UI/UX"
    p3.font.size = Pt(25)
    p3.font.color.rgb = COLOR_CARD_BORDER
    p3.font.bold = True
    p3.alignment = PP_ALIGN.CENTER
    p3.space_after = Pt(18)

    p4 = ttf.add_paragraph()
    p4.text = "Empowering Off-Grid Life-Saving Communication When All Networks Fail"
    p4.font.size = Pt(25)
    p4.font.color.rgb = COLOR_TEXT_SECONDARY
    p4.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: Executive Recap of Phase 1
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "📋 Recap: What Was Achieved in Phase 1?", "PHASE 1 RECAP")

    add_card(s2, 0.6, 1.65, 5.9, 5.3, "📡 Core Mesh Foundations", [
        "BLE Discovery: Sub-second peer beaconing",
        "Wi-Fi Direct P2P: High bandwidth sockets",
        "Multi-Hop Routing: 3+ node relaying",
        "Decentralized: Zero central server reliance"
    ])

    add_card(s2, 6.8, 1.65, 5.9, 5.3, "💬 Essential Communication", [
        "Encrypted P2P Chats: End-to-end security",
        "Offline File & Photo Transfers verified",
        "Battery Conservation: Low-power BLE sleep",
        "Android 10 - 18 Universal compatibility"
    ])

    # =========================================================================
    # SLIDE 3: Phase 1 Gaps & Why Phase 2 Was Born
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "⚡ Evolution: Moving from Phase 1 to Phase 2", "TRANSITION")

    add_card(s3, 0.6, 1.65, 5.9, 5.3, "⚠️ Phase 1 Bottlenecks", [
        "Text only: No real-time voice or video calls",
        "No intelligence: Lacked on-device reasoning",
        "No knowledge base during natural disasters",
        "Isolation: No link to laptop command stations"
    ], border_color=COLOR_DANGER_RED, title_color=COLOR_DANGER_RED)

    add_card(s3, 6.8, 1.65, 5.9, 5.3, "🚀 Phase 2 Mission Objectives", [
        "High Quality Voice & Video P2P Calling",
        "Native On-Device Qwen3 LLM (llama.cpp)",
        "Laptop Emergency Portal (Port 8888)",
        "1-Touch Mesh SOS Emergency Beaconing"
    ])

    # =========================================================================
    # SLIDE 4: Existing & Similar Apps Landscape
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "🔍 Existing Offline Apps & Industry Landscape", "MARKET ANALYSIS")

    add_card(s4, 0.6, 1.65, 3.8, 5.3, "Bridgefy", [
        "Bluetooth text mesh",
        "Proprietary protocol",
        "No voice or video calls",
        "Zero AI capabilities"
    ])

    add_card(s4, 4.75, 1.65, 3.8, 5.3, "Briar Messaging", [
        "High privacy focused",
        "Relies heavily on Tor",
        "High battery & CPU drain",
        "Text only, no calling"
    ])

    add_card(s4, 8.9, 1.65, 3.8, 5.3, "Meshtastic", [
        "LoRa radio mesh",
        "Requires $60 hardware",
        "Extremely slow bitrates",
        "Cannot stream media"
    ])

    # =========================================================================
    # SLIDE 5: Deep Competitive Analysis Matrix
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "📊 Detailed Competitive Analysis Matrix", "BENCHMARK")

    add_card(s5, 0.6, 1.65, 5.9, 5.3, "❌ Traditional Offline Apps", [
        "Voice/Video Calls: Unsupported / None",
        "AI Assistance: 100% Dependent on cloud",
        "Hardware: Need external dongles / radios",
        "Setup: Complex pairing & sluggish relays",
        "Disaster Utility: Very limited text alerts"
    ], border_color=COLOR_DANGER_RED, title_color=COLOR_DANGER_RED)

    add_card(s5, 6.8, 1.65, 5.9, 5.3, "✅ Nexus MeshLink Dominance", [
        "Real-Time Calls: 48kHz HD Audio & 720p Video",
        "Local AI: 100% On-Device Qwen3 LLM",
        "Hardware: Standard Android Phones (No extras)",
        "Local Portal: Built-in Laptop Web Station",
        "Emergency Shield: Instant 112 & Mesh SOS"
    ])

    # =========================================================================
    # SLIDE 6: Why Nexus MeshLink is the Best & Useful for All
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "🌟 Why Nexus MeshLink is Best & Universal", "VALUE PROPOSITION")

    add_card(s6, 0.6, 1.65, 5.9, 5.3, "💡 Small Brain + Powerful Tools", [
        "Smart intent detection with AI Router",
        "Executes critical tasks deterministically",
        "Hinglish, Hindi & English comprehension",
        "Adaptive model sizes (0.6B, 1.7B, 4B)"
    ])

    add_card(s6, 6.8, 1.65, 5.9, 5.3, "🌍 Universal Life-Saving Utility", [
        "Zero Internet & Zero Mobile Data Needed",
        "Free forever with no cellular recharge",
        "Accessible to everyday users effortlessly",
        "Works smoothly across diverse phone brands"
    ])

    # =========================================================================
    # SLIDE 7: Real-World Use Cases
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "🎯 Critical Real-World Use Cases", "APPLICATIONS")

    add_card(s7, 0.6, 1.65, 5.9, 2.5, "🚨 Disaster Relief Zones", [
        "Floods & earthquakes destroying towers",
        "Medical triage & emergency coordination"
    ])

    add_card(s7, 6.8, 1.65, 5.9, 2.5, "🏕️ Remote Expeditions & Defense", [
        "Himalayan hiking, forests, border patrols",
        "Tactical off-grid voice & situational AI"
    ])

    add_card(s7, 0.6, 4.45, 5.9, 2.5, "🎪 Crowded Public Events", [
        "Stadiums & festivals with tower overload",
        "Instant peer-to-peer family rendezvous"
    ])

    add_card(s7, 6.8, 4.45, 5.9, 2.5, "🏫 Off-Grid Campuses & Villages", [
        "Rural schooling & community hubs",
        "Local file sharing & survival education"
    ])

    # =========================================================================
    # SLIDE 8: Phase 2 Breakthrough: Real-Time Voice & Video Calls
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "📞 Phase 2: Ultra Low-Latency P2P Calls", "VOICE & VIDEO")

    add_card(s8, 0.6, 1.65, 5.9, 5.3, "🎙️ 48kHz HD Audio Engine", [
        "Direct socket audio streaming",
        "Acoustic echo cancellation enabled",
        "Sub-50ms transmission latency",
        "Loudspeaker & earpiece auto-routing"
    ])

    add_card(s8, 6.8, 1.65, 5.9, 5.3, "📹 720p 30fps Video Pipeline", [
        "Hardware-accelerated H.264 codecs",
        "Dynamic portrait & landscape mirroring",
        "Front & back camera seamless toggling",
        "Zero cell tower or internet requirement"
    ])

    # =========================================================================
    # SLIDE 9: Phase 2 Breakthrough: 100% On-Device Qwen LLM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "🧠 Phase 2: On-Device Qwen AI Architecture", "LOCAL INFERENCE")

    add_card(s9, 0.6, 1.65, 6.8, 5.3, "⚙️ Native llama.cpp Runtime", [
        "Embedded libllama-server native engine",
        "Qwen3 1.7B Q4_K_M GGUF model on mobile CPU",
        "2048 token context for extensive answers",
        "Natural Hinglish & English explanations"
    ])

    if os.path.exists(IMG_LONG_ANSWER):
        try:
            s9.shapes.add_picture(IMG_LONG_ANSWER, Inches(7.7), Inches(1.65), height=Inches(5.3))
        except Exception:
            pass

    # =========================================================================
    # SLIDE 10: Phase 2 Breakthrough: 3 AI Modes & Live Thinking Chain
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "🎛️ Phase 2: The 3 Chat Modes & Thinking Process", "AI EXPERIENCE")

    add_card(s10, 0.6, 1.65, 6.8, 5.3, "💡 3 Operating Modes", [
        "🧠 Qwen: Pure offline neural reasoning",
        "⚡ Default: Rule-based fast battery saver",
        "🤖 Hybrid: Emergency tools + Qwen logic",
        "💭 Collapsible live thinking box"
    ])

    if os.path.exists(IMG_MODE_DIALOG):
        try:
            s10.shapes.add_picture(IMG_MODE_DIALOG, Inches(7.7), Inches(1.65), height=Inches(5.3))
        except Exception:
            pass

    # =========================================================================
    # SLIDE 11: Phase 2 Breakthrough: Laptop Command Station & Web Portal
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "💻 Phase 2: Laptop Command Portal (Port 8888)", "WEB PORTAL")

    add_card(s11, 0.6, 1.65, 6.8, 5.3, "🌐 Off-Grid Web Hub", [
        "Lightweight Python server on Port 8888",
        "In-App browser with auto-connect logic",
        "Direct 1-Click APK install for Android phones",
        "Shared survival manuals & emergency news"
    ])

    if os.path.exists(IMG_BROWSER):
        try:
            s11.shapes.add_picture(IMG_BROWSER, Inches(7.7), Inches(1.65), height=Inches(5.3))
        except Exception:
            pass

    # =========================================================================
    # SLIDE 12: Phase 3 Kickoff: UI/UX Design System & Philosophy
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "🎨 Phase 3: UI/UX Design Philosophy & Systems", "DESIGN SYSTEM")

    add_card(s12, 0.6, 1.65, 5.9, 5.3, "🛡️ Emergency-First Principles", [
        "High contrast: Legible under harsh sunlight",
        "Zero friction: Big touch targets for SOS",
        "Cognitive calmness: Eliminating panic UI",
        "Instant feedback with live status pills"
    ])

    add_card(s12, 6.8, 1.65, 5.9, 5.3, "✨ Production Polish", [
        "Modern clean glassmorphic components",
        "Standardized 5-Tab ergonomic bottom bar",
        "Micro-animations for call & thinking states",
        "Smooth expandable card containers"
    ])

    # =========================================================================
    # SLIDE 13: Phase 3 Color Palette & Visual Psychology
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "🌈 Phase 3: Color Palette & Visual Psychology", "COLOR SYSTEM")

    add_card(s13, 0.6, 1.65, 5.9, 2.5, "🌿 Emerald Green (#10B981)", [
        "Symbolizes life, health, survival, connection",
        "Primary action buttons & verified status"
    ], border_color=COLOR_CARD_BORDER, title_color=COLOR_EMERALD_DARK)

    add_card(s13, 6.8, 1.65, 5.9, 2.5, "🌌 Dark Slate (#0F172A)", [
        "Represents authority, security, precision",
        "Deep contrast headers & text hierarchy"
    ], border_color=COLOR_TEXT_PRIMARY, title_color=COLOR_TEXT_PRIMARY)

    add_card(s13, 0.6, 4.45, 5.9, 2.5, "🚨 Signal Red (#EF4444)", [
        "High-urgency emergency warnings & SOS",
        "Reserved strictly for critical alerts"
    ], border_color=COLOR_DANGER_RED, title_color=COLOR_DANGER_RED)

    add_card(s13, 6.8, 4.45, 5.9, 2.5, "🌱 Soft Mint (#F0FDF4)", [
        "Calming background soothing user stress",
        "Clean, modern, battery-efficient aesthetics"
    ], border_color=COLOR_CARD_BORDER_SOFT, title_color=COLOR_EMERALD_DARK)

    # =========================================================================
    # SLIDE 14: Phase 3 Typography & Component Hierarchy
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "📐 Phase 3: Component Hierarchy & Typography", "COMPONENTS")

    add_card(s14, 0.6, 1.65, 5.9, 5.3, "🔤 Typography Standards", [
        "Display: Sans-serif Black for bold headers",
        "Body: Sans-serif Medium for readability",
        "Strict scale: 32pt Titles, 26pt Cards",
        "High contrast on white & mint surfaces"
    ])

    add_card(s14, 6.8, 1.65, 5.9, 5.3, "🧩 Core Reusable Components", [
        "Floating Mode Selector Pill with arrow",
        "Collapsible Thinking Card with toggle arrow",
        "Horizontal interactive quick-action chips",
        "Emergency Action trigger buttons"
    ])

    # =========================================================================
    # SLIDE 15: Phase 3 Real Hardware Benchmarks & Performance
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "📊 Phase 3: Real Device Performance & Metrics", "PERFORMANCE")

    add_card(s15, 0.6, 1.65, 5.9, 5.3, "⚡ Measured Speed & Power", [
        "AI Generation: 9.8 tokens/second on CPU",
        "RAM Usage: ~585 MB (Lightweight footprint)",
        "Audio Call Latency: < 45 ms end-to-end",
        "Video Frame Rate: Steady 30 fps over P2P"
    ])

    add_card(s15, 6.8, 1.65, 5.9, 5.3, "🔋 Battery & Network Footprint", [
        "Cellular Data Consumed: Exactly 0.00 KB",
        "Server Latency: Instant local HTTP ping",
        "Thermal Profile: Cool CPU with thread gating",
        "Discovery Time: < 800ms for nearby nodes"
    ])

    # =========================================================================
    # SLIDE 16: Phase 3 Multi-Device Production Verification
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "📱 Phase 3: Field Tested on Real Android Hardware", "DEVICE TESTING")

    add_card(s16, 0.6, 1.65, 6.8, 5.3, "🔬 Dual Device Field Test", [
        "AI Nova 1 5G: Running Qwen 1.7B server",
        "OPPO Reno2 F: Auto-detected 0.6B tier",
        "Simultaneous P2P calling verified live",
        "Direct APK install verified via Laptop Hub"
    ])

    if os.path.exists(IMG_OPPO):
        try:
            s16.shapes.add_picture(IMG_OPPO, Inches(7.7), Inches(1.65), height=Inches(5.3))
        except Exception:
            pass

    # =========================================================================
    # SLIDE 17: Next Milestones & Future Roadmap
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "🚀 Next Milestones & Future Roadmap", "FUTURE ROADMAP")

    add_card(s17, 0.6, 1.65, 5.9, 5.3, "📡 Extended Hardware Reach", [
        "BLE Coded PHY: 1.5 km long-range hops",
        "Drone Relay Nodes: Aerial disaster mesh",
        "Solar-powered stationary repeater pods",
        "Multi-hop video packet routing"
    ])

    add_card(s17, 6.8, 1.65, 5.9, 5.3, "🤖 Advanced AI Upgrades", [
        "Offline Speech-to-Text: Whisper.tflite",
        "Mesh Map Vector Search for offline GIS",
        "Automated SOS situational report generator",
        "Cross-device decentralized model sharding"
    ])

    # =========================================================================
    # SLIDE 18: Conclusion & Mission Summary
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18, use_light_green=True)

    cbox = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.5), Inches(11.333), Inches(5.2))
    cbox.fill.solid()
    cbox.fill.fore_color.rgb = COLOR_BG_CARD
    cbox.line.color.rgb = COLOR_CARD_BORDER
    cbox.line.width = Pt(3.0)

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
    cp2.text = "\"Communication When Everything Else Fails.\""
    cp2.font.size = Pt(28)
    cp2.font.bold = True
    cp2.font.color.rgb = COLOR_TEXT_PRIMARY
    cp2.alignment = PP_ALIGN.CENTER
    cp2.space_after = Pt(18)

    cp3 = ctf.add_paragraph()
    cp3.text = "• Phase 2 achieved complete on-device intelligence & low-latency calling."
    cp3.font.size = Pt(25)
    cp3.font.color.rgb = COLOR_TEXT_SECONDARY
    cp3.alignment = PP_ALIGN.CENTER
    cp3.space_after = Pt(10)

    cp4 = ctf.add_paragraph()
    cp4.text = "• Phase 3 established production-grade UI/UX with verified dual-device stability."
    cp4.font.size = Pt(25)
    cp4.font.color.rgb = COLOR_TEXT_SECONDARY
    cp4.alignment = PP_ALIGN.CENTER
    cp4.space_after = Pt(10)

    cp5 = ctf.add_paragraph()
    cp5.text = "• A complete life-saving ecosystem ready for real-world deployment."
    cp5.font.size = Pt(25)
    cp5.font.color.rgb = COLOR_CARD_BORDER
    cp5.font.bold = True
    cp5.alignment = PP_ALIGN.CENTER

    out_file = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_Phase3_Master_Presentation.pptx"
    prs.save(out_file)
    print("SUCCESS: Saved presentation to:", out_file)

    # Also save a copy in MeshLinkOffline
    out_file2 = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Master_Presentation.pptx"
    prs.save(out_file2)
    print("SUCCESS: Saved presentation to:", out_file2)

if __name__ == "__main__":
    build_nexus_master_deck()
