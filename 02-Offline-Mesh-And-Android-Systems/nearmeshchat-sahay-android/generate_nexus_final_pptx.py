import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def build_no_logo_nexus_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Classic 3D Metallic & Emerald Palette
    COLOR_BG_DARK = RGBColor(11, 15, 25)         # #0B0F19 (Deep Charcoal)
    COLOR_CARD_BG = RGBColor(23, 32, 51)         # #172033 (Dark Slate Glass)
    COLOR_CARD_SHADOW = RGBColor(3, 5, 10)       # #03050A (3D Shadow)
    COLOR_SILVER_BORDER = RGBColor(226, 232, 240)# #E2E8F0 (Metallic Silver Border)
    COLOR_SILVER_LIGHT = RGBColor(248, 250, 252) # #F8FAFC (White/Silver)
    COLOR_GREEN = RGBColor(34, 197, 94)          # #22C55E (Vibrant Emerald Green)
    COLOR_GREEN_DARK = RGBColor(22, 101, 52)     # #166534 (Dark Emerald)
    COLOR_WHITE = RGBColor(255, 255, 255)        # #FFFFFF (Pure White)
    COLOR_GRAY_MUTED = RGBColor(160, 174, 192)   # #A0AEC0 (Silver Gray)

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG_DARK
        bg.line.fill.background()
        
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.1))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_GREEN
        top_bar.line.fill.background()

    def add_header(slide, title_text, badge_text="NEXUS MESHLINK"):
        h_shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(0.43), Inches(12.2), Inches(0.95))
        h_shadow.fill.solid()
        h_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
        h_shadow.line.fill.background()

        header_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(0.35), Inches(12.2), Inches(0.95))
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = COLOR_CARD_BG
        header_box.line.color.rgb = COLOR_SILVER_BORDER
        header_box.line.width = Pt(2.5)

        tf = header_box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.35)
        tf.margin_right = Inches(2.2) # Guarantees header text stops before badge

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

        # Smaller compact badge tag on far right (no collision)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.85), Inches(0.55), Inches(1.65), Inches(0.48))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_GREEN
        badge.line.color.rgb = COLOR_WHITE
        badge.line.width = Pt(1.5)

        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = badge_text
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_BG_DARK

    def add_card(slide, left, top, width, height, title, bullet_items, border_color=COLOR_SILVER_BORDER, title_color=COLOR_GREEN, font_size=17.5):
        shadow = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.08), Inches(top + 0.08), Inches(width), Inches(height))
        shadow.fill.solid()
        shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
        shadow.line.fill.background()

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = border_color
        card.line.width = Pt(2.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.3)
        tf.margin_top = Inches(0.3)
        tf.margin_right = Inches(0.3)
        tf.margin_bottom = Inches(0.2)

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(22)
        p0.font.bold = True
        p0.font.color.rgb = title_color
        p0.space_after = Pt(10)

        for item in bullet_items:
            p = tf.add_paragraph()
            p.text = "◈ " + item
            p.font.size = Pt(font_size)
            p.font.bold = True
            p.font.color.rgb = COLOR_WHITE
            p.space_after = Pt(6)

    def add_node(slide, left, top, width, height, label, subtext="", node_color=COLOR_GREEN):
        ns = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.06), Inches(top + 0.06), Inches(width), Inches(height))
        ns.fill.solid()
        ns.fill.fore_color.rgb = COLOR_CARD_SHADOW
        ns.line.fill.background()

        node = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        node.fill.solid()
        node.fill.fore_color.rgb = COLOR_CARD_BG
        node.line.color.rgb = node_color
        node.line.width = Pt(2.5)

        tf = node.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p = tf.paragraphs[0]
        p.text = label
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = node_color

        if subtext:
            p2 = tf.add_paragraph()
            p2.text = subtext
            p2.alignment = PP_ALIGN.CENTER
            p2.font.size = Pt(13)
            p2.font.bold = True
            p2.font.color.rgb = COLOR_SILVER_LIGHT

    def add_arrow(slide, left, top, width, height, arrow_color=COLOR_GREEN):
        arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(left), Inches(top), Inches(width), Inches(height))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = arrow_color
        arrow.line.color.rgb = COLOR_WHITE
        arrow.line.width = Pt(1.5)

    def add_stat_box(slide, left, top, width, height, number, label, num_color=COLOR_GREEN):
        sbox = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left + 0.08), Inches(top + 0.08), Inches(width), Inches(height))
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = COLOR_CARD_SHADOW
        sbox.line.fill.background()

        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_SILVER_BORDER
        box.line.width = Pt(2.5)

        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p = tf.paragraphs[0]
        p.text = number
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(46)
        p.font.bold = True
        p.font.color.rgb = num_color

        p2 = tf.add_paragraph()
        p2.text = label
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(15)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_WHITE

    # =========================================================================
    # SLIDE 1: Cover Presentation Slide (NO LOGO AT ALL)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    c_shadow = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(1.28), Inches(10.933), Inches(5.1))
    c_shadow.fill.solid()
    c_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    c_shadow.line.fill.background()

    cover_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(10.933), Inches(5.1))
    cover_card.fill.solid()
    cover_card.fill.fore_color.rgb = COLOR_CARD_BG
    cover_card.line.color.rgb = COLOR_GREEN
    cover_card.line.width = Pt(3.5)

    tf1 = cover_card.text_frame
    tf1.word_wrap = True
    tf1.margin_top = Inches(0.4)

    p = tf1.paragraphs[0]
    p.text = "NEXUS MESHLINK"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(46)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(10)

    p = tf1.add_paragraph()
    p.text = "Off-Grid P2P Mesh Communication Suite — Phase 2 & Phase 3"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN
    p.space_after = Pt(30)

    p = tf1.add_paragraph()
    p.text = "PROJECT PRESENTER"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_SILVER_BORDER
    p.space_after = Pt(6)

    p = tf1.add_paragraph()
    p.text = "Shaikh Abdul Zubair Abdul Kabir"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(10)

    p = tf1.add_paragraph()
    p.text = "SRK Institute of Management and Computer Application"
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_GRAY_MUTED

    # Bottom 4 Badges
    badges = [
        ("Off-Grid Mesh", 1.8),
        ("720p UDP Streaming", 4.4),
        ("RuVNet 3D Radar", 7.0),
        ("RSA + AES Security", 9.6)
    ]
    for text, left in badges:
        b = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(5.4), Inches(2.3), Inches(0.5))
        b.fill.solid()
        b.fill.fore_color.rgb = COLOR_GREEN_DARK
        b.line.color.rgb = COLOR_GREEN
        b.line.width = Pt(1.5)
        btf = b.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.text = text
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(12)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_WHITE

    # =========================================================================
    # SLIDE 2: Problem Statement & Vision
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "02. Executive Problem Statement & Mesh Vision", "VISION")

    add_card(s2, 0.5, 1.45, 5.9, 5.5, "The Off-Grid Crisis", [
        "Cellular Grid Failure: Disasters & blackouts destroy phone towers completely.",
        "Cloud App Shutdown: Apps like WhatsApp stop working without cloud servers.",
        "Severe Isolation: Phones 10m apart cannot talk without cell towers."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=17.5)

    add_card(s2, 6.9, 1.45, 5.9, 5.5, "The Nexus Mesh Solution", [
        "100% Serverless & Zero SIM: Direct P2P radio over Wi-Fi Direct & BLE 5.0.",
        "Dynamic Multi-Hop Relay: Phones automatically relay encrypted packets.",
        "Full Off-Grid Suite: Text Chat, Voice, 720p Video Calls & RuVNet Radar."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=17.5)

    # =========================================================================
    # SLIDE 3: Phase 2 — Gossip Routing (WITH FLOWCHART)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "03. Phase 2: Multi-Hop Gossip Routing Flowchart", "PHASE 2")

    f_shadow = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(1.53), Inches(12.2), Inches(2.45))
    f_shadow.fill.solid()
    f_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    f_shadow.line.fill.background()

    flow_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.45), Inches(12.2), Inches(2.45))
    flow_box.fill.solid()
    flow_box.fill.fore_color.rgb = COLOR_CARD_BG
    flow_box.line.color.rgb = COLOR_GREEN
    flow_box.line.width = Pt(2.5)

    add_node(s3, 0.8, 1.8, 2.2, 1.75, "Device A\n(Origin)", "Gen Packet ID\nSet TTL = 5", COLOR_WHITE)
    add_arrow(s3, 3.1, 2.5, 0.5, 0.35)

    add_node(s3, 3.7, 1.8, 2.4, 1.75, "Relay Node B", "De-duplicate Check\nForward Packet", COLOR_GREEN)
    add_arrow(s3, 6.2, 2.5, 0.5, 0.35)

    add_node(s3, 6.8, 1.8, 2.4, 1.75, "Relay Node C", "Decrement TTL\nBroadcast Mesh", COLOR_GREEN)
    add_arrow(s3, 9.3, 2.5, 0.5, 0.35)

    add_node(s3, 9.9, 1.8, 2.4, 1.75, "Device D\n(Target)", "Match Target MAC\nDecrypt Payload", COLOR_WHITE)

    add_card(s3, 0.5, 4.1, 5.9, 2.9, "Dynamic Peer Discovery", [
        "Hybrid Scan: Wi-Fi Direct P2P & BLE 5.0 scanning.",
        "NSD (mDNS): Auto-resolves local mesh IP endpoints."
    ], font_size=16)

    add_card(s3, 6.9, 4.1, 5.9, 2.9, "Store-and-Forward Engine", [
        "De-duplication: Unique Packet ID prevents loops.",
        "Store-and-Forward: Buffers packets until peer is in range."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=16)

    # =========================================================================
    # SLIDE 4: Phase 3 — Voice & 720p Video UDP Engine (WITH PIPELINE)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "04. Phase 3: P2P Voice & 720p Video UDP Engine", "PHASE 3")

    p_shadow = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(1.53), Inches(12.2), Inches(2.45))
    p_shadow.fill.solid()
    p_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    p_shadow.line.fill.background()

    pipe_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.45), Inches(12.2), Inches(2.45))
    pipe_box.fill.solid()
    pipe_box.fill.fore_color.rgb = COLOR_CARD_BG
    pipe_box.line.color.rgb = COLOR_SILVER_BORDER
    pipe_box.line.width = Pt(2.5)

    add_node(s4, 0.7, 1.8, 2.0, 1.75, "Camera / Mic", "720p @ 30FPS\n16kHz Audio", COLOR_WHITE)
    add_arrow(s4, 2.8, 2.5, 0.4, 0.35)

    add_node(s4, 3.3, 1.8, 2.2, 1.75, "MediaCodec", "H.264 Video Encode\nOpus Audio", COLOR_SILVER_LIGHT)
    add_arrow(s4, 5.6, 2.5, 0.4, 0.35)

    add_node(s4, 6.1, 1.8, 2.2, 1.75, "UDP Socket", "Voice Port: 50005\nVideo Port: 50006", COLOR_GREEN)
    add_arrow(s4, 8.4, 2.5, 0.4, 0.35)

    add_node(s4, 8.9, 1.8, 1.9, 1.75, "Wi-Fi Direct", "Direct Radio Link\nZero Router", COLOR_GREEN)
    add_arrow(s4, 10.9, 2.5, 0.35, 0.35)

    add_node(s4, 11.3, 1.8, 1.2, 1.75, "Render", "Sub-100ms", COLOR_WHITE)

    add_stat_box(s4, 0.5, 4.1, 3.8, 2.9, "< 50 ms", "Voice Socket Latency\n(Direct UDP Datagram)", COLOR_GREEN)
    add_stat_box(s4, 4.7, 4.1, 3.9, 2.9, "720p 30FPS", "H.264 Video Stream\n(Hardware Acceleration)", COLOR_WHITE)
    add_stat_box(s4, 8.9, 4.1, 3.8, 2.9, "Port 50005/6", "Stream Socket Ports\n(Sub-100ms Performance)", COLOR_GREEN)

    # =========================================================================
    # SLIDE 5: RuVNet Wi-Fi Wave Sensing 3D Radar
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "05. RuVNet Wi-Fi Wave Sensing 3D Radar", "AI SENSING")

    add_card(s5, 0.5, 1.45, 5.9, 5.5, "RuVNet Wave Sensing Tech", [
        "Camera-Free Detection: Detects human movement through walls & pitch darkness without optical cameras.",
        "Signal Disturbance Analysis: Measures multipath Wi-Fi signal reflections caused by body movement.",
        "Disaster Search & Rescue: Locates trapped victims in rubble while preserving 100% privacy."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=17.5)

    add_card(s5, 6.9, 1.45, 5.9, 5.5, "3D Radar Processing Pipeline", [
        "1. Emission: 2.4GHz / 5GHz Wi-Fi radio wave propagation.",
        "2. Perturbation: Human motion induces phase shifts & wave reflections.",
        "3. Extraction: Algorithmic extraction of Doppler variance features.",
        "4. Render: Real-time X, Y, Z coordinates plotted on tactical radar."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=17.5)

    # =========================================================================
    # SLIDE 6: UI Design & Emerald Green (#16A34A) Rationale
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "06. UI Design & Emerald Green (#16A34A) Rationale", "UI SYSTEM")

    add_card(s6, 0.5, 1.45, 5.9, 5.5, "Emerald Green Color Rationale", [
        "High Outdoor Contrast: Emerald green provides maximum legibility under harsh sunlight.",
        "Night Rescue Low Strain: Prevents night-blindness during dark field rescue operations.",
        "OLED Power Savings: Deep Slate (#0F172A) + Emerald Green saves up to 35% AMOLED battery."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=17.5)

    add_card(s6, 6.9, 1.45, 5.9, 5.5, "App Screen UI Architecture", [
        "1. Mesh Navigation Bar: Toggles between Mesh Chat, Calls, RuVNet Radar & SOS Tools.",
        "2. Status Header: Real-time peer counter & Wi-Fi Direct connection state.",
        "3. Call Control Overlay: Floating Audio/Video feed overlay with live latency readout."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=17.5)

    # =========================================================================
    # SLIDE 7: Technical Stack & API Breakdown
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "07. Technical Stack & API Dependencies", "TECH STACK")

    add_card(s7, 0.5, 1.45, 2.8, 5.5, "Android P2P", [
        "Android SDK 34",
        "Kotlin Coroutines",
        "WifiP2pManager",
        "NSD (mDNS)",
        "BLE 5.0 Scanner"
    ], title_color=COLOR_GREEN, font_size=16)

    add_card(s7, 3.6, 1.45, 2.8, 5.5, "Media Stream", [
        "Camera2 API",
        "MediaCodec H.264",
        "AudioRecord PCM",
        "AudioTrack Render",
        "SurfaceView"
    ], title_color=COLOR_WHITE, font_size=16)

    add_card(s7, 6.7, 1.45, 2.8, 5.5, "Networking", [
        "DatagramSocket UDP",
        "ServerSocket TCP",
        "NanoHTTPD Server",
        "NIO ByteBuffers",
        "UDP Multicast"
    ], title_color=COLOR_GREEN, font_size=16)

    add_card(s7, 9.8, 1.45, 3.0, 5.5, "Security", [
        "RSA-2048 KeyPair",
        "Cipher AES-256",
        "SHA-256 Digest",
        "SecureRandom",
        "Base64 Armor"
    ], title_color=COLOR_WHITE, font_size=16)

    # =========================================================================
    # SLIDE 8: Cryptography & Security Shield (WITH FLOWCHART)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "08. Zero-Trust Cryptography & End-to-End Security", "SECURITY")

    c_shadow = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(1.53), Inches(12.2), Inches(2.45))
    c_shadow.fill.solid()
    c_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    c_shadow.line.fill.background()

    c_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.45), Inches(12.2), Inches(2.45))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_CARD_BG
    c_box.line.color.rgb = COLOR_GREEN
    c_box.line.width = Pt(2.5)

    add_node(s8, 0.8, 1.8, 2.2, 1.75, "Plaintext Data", "Outgoing Packet", COLOR_WHITE)
    add_arrow(s8, 3.1, 2.5, 0.5, 0.35)

    add_node(s8, 3.7, 1.8, 2.4, 1.75, "AES-256 GCM", "Symmetric Session Key\n12-byte IV + Auth Tag", COLOR_GREEN)
    add_arrow(s8, 6.2, 2.5, 0.5, 0.35)

    add_node(s8, 6.8, 1.8, 2.4, 1.75, "RSA-2048 Wrap", "Encrypt Session Key with\nTarget Public Key", COLOR_WHITE)
    add_arrow(s8, 9.3, 2.5, 0.5, 0.35)

    add_node(s8, 9.9, 1.8, 2.4, 1.75, "Recipient Decrypt", "Private Key Unwraps Key\nDecrypts Payload", COLOR_GREEN)

    add_card(s8, 0.5, 4.1, 5.9, 2.9, "Key Exchange", [
        "Zero Central Server: Exchanged P2P during node discovery.",
        "Ephemeral Keys: AES-256 keys refresh per session."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=16)

    add_card(s8, 6.9, 4.1, 5.9, 2.9, "Packet Protection", [
        "GCM Auth Tag: Detects packet modifications in transit.",
        "SHA-256 Signatures: Rejects spoofed mesh relay frames."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=16)

    # =========================================================================
    # SLIDE 9: Emergency SOS Broadcast & Survival Suite (WITH SOS TREE)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "09. Emergency SOS Broadcast & Survival Suite", "SURVIVAL")

    sos_shadow = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(1.53), Inches(12.2), Inches(2.45))
    sos_shadow.fill.solid()
    sos_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    sos_shadow.line.fill.background()

    sos_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.45), Inches(12.2), Inches(2.45))
    sos_box.fill.solid()
    sos_box.fill.fore_color.rgb = COLOR_CARD_BG
    sos_box.line.color.rgb = COLOR_SILVER_BORDER
    sos_box.line.width = Pt(2.5)

    add_node(s9, 0.8, 1.8, 2.2, 1.75, "1-Tap SOS", "Victim Broadcast Beacon", COLOR_WHITE)
    add_arrow(s9, 3.1, 2.5, 0.5, 0.35)

    add_node(s9, 3.7, 1.8, 2.4, 1.75, "Mesh Relay", "Bypasses Hop Limits\nMax Transmit Power", COLOR_GREEN)
    add_arrow(s9, 6.2, 2.5, 0.5, 0.35)

    add_node(s9, 6.8, 1.8, 2.4, 1.75, "Nearby Nodes", "Overlays Emergency Alert\nOn Nearby Phones", COLOR_WHITE)
    add_arrow(s9, 9.3, 2.5, 0.5, 0.35)

    add_node(s9, 9.9, 1.8, 2.4, 1.75, "Rescue Beacon", "Acoustic Audio Siren\nMorse Camera Strobe", COLOR_GREEN)

    add_card(s9, 0.5, 4.1, 5.9, 2.9, "Acoustic Audio Siren", [
        "Piercing Tone: 2.5kHz - 4kHz acoustic tone for rescue pinpointing.",
        "Override Silent Mode: Sounds via STREAM_ALARM channel even when muted."
    ], font_size=16)

    add_card(s9, 6.9, 4.1, 5.9, 2.9, "Morse Code Strobe", [
        "Camera Torch Strobe: Pulses hardware LED flash in SOS pattern.",
        "GPS Payload: Attaches last-known GPS location to SOS packet."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=16)

    # =========================================================================
    # SLIDE 10: Air-Gapped Web Server & APK Sharing
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "10. Air-Gapped Local Web Server & APK Sharing", "DISTRIBUTION")

    h_shadow = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.58), Inches(1.53), Inches(12.2), Inches(2.45))
    h_shadow.fill.solid()
    h_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    h_shadow.line.fill.background()

    h_box = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.45), Inches(12.2), Inches(2.45))
    h_box.fill.solid()
    h_box.fill.fore_color.rgb = COLOR_CARD_BG
    h_box.line.color.rgb = COLOR_GREEN
    h_box.line.width = Pt(2.5)

    add_node(s10, 0.8, 1.8, 2.2, 1.75, "Host Device", "NanoHTTPD Web Server\nPort 8080 Active", COLOR_GREEN)
    add_arrow(s10, 3.1, 2.5, 0.5, 0.35)

    add_node(s10, 3.7, 1.8, 2.4, 1.75, "Wi-Fi Hotspot", "Zero Internet Needed\nIP: 192.168.49.1", COLOR_WHITE)
    add_arrow(s10, 6.2, 2.5, 0.5, 0.35)

    add_node(s10, 6.8, 1.8, 2.4, 1.75, "Peer Browser", "Opens Mobile Browser\n192.168.49.1:8080", COLOR_WHITE)
    add_arrow(s10, 9.3, 2.5, 0.5, 0.35)

    add_node(s10, 9.9, 1.8, 2.4, 1.75, "1-Click Download", "Direct APK Install\nZero Play Store", COLOR_GREEN)

    add_card(s10, 0.5, 4.1, 5.9, 2.9, "Off-Grid Distribution", [
        "Play Store Independent: Distributes APK package in field without internet.",
        "Lightweight Web Server: NanoHTTPD footprint under 100KB inside APK."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=16)

    add_card(s10, 6.9, 4.1, 5.9, 2.9, "QR Code Hotspot Join", [
        "Instant Wi-Fi Join: Screen renders QR code containing hotspot credentials.",
        "Field Deployment Ready: Equips surrounding crowd within 60 seconds."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=16)

    # =========================================================================
    # SLIDE 11: Field Benchmarks
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "11. Real-World Field Performance Benchmarks", "BENCHMARKS")

    add_stat_box(s11, 0.5, 1.45, 2.8, 2.5, "99.4%", "Message Delivery Rate\n(3-Hop Mesh Environment)", COLOR_GREEN)
    add_stat_box(s11, 3.6, 1.45, 2.8, 2.5, "< 50 ms", "Direct Voice UDP Latency\n(Real-Time Sub-100ms)", COLOR_WHITE)
    add_stat_box(s11, 6.7, 1.45, 2.8, 2.5, "150 m", "Max Direct Hop Range\n(Wi-Fi Direct Line-of-Sight)", COLOR_GREEN)
    add_stat_box(s11, 9.8, 1.45, 3.0, 2.5, "0.0 KB", "External Cloud Data\n(100% Off-Grid Sovereign)", COLOR_WHITE)

    add_card(s11, 0.5, 4.15, 5.9, 2.85, "Physical Test Environments", [
        "Underground Basement Test: Verified voice & text relay through concrete slabs.",
        "Urban Obstacle Test: Tested 3-hop message routing across masonry walls."
    ], font_size=16)

    add_card(s11, 6.9, 4.15, 5.9, 2.85, "Battery & Memory Efficiency", [
        "OLED Dark UI Theme: Saves up to 35% battery consumption during continuous use.",
        "Low RAM Footprint: Operates comfortably on budget devices with 2GB RAM."
    ], border_color=COLOR_GREEN, title_color=COLOR_GREEN, font_size=16)

    # =========================================================================
    # SLIDE 12: Phase 4 Roadmap & Conclusion
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "12. Phase 4 Roadmap & Project Conclusion", "CONCLUSION")

    add_card(s12, 0.5, 1.45, 5.9, 5.5, "Phase 4 Development Roadmap", [
        "1. AI Smart Mesh Routing: Machine learning predicts link quality & node battery.",
        "2. Hardware LoRa Bridge: 868MHz/915MHz LoRa radios for 10km+ long range hops.",
        "3. RuVNet 3D Point-Cloud: Upgrading wave sensing to render full spatial point-cloud.",
        "4. Multi-Platform Support: Expanding mesh client protocol to iOS and Linux terminals."
    ], border_color=COLOR_SILVER_BORDER, title_color=COLOR_WHITE, font_size=17.5)

    c_shadow = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.98), Inches(1.53), Inches(5.9), Inches(5.42))
    c_shadow.fill.solid()
    c_shadow.fill.fore_color.rgb = COLOR_CARD_SHADOW
    c_shadow.line.fill.background()

    conc_card = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.45), Inches(5.9), Inches(5.42))
    conc_card.fill.solid()
    conc_card.fill.fore_color.rgb = COLOR_CARD_BG
    conc_card.line.color.rgb = COLOR_GREEN
    conc_card.line.width = Pt(3.0)

    ctf2 = conc_card.text_frame
    ctf2.word_wrap = True
    ctf2.margin_left = Inches(0.35)
    ctf2.margin_top = Inches(0.35)

    cp = ctf2.paragraphs[0]
    cp.text = "PROJECT CONCLUSION"
    cp.font.size = Pt(22)
    cp.font.bold = True
    cp.font.color.rgb = COLOR_GREEN
    cp.space_after = Pt(12)

    cp1 = ctf2.add_paragraph()
    cp1.text = "Nexus MeshLink proves that high-performance, decentralized, and serverless communication is fully achievable using existing consumer mobile hardware."
    cp1.font.size = Pt(17)
    cp1.font.bold = True
    cp1.font.color.rgb = COLOR_WHITE
    cp1.space_after = Pt(16)

    cp2 = ctf2.add_paragraph()
    cp2.text = "By unifying P2P mesh relay, real-time voice/720p video streaming, RuVNet wave sensing, and RSA/AES security, Nexus MeshLink offers an indispensable lifeline."
    cp2.font.size = Pt(17)
    cp2.font.bold = True
    cp2.font.color.rgb = COLOR_WHITE
    cp2.space_after = Pt(22)

    cp3 = ctf2.add_paragraph()
    cp3.text = "Thank You! Questions & Discussion"
    cp3.alignment = PP_ALIGN.CENTER
    cp3.font.size = Pt(19)
    cp3.font.bold = True
    cp3.font.color.rgb = COLOR_GREEN
    cp3.space_after = Pt(6)

    cp4 = ctf2.add_paragraph()
    cp4.text = "Presenter: Shaikh Abdul Zubair Abdul Kabir | SRK Institute"
    cp4.alignment = PP_ALIGN.CENTER
    cp4.font.size = Pt(14)
    cp4.font.bold = True
    cp4.font.color.rgb = COLOR_GRAY_MUTED

    output_path = r"c:\Users\abdul\AndroidStudioProjects\NearMeshChat\Nexus_Phase2_Phase3_Final_Presentation.pptx"
    prs.save(output_path)
    print(f"Final presentation without logo and 100% bold text saved to {output_path}")

if __name__ == "__main__":
    build_no_logo_nexus_deck()
