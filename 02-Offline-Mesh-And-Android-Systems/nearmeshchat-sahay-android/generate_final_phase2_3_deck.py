import os
import win32com.client
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    COLOR_LIME = RGBColor(126, 217, 87)       # #7ED957
    COLOR_BLUE = RGBColor(18, 34, 157)        # #12229D
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_DARK = RGBColor(15, 23, 42)         # #0F172A
    COLOR_ACCENT_GREEN = RGBColor(16, 185, 129)
    COLOR_RED = RGBColor(239, 68, 68)

    FONT_TITLE = "Anton"
    FONT_BODY = "Inter"

    assets_dir = r"C:\Users\abdul\.gemini\antigravity\brain\6595af32-c191-4f5f-9a11-badad9549133\scratch\polished_assets"
    pie_chart_path = os.path.join(assets_dir, "3d_pie_chart.png")
    bar_chart_path = os.path.join(assets_dir, "3d_bar_comparison.png")

    mock_chats = os.path.join(assets_dir, "mock_chats.png")
    mock_calls = os.path.join(assets_dir, "mock_calls.png")
    mock_radar = os.path.join(assets_dir, "mock_radar.png")
    mock_portal = os.path.join(assets_dir, "mock_portal.png")
    mock_ai = os.path.join(assets_dir, "mock_ai.png")
    mock_sos = os.path.join(assets_dir, "mock_sos.png")
    mock_profile = os.path.join(assets_dir, "mock_profile.png")

    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_LIME
        bg.line.fill.background()
        return bg

    def add_top_bar(slide, slide_num_str):
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(0.40), Inches(12.133), Inches(0.85))
        bar.fill.solid()
        bar.fill.fore_color.rgb = COLOR_BLUE
        bar.line.color.rgb = COLOR_WHITE
        bar.line.width = Pt(2.5)

        tf = bar.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run1 = p.add_run()
        run1.text = " NEXUS MESHLINK"
        run1.font.name = FONT_TITLE
        run1.font.size = Pt(27)
        run1.font.bold = True
        run1.font.color.rgb = COLOR_WHITE

        run_space = p.add_run()
        run_space.text = " " * 38

        run2 = p.add_run()
        run2.text = f"#{slide_num_str}"
        run2.font.name = FONT_TITLE
        run2.font.size = Pt(27)
        run2.font.bold = True
        run2.font.color.rgb = COLOR_WHITE
        return bar

    def add_header_banner(slide, title_text):
        hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.35), Inches(12.133), Inches(0.88))
        hdr.fill.solid()
        hdr.fill.fore_color.rgb = COLOR_BLUE
        hdr.line.color.rgb = COLOR_WHITE
        hdr.line.width = Pt(2.5)

        tf = hdr.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = title_text.upper()
        run.font.name = FONT_TITLE
        run.font.size = Pt(25)
        run.font.bold = True
        run.font.color.rgb = COLOR_WHITE
        return hdr

    def add_card(slide, left, top, width, height, bg_color=COLOR_WHITE, border_color=COLOR_BLUE):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(3.5)
        return card

    def add_outline_badge(slide, left, top, width, height, text, bg_color=COLOR_BLUE, border_color=COLOR_BLUE, text_color=COLOR_WHITE):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = bg_color
        box.line.color.rgb = border_color
        box.line.width = Pt(2.5)

        tf = box.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = text.upper()
        run.font.name = FONT_TITLE
        run.font.size = Pt(19)
        run.font.bold = True
        run.font.color.rgb = text_color
        return box

    def add_bullets(slide, left, top, width, height, bullets, text_color=COLOR_DARK, font_size=25):
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.word_wrap = True
        for i, b_text in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = f"• {b_text}"
            p.font.name = FONT_BODY
            p.font.size = Pt(font_size)
            p.font.bold = True
            p.font.color.rgb = text_color
            p.space_after = Pt(10)
        return tb

    # ==================== SLIDE 1: COVER ====================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)
    c1 = add_card(s1, Inches(1.2), Inches(1.1), Inches(10.933), Inches(5.3), bg_color=COLOR_BLUE, border_color=COLOR_WHITE)
    tf1 = c1.text_frame
    tf1.word_wrap = True
    p1_1 = tf1.paragraphs[0]
    p1_1.alignment = PP_ALIGN.CENTER
    r1_1 = p1_1.add_run()
    r1_1.text = "NEXUS MESHLINK"
    r1_1.font.name = FONT_TITLE
    r1_1.font.size = Pt(56)
    r1_1.font.bold = True
    r1_1.font.color.rgb = COLOR_LIME

    p1_2 = tf1.add_paragraph()
    p1_2.alignment = PP_ALIGN.CENTER
    r1_2 = p1_2.add_run()
    r1_2.text = "AUTONOMOUS P2P OFF-GRID MESH & ON-DEVICE AI"
    r1_2.font.name = FONT_TITLE
    r1_2.font.size = Pt(28)
    r1_2.font.bold = True
    r1_2.font.color.rgb = COLOR_WHITE
    p1_2.space_before = Pt(16)

    p1_3 = tf1.add_paragraph()
    p1_3.alignment = PP_ALIGN.CENTER
    r1_3 = p1_3.add_run()
    r1_3.text = "Zero Internet • Zero Routers • Native Qwen AI • HD Voice/Video Calls"
    r1_3.font.name = FONT_BODY
    r1_3.font.size = Pt(25)
    r1_3.font.bold = True
    r1_3.font.color.rgb = COLOR_WHITE
    p1_3.space_before = Pt(26)

    # ==================== SLIDE 2: THE BLACKOUT REALITY ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_top_bar(s2, "02")
    add_header_banner(s2, "THE PROBLEM: WHY CELLULAR & INTERNET FAIL")
    add_card(s2, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s2, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "SINGLE POINT OF FAILURE CRASH")
    add_bullets(s2, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Disasters, cyclones & war collapse cell towers in minutes.",
        "Total blackout: WhatsApp, Telegram & Zello become dead.",
        "Solution: A 100% decentralized mesh connecting directly device-to-device without internet."
    ], font_size=25)
    if os.path.exists(mock_chats):
        s2.shapes.add_picture(mock_chats, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 3: COMPETITOR LANDSCAPE ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_top_bar(s3, "03")
    add_header_banner(s3, "PHASE 2: COMPETITOR ANALYSIS & FATAL GAPS")
    
    # Left Card: Bridgefy & Briar
    add_card(s3, Inches(0.6), Inches(2.40), Inches(5.9), Inches(4.75))
    add_outline_badge(s3, Inches(0.8), Inches(2.55), Inches(5.5), Inches(0.65), "BRIDGEFY & BRIAR (BLE ONLY)", bg_color=COLOR_RED, border_color=COLOR_RED)
    add_bullets(s3, Inches(0.8), Inches(3.35), Inches(5.5), Inches(3.6), [
        "Throttled to 1-2 Mbps Bluetooth with high packet drops.",
        "ZERO voice or video calling on mesh.",
        "ZERO offline AI intelligence — static text only."
    ], font_size=24)

    # Right Card: Walkie Talkies & WhatsApp
    add_card(s3, Inches(6.8), Inches(2.40), Inches(5.9), Inches(4.75))
    add_outline_badge(s3, Inches(7.0), Inches(2.55), Inches(5.5), Inches(0.65), "ZELLO & WHATSAPP (CLOUD SLAVES)", bg_color=COLOR_RED, border_color=COLOR_RED)
    add_bullets(s3, Inches(7.0), Inches(3.35), Inches(5.5), Inches(3.6), [
        "Zello requires cellular data & cloud servers to operate.",
        "Tower down = Zello completely dead! Zero mesh.",
        "WhatsApp / Signal impossible without SIM & servers."
    ], font_size=24)

    # ==================== SLIDE 4: 3D BENCHMARK COMPARISON ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_top_bar(s4, "04")
    add_header_banner(s4, "PHASE 2: 3D PERFORMANCE BENCHMARK VS COMPETITORS")
    add_card(s4, Inches(0.6), Inches(2.40), Inches(5.6), Inches(4.75))
    add_outline_badge(s4, Inches(0.8), Inches(2.55), Inches(5.2), Inches(0.65), "THROUGHPUT REVOLUTION")
    add_bullets(s4, Inches(0.8), Inches(3.35), Inches(5.2), Inches(3.6), [
        "Nexus MeshLink delivers 250 Mbps via Wi-Fi Direct.",
        "125x faster than Bridgefy (2 Mbps BLE bottleneck).",
        "Enables instant HD photo transfers & video streaming."
    ], font_size=25)
    
    # Chart inside card
    add_card(s4, Inches(6.5), Inches(2.40), Inches(6.2), Inches(4.75))
    if os.path.exists(bar_chart_path):
        s4.shapes.add_picture(bar_chart_path, Inches(6.6), Inches(2.50), width=Inches(6.0))

    # ==================== SLIDE 5: 3D PIE CHART ARCHITECTURE ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_top_bar(s5, "05")
    add_header_banner(s5, "PHASE 2: OFF-GRID PROTOCOL CAPACITY (3D PIE)")
    add_card(s5, Inches(0.6), Inches(2.40), Inches(5.6), Inches(4.75))
    add_outline_badge(s5, Inches(0.8), Inches(2.55), Inches(5.2), Inches(0.65), "TRI-LAYER PROTOCOL STACK")
    add_bullets(s5, Inches(0.8), Inches(3.35), Inches(5.2), Inches(3.6), [
        "65% Wi-Fi Direct: Ultra-fast 250 Mbps mesh data link.",
        "20% BLE Gossip: Ultra-low power peer beaconing.",
        "15% Laptop Server: Local HTTP vault & knowledge.",
        "0% Cloud Reliance: 100% operational in blackouts."
    ], font_size=24)

    # Chart inside card
    add_card(s5, Inches(6.5), Inches(2.40), Inches(6.2), Inches(4.75))
    if os.path.exists(pie_chart_path):
        s5.shapes.add_picture(pie_chart_path, Inches(6.6), Inches(2.50), width=Inches(6.0))

    # ==================== SLIDE 6: WHY NEXUS IS SUPERIOR (5 POLISHED CARDS) ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_top_bar(s6, "06")
    add_header_banner(s6, "PHASE 2: WHY NEXUS IS BEST — OUR 5 CORE USPs")
    
    # Top Row: 3 Cards (Speed, AI, Calling)
    # Card 1: 250 Mbps Speed
    add_card(s6, Inches(0.6), Inches(2.40), Inches(3.85), Inches(2.28))
    add_outline_badge(s6, Inches(0.75), Inches(2.50), Inches(3.55), Inches(0.55), "250 MBPS MESH SPEED", bg_color=COLOR_BLUE, border_color=COLOR_BLUE)
    add_bullets(s6, Inches(0.75), Inches(3.15), Inches(3.55), Inches(1.45), [
        "125x faster than Bridgefy BLE.",
        "Instant HD photos & media sync."
    ], font_size=20)

    # Card 2: Offline AI
    add_card(s6, Inches(4.74), Inches(2.40), Inches(3.85), Inches(2.28))
    add_outline_badge(s6, Inches(4.89), Inches(2.50), Inches(3.55), Inches(0.55), "100% ON-DEVICE AI", bg_color=COLOR_BLUE, border_color=COLOR_BLUE)
    add_bullets(s6, Inches(4.89), Inches(3.15), Inches(3.55), Inches(1.45), [
        "Embedded Qwen LLM on CPU/NPU.",
        "Zero server, zero cloud, 100% private."
    ], font_size=20)

    # Card 3: P2P Calling
    add_card(s6, Inches(8.88), Inches(2.40), Inches(3.85), Inches(2.28))
    add_outline_badge(s6, Inches(9.03), Inches(2.50), Inches(3.55), Inches(0.55), "P2P ENCRYPTED CALLS", bg_color=COLOR_BLUE, border_color=COLOR_BLUE)
    add_bullets(s6, Inches(9.03), Inches(3.15), Inches(3.55), Inches(1.45), [
        "HD Voice & Video over Wi-Fi Direct.",
        "Zero SIM card or tower needed."
    ], font_size=20)

    # Bottom Row: 2 Cards (Laptop Server & Emergency SOS)
    # Card 4: Laptop Web Portal
    add_card(s6, Inches(0.6), Inches(4.82), Inches(5.9), Inches(2.32))
    add_outline_badge(s6, Inches(0.8), Inches(4.94), Inches(5.5), Inches(0.55), "LAPTOP WEB VAULT (PORT 8888)", bg_color=COLOR_BLUE, border_color=COLOR_BLUE)
    add_bullets(s6, Inches(0.8), Inches(5.58), Inches(5.5), Inches(1.48), [
        "Turns any PC into an off-grid field server & knowledge hub.",
        "Distributes emergency docs, maps & live telemetry."
    ], font_size=21)

    # Card 5: Emergency SOS
    add_card(s6, Inches(6.83), Inches(4.82), Inches(5.9), Inches(2.32))
    add_outline_badge(s6, Inches(7.03), Inches(4.94), Inches(5.5), Inches(0.55), "1-TAP EMERGENCY SOS BEACON", bg_color=COLOR_RED, border_color=COLOR_RED)
    add_bullets(s6, Inches(7.03), Inches(5.58), Inches(5.5), Inches(1.48), [
        "Instant distress broadcast with GPS coordinates (±2m).",
        "Triggers high-frequency acoustic beacon siren."
    ], font_size=21)

    # ==================== SLIDE 7: FEATURE: MESH CHAT ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_top_bar(s7, "07")
    add_header_banner(s7, "FEATURE 1: DUAL-STACK P2P MESH CHAT")
    add_card(s7, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s7, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "HIGH-SPEED OFFLINE CHAT")
    add_bullets(s7, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Auto-discovery via BLE Beaconing + Wi-Fi Direct links.",
        "Broadcast Channel reaches all nearby nodes simultaneously.",
        "Direct 1-on-1 private encrypted chats with delivery ticks.",
        "Autonomous store-and-forward routing when peers drop."
    ], font_size=24)
    if os.path.exists(mock_chats):
        s7.shapes.add_picture(mock_chats, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 8: FEATURE: OFFLINE AI ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_top_bar(s8, "08")
    add_header_banner(s8, "FEATURE 2: 100% ON-DEVICE QWEN AI INTELLIGENCE")
    add_card(s8, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s8, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "ZERO-SERVER NATIVE LLAMA.CPP")
    add_bullets(s8, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Embedded libllama C++ runtime running Qwen LLM on CPU/NPU.",
        "Instant survival advice, emergency triage, code, and math.",
        "Zero tokens sent to cloud — 100% private and offline.",
        "Quick emergency pills: Recursion, First Aid, Code."
    ], font_size=24)
    if os.path.exists(mock_ai):
        s8.shapes.add_picture(mock_ai, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 9: FEATURE: P2P CALLS ====================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_top_bar(s9, "09")
    add_header_banner(s9, "FEATURE 3: HD ENCRYPTED VOICE & VIDEO CALLS")
    add_card(s9, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s9, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "ZERO-CELLULAR P2P CALLING")
    add_bullets(s9, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Direct socket audio & video streaming over Wi-Fi Direct.",
        "Ultra-low latency (<28ms) with Opus audio codec.",
        "Zero SIM card or tower needed — works in airplane mode.",
        "Recent calls log tracks encrypted mesh call duration."
    ], font_size=24)
    if os.path.exists(mock_calls):
        s9.shapes.add_picture(mock_calls, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 10: FEATURE: LAPTOP WEB PORTAL ====================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_top_bar(s10, "10")
    add_header_banner(s10, "FEATURE 4: DECENTRALIZED LAPTOP WEB PORTAL")
    add_card(s10, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s10, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "LOCAL HTTP KNOWLEDGE VAULT")
    add_bullets(s10, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Turns any PC into a field server over Wi-Fi (Port 8888).",
        "Embedded web client browses emergency docs & manuals.",
        "Shared File Hub for rapid distribution of rescue maps.",
        "Real-time server telemetry and connected peer sockets."
    ], font_size=24)
    if os.path.exists(mock_portal):
        s10.shapes.add_picture(mock_portal, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 11: FEATURE: SOS BEACON ====================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_top_bar(s11, "11")
    add_header_banner(s11, "FEATURE 5: AUTONOMOUS EMERGENCY SOS BROADCAST")
    add_card(s11, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s11, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "LIFE-SAVING DISTRESS SIGNAL", bg_color=COLOR_RED, border_color=COLOR_RED)
    add_bullets(s11, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "1-Tap floating red SOS button accessible from every tab.",
        "Attaches live GPS coordinates: Accuracy within ±2m.",
        "Triggers high-frequency acoustic beacon siren for rescue.",
        "Dispatches high-priority distress signal across all mesh hops."
    ], font_size=24)
    if os.path.exists(mock_sos):
        s11.shapes.add_picture(mock_sos, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 12: PHASE 3 UX PHILOSOPHY ====================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_top_bar(s12, "12")
    add_header_banner(s12, "PHASE 3: WHY THIS UI/UX DESIGN WAS CHOSEN")
    add_card(s12, Inches(0.6), Inches(2.40), Inches(12.133), Inches(4.75))
    add_outline_badge(s12, Inches(1.0), Inches(2.55), Inches(11.333), Inches(0.65), "TACTICAL SIMPLICITY & STRESS PSYCHOLOGY")
    add_bullets(s12, Inches(1.0), Inches(3.35), Inches(11.333), Inches(3.6), [
        "Disaster psychology: High-stress users experience severe tunnel vision.",
        "Zero Complexity: Complex menus and deep settings cause fatal delays.",
        "Single-Thumb Reach: Every life-saving tool is reachable with 1 hand.",
        "Persistent Feedback: User always knows if mesh is active or scanning.",
        "Design Rule: Maximum visual clarity, minimum cognitive load in crises."
    ], font_size=25)

    # ==================== SLIDE 13: DESIGN DECISION 1: COLOR PALETTE ====================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s13)
    add_top_bar(s13, "13")
    add_header_banner(s13, "PHASE 3 DESIGN: COLOR PSYCHOLOGY & VISIBILITY")
    
    # Left Card: Lime / Green
    add_card(s13, Inches(0.6), Inches(2.40), Inches(5.9), Inches(4.75))
    add_outline_badge(s13, Inches(0.8), Inches(2.55), Inches(5.5), Inches(0.65), "LIME & EMERALD GREEN (#7ED957)", bg_color=COLOR_ACCENT_GREEN, border_color=COLOR_ACCENT_GREEN)
    add_bullets(s13, Inches(0.8), Inches(3.35), Inches(5.5), Inches(3.6), [
        "Maximum outdoor readability under sunlight & smoke.",
        "Psychological signal of safety & active mesh health.",
        "High contrast against white cards prevents eye fatigue."
    ], font_size=24)

    # Right Card: Royal Blue & Red
    add_card(s13, Inches(6.8), Inches(2.40), Inches(5.9), Inches(4.75))
    add_outline_badge(s13, Inches(7.0), Inches(2.55), Inches(5.5), Inches(0.65), "ROYAL BLUE & SIGNAL RED", bg_color=COLOR_BLUE, border_color=COLOR_BLUE)
    add_bullets(s13, Inches(7.0), Inches(3.35), Inches(5.5), Inches(3.6), [
        "Royal Blue (#12229D): Institutional trust & stability.",
        "Signal Red (#EF4444): Reserved strictly for SOS alert.",
        "Color hierarchy guides the eye to what matters instantly."
    ], font_size=24)

    # ==================== SLIDE 14: DESIGN DECISION 2: 5-TAB ERGONOMICS ====================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14)
    add_top_bar(s14, "14")
    add_header_banner(s14, "PHASE 3 DESIGN: 5-TAB BOTTOM NAVIGATION & SOS FAB")
    add_card(s14, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s14, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "THUMB-ZONE ERGONOMICS")
    add_bullets(s14, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Bottom bar keeps all 5 modes (Chat, Call, Radar, Web, AI) in reach.",
        "No hamburger menus: Switching modes takes exactly 1 tap.",
        "Floating SOS FAB is fixed above bottom bar — zero menu hunting.",
        "Optimized for one-handed operation during rescue and field walking."
    ], font_size=24)
    if os.path.exists(mock_chats):
        s14.shapes.add_picture(mock_chats, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 15: DESIGN DECISION 3: RADAR VISUALIZATION ====================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s15)
    add_top_bar(s15, "15")
    add_header_banner(s15, "PHASE 3 DESIGN: RUVNET WAVE RADAR PROXIMITY")
    add_card(s15, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s15, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "SPATIAL DISTANCE AWARENESS")
    add_bullets(s15, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Why Radar? Raw MAC address lists are confusing in emergencies.",
        "Concentric rings (2m, 5m, 10m) show immediate proximity.",
        "Wi-Fi sensing wave sweep indicates active scan without lag.",
        "Transforms complex RF signal strength (RSSI) into intuitive distance."
    ], font_size=24)
    if os.path.exists(mock_radar):
        s15.shapes.add_picture(mock_radar, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 16: DESIGN DECISION 4: IDENTITY & SECURITY ====================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s16)
    add_top_bar(s16, "16")
    add_header_banner(s16, "PHASE 3 DESIGN: CRYPTOGRAPHIC NODE IDENTITY")
    add_card(s16, Inches(0.6), Inches(2.40), Inches(6.9), Inches(4.75))
    add_outline_badge(s16, Inches(0.9), Inches(2.55), Inches(6.3), Inches(0.65), "SECURE OFF-GRID PROFILES")
    add_bullets(s16, Inches(0.9), Inches(3.35), Inches(6.3), Inches(3.6), [
        "Emergency Roles (Doctor, Citizen, Rescue) for triage priority.",
        "Cryptographic Node ID (mesh@fa089145e9a5) prevents spoofing.",
        "Profile & Avatar sync across mesh over direct sockets.",
        "Zero phone number or email tracking required for complete privacy."
    ], font_size=24)
    if os.path.exists(mock_profile):
        s16.shapes.add_picture(mock_profile, Inches(8.3), Inches(2.40), height=Inches(4.75))

    # ==================== SLIDE 17: FIELD VERIFICATION ====================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s17)
    add_top_bar(s17, "17")
    add_header_banner(s17, "MULTI-DEVICE FIELD TESTING & HARDWARE TELEMETRY")
    add_card(s17, Inches(0.6), Inches(2.40), Inches(12.133), Inches(4.75))
    add_outline_badge(s17, Inches(1.0), Inches(2.55), Inches(11.333), Inches(0.65), "PROVEN ON PHYSICAL ANDROID HARDWARE")
    add_bullets(s17, Inches(1.0), Inches(3.35), Inches(11.333), Inches(3.6), [
        "Oppo Reno2 F (MediaTek Helio P70, 8GB RAM, Android 11): 100% verified.",
        "Nova 1 5G (Dimensity 6080, 8GB RAM, Android 14): 100% verified.",
        "Tested bidirectional HD photo sync, P2P calling, and RuVNet radar scanning.",
        "Zero packet drop recorded over 50 continuous Wi-Fi Direct socket transfers."
    ], font_size=25)

    # ==================== SLIDE 18: CONCLUSION ====================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s18)
    c18 = add_card(s18, Inches(1.2), Inches(1.1), Inches(10.933), Inches(5.3), bg_color=COLOR_BLUE, border_color=COLOR_WHITE)
    tf18 = c18.text_frame
    tf18.word_wrap = True
    p18_1 = tf18.paragraphs[0]
    p18_1.alignment = PP_ALIGN.CENTER
    r18_1 = p18_1.add_run()
    r18_1.text = "NEXUS MESHLINK"
    r18_1.font.name = FONT_TITLE
    r18_1.font.size = Pt(54)
    r18_1.font.bold = True
    r18_1.font.color.rgb = COLOR_LIME

    p18_2 = tf18.add_paragraph()
    p18_2.alignment = PP_ALIGN.CENTER
    r18_2 = p18_2.add_run()
    r18_2.text = "THE FUTURE OF RESILIENT OFF-GRID COMMUNICATION"
    r18_2.font.name = FONT_TITLE
    r18_2.font.size = Pt(28)
    r18_2.font.bold = True
    r18_2.font.color.rgb = COLOR_WHITE
    p18_2.space_before = Pt(16)

    p18_3 = tf18.add_paragraph()
    p18_3.alignment = PP_ALIGN.CENTER
    r18_3 = p18_3.add_run()
    r18_3.text = "Autonomous Mesh • 250 Mbps Throughput • 100% Offline AI • Zero Cloud Reliance"
    r18_3.font.name = FONT_BODY
    r18_3.font.size = Pt(25)
    r18_3.font.bold = True
    r18_3.font.color.rgb = COLOR_WHITE
    p18_3.space_before = Pt(26)

    output_path = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_3_Master_Final.pptx"
    try:
        prs.save(output_path)
    except PermissionError:
        output_path = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_3_Master_V2.pptx"
        prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

    # Apply smooth modern slide transition (Push Left - Canva/Keynote style)
    try:
        ppt = win32com.client.Dispatch("PowerPoint.Application")
        pres = ppt.Presentations.Open(os.path.abspath(output_path), WithWindow=False)
        for s in pres.Slides:
            s.SlideShowTransition.EntryEffect = 3843 # ppEffectPushLeft (modern smooth slide-in)
            s.SlideShowTransition.Duration = 0.25
        pres.Save()
        pres.Close()
        print("Smooth PushLeft slide transitions applied via COM.")
    except Exception as e:
        print("COM transition notice:", e)

if __name__ == "__main__":
    build_presentation()
