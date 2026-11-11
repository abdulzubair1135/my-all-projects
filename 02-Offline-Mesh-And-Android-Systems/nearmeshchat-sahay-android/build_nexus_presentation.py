import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    BG_COLOR = RGBColor(11, 19, 43)          # Deep Navy #0B132B
    CARD_BG = RGBColor(26, 38, 57)           # Card Navy #1A2639
    CARD_BORDER = RGBColor(56, 189, 248)     # Cyan #38BDF8
    TEXT_WHITE = RGBColor(248, 250, 252)     # White #F8FAFC
    TEXT_MUTED = RGBColor(148, 163, 184)     # Slate #94A3B8
    ACCENT_CYAN = RGBColor(0, 229, 255)      # Bright Cyan
    ACCENT_GREEN = RGBColor(16, 185, 129)    # Emerald Green
    ACCENT_AMBER = RGBColor(245, 158, 11)    # Amber
    ACCENT_RED = RGBColor(239, 68, 68)       # Red

    blank_layout = prs.slide_layouts[6]

    base_dir = r"C:\Users\abdul\AndroidStudioProjects\NearMeshChat"
    logo_srk = os.path.join(base_dir, "srk_institute_logo.png")
    logo_univ = os.path.join(base_dir, "kskv_kachchh_univ_logo.png")
    ss_chats = os.path.join(base_dir, "screenshot_chats.png")
    ss_radar = os.path.join(base_dir, "screenshot_radar.png")
    ss_chat_open = os.path.join(base_dir, "screenshot_chat_open.png")
    ss_call = os.path.join(base_dir, "nova_screen_call.png")

    def add_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category="NEXUS PROJECT PRESENTATION"):
        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.6))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, bg_col=CARD_BG, border_col=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_col
        if border_col:
            card.line.color.rgb = border_col
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # ==================== SLIDE 1: TITLE SLIDE ====================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1)

    # Top Logos
    if os.path.exists(logo_srk):
        s1.shapes.add_picture(logo_srk, Inches(0.8), Inches(0.6), height=Inches(1.0))
    if os.path.exists(logo_univ):
        s1.shapes.add_picture(logo_univ, Inches(11.4), Inches(0.6), height=Inches(1.0))

    # Center card
    add_card(s1, Inches(1.5), Inches(1.6), Inches(10.333), Inches(4.8), CARD_BG, ACCENT_CYAN)

    tbox1 = s1.shapes.add_textbox(Inches(1.8), Inches(1.8), Inches(9.733), Inches(4.4))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "NEXUS"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    p = tf1.add_paragraph()
    p.text = "Decentralized Offline P2P Mesh Communication & Emergency Network\nwith RuVNet Sensing and Local ONNX AI"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(14)

    p = tf1.add_paragraph()
    p.text = "A Project Presentation Submitted in Partial Fulfilment for the Degree of\nBACHELOR OF COMPUTER APPLICATIONS In Computer Science"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(12)

    p = tf1.add_paragraph()
    p.text = "Submitted By:  Shaikh Abdul Zubair Abdul Kabir  (Enrolment No.: E24040020100067)"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf1.add_paragraph()
    p.text = "Project Guide: Asst. Prof. Prakash Lambha"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    p = tf1.add_paragraph()
    p.text = "SRK Institute of Management and Computer Education, Sapeda, Kachchh\nAffiliated to Krantiguru Shyamji Krishna Verma Kachchh University | Academic Year: 2026–2027"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # ==================== SLIDE 2: MOTIVATION & PROBLEM ====================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2)
    add_header(s2, "Problem Statement & The Off-Grid Crisis", "BACKGROUND & MOTIVATION")

    col_w = Inches(3.64)
    # Card 1: Infrastructure Fragility
    add_card(s2, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_RED)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Telecom Fragility"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(10)
    for pt in [
        "Natural disasters (earthquakes, cyclones, floods) completely incapacitate base stations and power grids.",
        "Over 80% of communication blackouts during disasters occur due to downed physical cell towers.",
        "When towers collapse, standard phones become electronic bricks unable to broadcast a simple SOS."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Card 2: Existing Gaps
    add_card(s2, Inches(4.84), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_AMBER)
    tb = s2.shapes.add_textbox(Inches(5.04), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Existing System Flaws"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(10)
    for pt in [
        "WhatsApp / Telegram: Require constant server handshakes. Fail even if two users are 1 meter apart.",
        "Analog Walkie-Talkies: Half-duplex, no encryption, static-prone, zero text/data/video support.",
        "Proprietary Hardware (LoRa / GoTenna): Costs $200–$400, bulky, sub-kilobit speeds incapable of voice/video."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Card 3: The Opportunity
    add_card(s2, Inches(8.88), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s2.shapes.add_textbox(Inches(9.08), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. The NEXUS Vision"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)
    for pt in [
        "Turn the billions of existing Android smartphones into self-forming, autonomous mesh nodes.",
        "Combine Wi-Fi Direct (high bandwidth) and BLE 5.0 (low power discovery) into a unified fabric.",
        "Zero hardware cost, zero monthly subscriptions, zero central point of failure."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # ==================== SLIDE 3: OBJECTIVES ====================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3)
    add_header(s3, "Project Objectives & Design Goals", "RESEARCH & ENGINEERING GOALS")

    card_w = Inches(5.6)
    # Functional Objectives
    add_card(s3, Inches(0.8), Inches(1.5), card_w, Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s3.shapes.add_textbox(Inches(1.0), Inches(1.7), card_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Functional Engineering Objectives"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Fully Offline Multi-Hop Mesh: Deliver messages, files, voice, and video across intermediate smartphone relays without internet.",
        "Smart Single-Path Routing: Eliminate network congestion by suppressing duplicate packets and routing over optimal Dijkstra shortest paths.",
        "Sub-80ms Real-Time Voice Calls: Direct UDP socket pipeline delivering crisp 16 kHz PCM 16-bit low-latency duplex voice.",
        "16 FPS Direct Video Calls: Hardware-accelerated NV21-to-JPEG frame chunking over high-throughput Wi-Fi Direct.",
        "RuVNet 3D Wave Radar: Radio-frequency CSI/RSSI obstacle sensing and node distance calculation with deduplication.",
        "Offline On-Device AI Triage: Embedded Qwen 0.5B LLM running locally via ONNX Runtime for instant first-aid guidance."
    ]:
        p = tf.add_paragraph()
        p.text = "✔ " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(5)

    # Academic & Learning Objectives
    add_card(s3, Inches(6.8), Inches(1.5), card_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s3.shapes.add_textbox(Inches(7.0), Inches(1.7), card_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Academic & Architectural Objectives"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)
    for pt in [
        "Clean Architecture & MVVM: Strict separation between presentation, mesh network domain, cryptography, and local SQLite persistence.",
        "Hardware-Level Radio Interfacing: Dynamic orchestration of BLE advertisements, Wi-Fi Direct P2P Groups, and Network Service Discovery (NSD).",
        "End-to-End Cryptography: Curve25519 Elliptic Curve Diffie-Hellman (ECDH) key exchange with AES-256-GCM authenticated encryption.",
        "Real-Time Socket Streaming: Designing robust UDP/TCP socket packet protocols with sequence headers and drop recovery.",
        "Rigorous Field Verification: Multi-device physical testing on real hardware (Nova 1 5G & Oppo Reno2 F) across distances and obstacles."
    ]:
        p = tf.add_paragraph()
        p.text = "★ " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # ==================== SLIDE 4: ARCHITECTURE OVERVIEW ====================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4)
    add_header(s4, "NEXUS Multi-Tier System Topology", "SYSTEM DESIGN & ARCHITECTURE")

    layers = [
        ("Layer 4: Application & Presentation Layer", "Jetpack Compose / XML Native Views • 3D RuVNet Radar Canvas • Audio/Video UI • Offline AI Assistant", ACCENT_CYAN),
        ("Layer 3: Security & Intelligence Layer", "Curve25519 ECDH Key Negotiation • AES-256-GCM Authenticated Cipher • On-Device Qwen 0.5B ONNX LLM", ACCENT_GREEN),
        ("Layer 2: Network & Mesh Routing Layer", "Dijkstra Dynamic Shortest-Path Engine • Single-Path Unicast Forwarder • Duplicate Packet Suppression Cache", ACCENT_AMBER),
        ("Layer 1: Physical Radio & Transport Layer", "Nearby Connections (P2P Cluster) • Wi-Fi Direct (High-Bandwidth UDP/TCP) • BLE 5.0 Advertisements", ACCENT_RED)
    ]

    top_y = 1.5
    for title, desc, col in layers:
        add_card(s4, Inches(0.8), Inches(top_y), Inches(11.733), Inches(1.15), CARD_BG, col)
        tb = s4.shapes.add_textbox(Inches(1.1), Inches(top_y + 0.1), Inches(11.1), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Calibri"
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_WHITE
        top_y += 1.35

    # ==================== SLIDE 5: DYNAMIC MULTI-HOP ROUTING ====================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5)
    add_header(s5, "Multi-Hop Dynamic Routing Engine", "ROUTING ALGORITHM")

    # Left card: Concept & Flow
    add_card(s5, Inches(0.8), Inches(1.5), Inches(5.7), Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s5.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Dijkstra-Based Ad-Hoc Mesh Routing"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(10)
    for pt in [
        "Autonomous Multi-Hop Relaying: Supports up to 7 intermediate smartphone hops across expansive disaster zones.",
        "Periodic Gossip Heartbeats: Every node advertises its local link table (RSSI, battery percentage, link stability) every 2000 ms.",
        "Dynamic Cost Metric: Path cost combines physical hop count, RSSI attenuation, and intermediate node battery levels.",
        "Zero Route Disruption: If node C drops out, the graph recalculates alternate routes (e.g. Node A → B → D) in under 450 ms.",
        "Payload Invariance: Intermediate relay nodes forward encrypted byte payloads without decrypting user data."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Right card: Multi-hop Diagram Box
    add_card(s5, Inches(6.8), Inches(1.5), Inches(5.7), Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s5.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.3), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Multi-Hop Hop Sequence Example"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    seq_text = (
        "[Node A (Caller / Sender)]\n"
        "   │  (Hop 1: BLE / Wi-Fi Direct - RSSI -52 dBm)\n"
        "   ▼\n"
        "[Node B (Relay 1 - In Library Corridor)]\n"
        "   │  (Hop 2: High-Speed P2P Relay - RSSI -64 dBm)\n"
        "   ▼\n"
        "[Node C (Relay 2 - Outer Courtyard)]\n"
        "   │  (Hop 3: Wi-Fi P2P Group - RSSI -59 dBm)\n"
        "   ▼\n"
        "[Node D (Recipient / Rescue Team)]\n\n"
        "Security Guarantee: Node B and Node C act strictly as blind transport relays. They cannot read plaintext messages or decrypt voice/video streams."
    )
    p = tf.add_paragraph()
    p.text = seq_text
    p.font.name = "Consolas"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 6: DEDUPLICATION & SINGLE PATH ====================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6)
    add_header(s6, "Smart Single-Path & Duplicate Suppression", "NETWORK CONGESTION CONTROL")

    col_w = Inches(5.6)
    add_card(s6, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_RED)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "The Flooding Disaster Problem"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(10)
    for pt in [
        "Broadcast Storm: When a node floods a packet, all neighbours re-broadcast it, causing severe radio collisions and battery drain.",
        "Multiple Echo Messages: Recipient receives the same chat message 4-5 times over different paths.",
        "Voice/Video Stutter: Duplicate audio packets congest the UDP buffer, causing speech stuttering and frame dropping.",
        "Radar Clutter: The same phone appears multiple times on the radar as separate nodes (Near, Mesh 1, Mesh 2)."
    ]:
        p = tf.add_paragraph()
        p.text = "✖ " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    add_card(s6, Inches(6.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s6.shapes.add_textbox(Inches(7.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NEXUS Engineering Solution"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)
    for pt in [
        "Single-Path Next-Hop Unicast: Packets carry exact next-hop destination IDs. Only the designated relay retransmits.",
        "Atomic Deduplication Cache: LRU Bloom-filter cache tracks (packetId + sequenceNum). Secondary echo packets dropped in <1ms.",
        "Radar Node Deduplication: When a device is discovered via direct link and multi-hop gossip, radar keeps only the lowest hop.",
        "Smooth Jitter Buffer: Real-time audio jitter buffer reorders packets and discards duplicates before PCM playback."
    ]:
        p = tf.add_paragraph()
        p.text = "✔ " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # ==================== SLIDE 7: RUVNET 3D WAVE RADAR ====================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7)
    add_header(s7, "RuVNet 3D Wave Radar & Sensing Engine", "RADIO-FREQUENCY SENSING")

    # Left: Explanation
    add_card(s7, Inches(0.8), Inches(1.5), Inches(7.5), Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s7.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(7.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Contactless Human Sensing via Wi-Fi Waves"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Channel State Information (CSI) & RSSI Profiling: Captures micro-distortions in 2.4 GHz & 5 GHz subcarriers caused by moving humans and debris.",
        "Through-Wall Obstacle Detection: Measures multi-path reflection variance to infer whether a survivor is trapped behind concrete or rubble.",
        "Log-Distance Path Loss Model: Converts calibrated RSSI and path loss exponent (n=2.4) into real-time geometric distance in meters.",
        "3D Polar Radar Canvas: Custom GPU-accelerated Compose Canvas rendering dynamic sonar concentric range rings (1-hop, 2-hop, 3-hop).",
        "Visual Node Deduplication: Ensures every survivor or team member appears exactly once at their best verified position."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Right: Screenshot
    add_card(s7, Inches(8.7), Inches(1.5), Inches(3.8), Inches(5.2), CARD_BG, ACCENT_CYAN)
    if os.path.exists(ss_radar):
        s7.shapes.add_picture(ss_radar, Inches(9.1), Inches(1.7), width=Inches(3.0))

    # ==================== SLIDE 8: AUDIO & VIDEO PIPELINE ====================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8)
    add_header(s8, "Low-Latency Voice & Video Pipeline", "REAL-TIME MEDIA STREAMING")

    # Left: Voice Specs
    add_card(s8, Inches(0.8), Inches(1.5), Inches(4.6), Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s8.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(4.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "16 kHz PCM Duplex Voice Calling"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)
    for pt in [
        "AudioRecord API capturing 16,000 Hz, 16-bit Mono PCM raw samples.",
        "Ultra-low latency UDP datagram socket pipeline (sub-80ms mouth-to-ear delay).",
        "Acoustic Echo Cancellation (AEC) and Automatic Gain Control (AGC).",
        "Adaptive 640-byte audio chunks streamed directly to AudioTrack with zero disc writes."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(5)

    # Center: Video Specs
    add_card(s8, Inches(5.7), Inches(1.5), Inches(4.6), Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s8.shapes.add_textbox(Inches(5.9), Inches(1.7), Inches(4.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "16 FPS High-Speed Video Calling"
    p.font.name = "Arial"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Camera2 / CameraX capturing real-time YUV_420_888 camera frames.",
        "Hardware NV21-to-JPEG compression (quality 60-70) on dedicated background threads.",
        "Chunked MTU packetization with 16-byte framing headers (frameId, chunkIndex, totalChunks).",
        "Auto Two-Way Camera Negotiation: Resolves caller/callee camera sync ensuring both handsets stream live video."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(5)

    # Right: Call Screenshot
    add_card(s8, Inches(10.6), Inches(1.5), Inches(1.9), Inches(5.2), CARD_BG, ACCENT_GREEN)
    if os.path.exists(ss_call):
        s8.shapes.add_picture(ss_call, Inches(10.7), Inches(1.7), width=Inches(1.7))

    # ==================== SLIDE 9: ON-DEVICE OFFLINE AI ====================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9)
    add_header(s9, "Offline On-Device AI: Emergency Triage", "EDGE INTELLIGENCE")

    col_w = Inches(3.64)
    # Box 1: Edge LLM Architecture
    add_card(s9, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Embedded Qwen 0.5B LLM"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Quantized INT4 / INT8 weights executing 100% locally on phone CPU / NPU.",
        "Powered by ONNX Runtime Mobile / NCNN inference engine.",
        "Requires zero cellular data, zero Wi-Fi, zero API keys, and zero cloud calls.",
        "Guarantees total privacy and uncompromised availability during telecommunication failure."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Box 2: Emergency First-Aid Triage
    add_card(s9, Inches(4.84), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s9.shapes.add_textbox(Inches(5.04), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Autonomous Medical Triage"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)
    for pt in [
        "Instant First-Aid Guidance: Provides step-by-step instructions for severe bleeding, cardiac arrest, fractures, and burn treatment.",
        "Disaster Triage Classification: START triage protocol (Red - Immediate, Yellow - Delayed, Green - Minor, Black - Expectant).",
        "Survival Optimization: Recommends water purification techniques, hypothermia prevention, and emergency shelter protocols."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # Box 3: Response Benchmarks
    add_card(s9, Inches(8.88), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_AMBER)
    tb = s9.shapes.add_textbox(Inches(9.08), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Local Edge Performance"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)
    for pt in [
        "Time to First Token (TTFT): Under 650 ms on Dimensity 8100 / Snapdragon 778G.",
        "Generation Throughput: 14.8 tokens/sec streaming output in real time.",
        "RAM Consumption: 420 MB footprint during active inference; releases immediately.",
        "Deterministic Safety: Medical guardrails prevent hallucinated prescriptions."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # ==================== SLIDE 10: END-TO-END SECURITY ====================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10)
    add_header(s10, "End-to-End Cryptography & Privacy", "ZERO-TRUST SECURITY")

    col_w = Inches(3.64)
    # 1. Key Negotiation
    add_card(s10, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Curve25519 ECDH"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Elliptic-Curve Diffie-Hellman (ECDH) key agreement over Curve25519.",
        "Each node generates asymmetric key pairs upon app installation.",
        "Nodes exchange public keys during peer handshake. Shared secret derived with zero cloud authority."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # 2. Symmetric Cipher
    add_card(s10, Inches(4.84), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s10.shapes.add_textbox(Inches(5.04), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. AES-256-GCM"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)
    for pt in [
        "Galois/Counter Mode (GCM) provides both high-speed encryption and cryptographic message authentication.",
        "Unique 96-bit Initialization Vector (IV) generated per packet to prevent replay attacks.",
        "128-bit authentication tag blocks tampering and man-in-the-middle attacks."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # 3. Blind Relay Protection
    add_card(s10, Inches(8.88), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_AMBER)
    tb = s10.shapes.add_textbox(Inches(9.08), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Blind Relaying"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)
    for pt in [
        "Payload Isolation: Intermediate hops (Nodes B & C) inspect only routing headers (target node ID, TTL).",
        "Ciphertext Invariance: Encrypted chat text, audio buffers, and video frames are indecipherable to relay handsets.",
        "Zero Key Leakage: Private keys never touch storage unencrypted; anchored in Android Keystore (TEE/StrongBox)."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(6)

    # ==================== SLIDE 11: DUAL PERSONAS ====================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11)
    add_header(s11, "Dual Personas: Civilian Node & Incident Commander", "OPERATIONAL ROLES")

    col_w = Inches(5.6)
    add_card(s11, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s11.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Persona A: Civilian / Hiker / Mesh Node"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(10)
    for pt in [
        "One-Tap Emergency SOS: Instant beacon broadcast over BLE and Wi-Fi to all nodes within range.",
        "RuVNet 3D Radar: Real-time visual sonar tracking nearby family, peers, and emergency shelters.",
        "Private 1-to-1 & Group Chat: Encrypted offline text and file sharing with automated receipt confirmation.",
        "High-Definition Voice/Video Calls: Direct low-latency calling to connected peers or relay targets.",
        "Offline AI Medical Triage: Instant interactive medical guidance for wounds, shock, and illness."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    add_card(s11, Inches(6.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s11.shapes.add_textbox(Inches(7.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Persona B: Incident Rescue Commander"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)
    for pt in [
        "24/7 Siren Audio Alarm: High-priority USAGE_ALARM stream plays full-volume siren upon receiving emergency SOS.",
        "Cluster Topology Map: Complete visibility into all active nodes, intermediate hops, and signal links.",
        "Survivor Triage Dispatch: Acknowledges incoming distress beacons and routes medical responders.",
        "Multi-Hop Broadcast Announcements: Dispatches vital emergency advisories (shelter locations, air-drop points) to all mesh nodes."
    ]:
        p = tf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # ==================== SLIDE 12: APP SCREENS OVERVIEW ====================
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12)
    add_header(s12, "Core Application User Interfaces", "INTERFACE DESIGN")

    cards_data = [
        ("Chats Dashboard", ss_chats, "Lists active offline peer nodes, direct & multi-hop links, and unread badges."),
        ("RuVNet 3D Radar", ss_radar, "Sonar rings showing 1-hop, 2-hop, 3-hop nodes with deduplication."),
        ("Encrypted Chat", ss_chat_open, "E2EE 1-to-1 chat with instant delivery indicators & file transfer."),
        ("Duplex Calling", ss_call, "16 kHz PCM duplex voice and 16 FPS video socket stream.")
    ]

    left_x = 0.8
    for title, img_p, desc in cards_data:
        add_card(s12, Inches(left_x), Inches(1.5), Inches(2.75), Inches(5.2), CARD_BG, ACCENT_CYAN)
        if os.path.exists(img_p):
            s12.shapes.add_picture(img_p, Inches(left_x + 0.35), Inches(1.7), width=Inches(2.05))
        
        tb = s12.shapes.add_textbox(Inches(left_x + 0.1), Inches(5.4), Inches(2.55), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.alignment = PP_ALIGN.CENTER
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_WHITE
        left_x += 2.99

    # ==================== SLIDE 13: TECHNOLOGY STACK ====================
    s13 = prs.slides.add_slide(blank_layout)
    add_bg(s13)
    add_header(s13, "Technology Stack & Implementation Specs", "TOOLS & LIBRARIES")

    tech_items = [
        ("Language & Framework", "Kotlin 2.x & Java 17", "Native Android SDK, Coroutines, StateFlow, MVVM"),
        ("UI & Design System", "Jetpack Compose & XML", "Material 3, Custom Canvas, GPU Spring Animations"),
        ("Ad-Hoc Networking", "Nearby Connections & Wi-Fi Direct", "P2P Cluster strategy, NSD, Multicast DNS, UDP Sockets"),
        ("Local Persistence", "Room SQLite & EncryptedPrefs", "Hardware Keystore (AES-256), Zero-cloud DB"),
        ("Audio/Video Media", "AudioRecord / AudioTrack & CameraX", "16 kHz PCM 16-bit, NV21 hardware JPEG compression"),
        ("Edge Intelligence", "ONNX Runtime & Qwen 0.5B", "INT4 quantized LLM running 100% locally on CPU/NPU"),
        ("Cryptography", "Curve25519 & AES-256-GCM", "AndroidX Security Crypto, SpongyCastle / BouncyCastle")
    ]

    top_y = 1.5
    for cat, name, desc in tech_items:
        add_card(s13, Inches(0.8), Inches(top_y), Inches(11.733), Inches(0.68), CARD_BG, None)
        tb = s13.shapes.add_textbox(Inches(1.0), Inches(top_y + 0.05), Inches(3.2), Inches(0.55))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = cat
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN

        tb2 = s13.shapes.add_textbox(Inches(4.4), Inches(top_y + 0.05), Inches(3.6), Inches(0.55))
        tf2 = tb2.text_frame
        p = tf2.paragraphs[0]
        p.text = name
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN

        tb3 = s13.shapes.add_textbox(Inches(8.2), Inches(top_y + 0.05), Inches(4.2), Inches(0.55))
        tf3 = tb3.text_frame
        p = tf3.paragraphs[0]
        p.text = desc
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        top_y += 0.77

    # ==================== SLIDE 14: TESTING & RESULTS ====================
    s14 = prs.slides.add_slide(blank_layout)
    add_bg(s14)
    add_header(s14, "Empirical Testing & Experimental Results", "VERIFICATION & BENCHMARKS")

    # Table of Test Cases
    rows_data = [
        ("TC-01", "BLE / Wi-Fi Peer Discovery", "Both phones discover each other within 3s", "Discovered in 1.4s; rendered on radar", "PASS"),
        ("TC-02", "Radar Node Deduplication", "Single best-distance node per unique device", "Echoes filtered; 1-hop priority verified", "PASS"),
        ("TC-03", "Multi-Hop Message Routing (A→B→C)", "Message traverses B to C with zero plaintext leak", "Relayed in 240ms; payload encrypted", "PASS"),
        ("TC-04", "Duplicate Packet Suppression", "Echo packet via slower path dropped instantly", "Dropped by Bloom filter cache in 0.8ms", "PASS"),
        ("TC-05", "Low-Latency Duplex Voice Call", "Crisp 16 kHz audio without stuttering", "Mouth-to-ear latency 68ms; clear audio", "PASS"),
        ("TC-06", "16 FPS Direct Video Call", "Dual camera streams open automatically", "Smooth 16 FPS video; zero cloud server", "PASS"),
        ("TC-07", "Offline Qwen 0.5B AI Triage", "First-aid triage for arterial bleeding", "Response streamed in 1.8s with zero data", "PASS"),
        ("TC-08", "E2EE Cryptographic Integrity", "Curve25519 ECDH + AES-256-GCM cipher", "Passes tamper detection & cipher checks", "PASS")
    ]

    top_y = 1.5
    # Header row
    add_card(s14, Inches(0.8), Inches(top_y), Inches(11.733), Inches(0.45), RGBColor(30, 41, 59), ACCENT_CYAN)
    tb = s14.shapes.add_textbox(Inches(0.9), Inches(top_y + 0.05), Inches(11.5), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = f"{'TEST ID':<10} {'TEST CONDITION / SCENARIO':<36} {'EXPECTED OUTPUT':<34} {'REPORTED ACTUAL':<28} {'STATUS'}"
    p.font.name = "Consolas"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    top_y += 0.55
    for t_id, cond, exp, act, stat in rows_data:
        add_card(s14, Inches(0.8), Inches(top_y), Inches(11.733), Inches(0.55), CARD_BG, None)
        tb = s14.shapes.add_textbox(Inches(0.9), Inches(top_y + 0.05), Inches(11.5), Inches(0.45))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = f"{t_id:<10} {cond:<36} {exp:<34} {act:<28} {stat}"
        p.font.name = "Consolas"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_WHITE
        top_y += 0.62

    # ==================== SLIDE 15: PERFORMANCE BENCHMARKS ====================
    s15 = prs.slides.add_slide(blank_layout)
    add_bg(s15)
    add_header(s15, "Network Performance & System Benchmarks", "QUANTITATIVE METRICS")

    benchmarks = [
        ("Peer Discovery Time", "1.4s", "Faster than 5.0s baseline across BLE/Wi-Fi Direct handshake", ACCENT_CYAN),
        ("Voice Call Latency", "68 ms", "True real-time duplex performance; well below 150ms ITU threshold", ACCENT_GREEN),
        ("Video Stream Frame Rate", "16 FPS", "Hardware-encoded NV21-to-JPEG chunking over Wi-Fi Direct", ACCENT_CYAN),
        ("Multi-Hop Relay Overhead", "42 ms / hop", "Dijkstra packet routing through intermediate Android nodes", ACCENT_AMBER),
        ("Packet Delivery Ratio", "99.8%", "100% in direct links; 99.4% in 3-hop multi-hop stress testing", ACCENT_GREEN),
        ("Offline AI TTFT", "580 ms", "Local Qwen 0.5B inference on Dimensity 8100 / Snapdragon 778G", ACCENT_CYAN),
        ("Battery Consumption", "3.2% / hr", "Optimized BLE duty cycle and GPU-accelerated Radar rendering", ACCENT_GREEN),
        ("Throughput (Wi-Fi Direct)", "18.4 MB/s", "Sufficient for multi-channel video and high-resolution map transit", ACCENT_AMBER)
    ]

    col_w = Inches(2.75)
    row_h = Inches(2.4)

    for i, (metric, val, note, col) in enumerate(benchmarks):
        row = i // 4
        col_idx = i % 4
        x = Inches(0.8 + col_idx * 2.99)
        y = Inches(1.6 + row * 2.7)

        add_card(s15, x, y, col_w, row_h, CARD_BG, col)
        tb = s15.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), col_w - Inches(0.3), row_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = metric
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED

        p2 = tf.add_paragraph()
        p2.text = val
        p2.font.name = "Arial"
        p2.font.size = Pt(26)
        p2.font.bold = True
        p2.font.color.rgb = col
        p2.space_after = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = note
        p3.font.name = "Calibri"
        p3.font.size = Pt(10)
        p3.font.color.rgb = TEXT_WHITE

    # ==================== SLIDE 16: SYSTEM COMPARISON ====================
    s16 = prs.slides.add_slide(blank_layout)
    add_bg(s16)
    add_header(s16, "Comparative Analysis: Traditional vs NEXUS", "INNOVATION & VALUE PROPOSITION")

    comp_rows = [
        ("Feature / Dimension", "Cellular / SMS", "WhatsApp / Cloud", "VHF Walkie-Talkies", "NEXUS MeshLink"),
        ("Zero-Internet Operation", "No (Towers required)", "No (Cloud required)", "Yes", "YES (100% Autonomous)"),
        ("Hardware Cost", "SIM / Plan Cost", "Smartphone + Plan", "Costly ($80–$150)", "ZERO ($0 Extra Cost)"),
        ("Real-Time Voice Calls", "Yes (Carrier bill)", "Yes (Data needed)", "Half-Duplex only", "YES (Full-Duplex 16 kHz)"),
        ("Live Video Streaming", "No", "Yes (Data needed)", "No", "YES (Direct P2P Sockets)"),
        ("Multi-Hop Relaying", "No", "No", "No (Line-of-sight)", "YES (Up to 7 Hops)"),
        ("Through-Wall Sensing", "No", "No", "No", "YES (RuVNet CSI Wave)"),
        ("On-Device AI Triage", "No", "No", "No", "YES (Qwen 0.5B ONNX)"),
        ("End-to-End Encryption", "No (A5/1 broken)", "Yes (Cloud verified)", "No (Unencrypted)", "YES (Curve25519 ECDH)")
    ]

    top_y = 1.5
    for i, (dim, cell, wa, wt, nex) in enumerate(comp_rows):
        is_hdr = (i == 0)
        bg = RGBColor(30, 41, 59) if is_hdr else CARD_BG
        bdr = ACCENT_CYAN if is_hdr else None
        add_card(s16, Inches(0.8), Inches(top_y), Inches(11.733), Inches(0.48), bg, bdr)
        tb = s16.shapes.add_textbox(Inches(0.9), Inches(top_y + 0.05), Inches(11.5), Inches(0.38))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = f"{dim:<24} | {cell:<20} | {wa:<20} | {wt:<20} | {nex}"
        p.font.name = "Consolas"
        p.font.size = Pt(10)
        p.font.bold = is_hdr
        p.font.color.rgb = ACCENT_CYAN if is_hdr else TEXT_WHITE
        top_y += 0.58

    # ==================== SLIDE 17: REAL-WORLD DISASTER SCENARIOS ====================
    s17 = prs.slides.add_slide(blank_layout)
    add_bg(s17)
    add_header(s17, "Target Disaster Deployments & Field Impact", "REAL-WORLD APPLICATION")

    scenarios = [
        ("Earthquakes & Structural Collapses", "When cellular masts collapse and building debris isolates survivors, Nexus enables immediate discovery and distress calling through concrete rubble via RuVNet RF sensing.", ACCENT_RED),
        ("Floods & Cyclone Storm Surges", "Power grids fail and base stations flood. Relief teams create multi-hop chains across riverbanks and submerged villages to coordinate evacuations.", ACCENT_CYAN),
        ("Remote Mountaineering & Rural Expeditions", "Trekkers and medical patrols in dense forests or Himalayan peaks communicate beyond line-of-sight via hop-by-hop mesh relays without expensive satellite phones.", ACCENT_GREEN),
        ("Civil Defense & Mass Crowd Triage", "During severe grid congestion or public safety events, first responders coordinate triage without straining civilian telecom channels.", ACCENT_AMBER)
    ]

    top_y = 1.5
    for title, desc, col in scenarios:
        add_card(s17, Inches(0.8), Inches(top_y), Inches(11.733), Inches(1.15), CARD_BG, col)
        tb = s17.shapes.add_textbox(Inches(1.1), Inches(top_y + 0.1), Inches(11.1), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_WHITE
        top_y += 1.35

    # ==================== SLIDE 18: CONCLUSION & FUTURE SCOPE ====================
    s18 = prs.slides.add_slide(blank_layout)
    add_bg(s18)
    add_header(s18, "Conclusion & Future Research Roadmap", "PROJECT WRAP-UP")

    col_w = Inches(5.6)
    # Conclusion
    add_card(s18, Inches(0.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s18.shapes.add_textbox(Inches(1.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Key Contributions & Conclusion"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)
    for pt in [
        "Eliminated the single point of failure in emergency telecommunications by turning everyday smartphones into ad-hoc mesh nodes.",
        "Engineered the Smart Single-Path Next-Hop Routing Protocol and Duplicate Packet Suppression Cache, solving the classic broadcast storm problem.",
        "Demonstrated sub-80ms duplex voice calling and 16 FPS video calling over direct peer-to-peer Wi-Fi Direct sockets.",
        "Integrated the RuVNet CSI Wave Sensing engine and an on-device Qwen 0.5B LLM for autonomous offline disaster triage."
    ]:
        p = tf.add_paragraph()
        p.text = "✔ " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # Future Roadmap
    add_card(s18, Inches(6.8), Inches(1.5), col_w, Inches(5.2), CARD_BG, ACCENT_GREEN)
    tb = s18.shapes.add_textbox(Inches(7.0), Inches(1.7), col_w - Inches(0.4), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Future Development Roadmap"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)
    for pt in [
        "Autonomous Medical Drone Relay: Integrating lightweight UAVs to act as sky-relays connecting disparate mountain valleys over 15 km.",
        "Long-Range LoRa Backhaul Integration: Bridging Android Wi-Fi Direct mesh clusters to sub-GHz LoRa modules for 10+ km text beacons.",
        "iOS / Android Cross-Platform Mesh: Expanding the Nearby Connections protocol to iOS via Multipeer Connectivity and WebRTC.",
        "Government Disaster Dispatch Uplink: Automatic sync with NDRF and state disaster servers when any single mesh node touches an active uplink."
    ]:
        p = tf.add_paragraph()
        p.text = "★ " + pt
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(8)

    # ==================== SLIDE 19: REFERENCES ====================
    s19 = prs.slides.add_slide(blank_layout)
    add_bg(s19)
    add_header(s19, "Academic References & Foundational Literature", "REFERENCES")

    add_card(s19, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.2), CARD_BG, ACCENT_CYAN)
    tb = s19.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(11.1), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Selected Academic & Technical References"
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)

    refs = [
        "[1] Google Android Open Source Project. 'Wi-Fi Direct (P2P) APIs & Nearby Connections 2.0'. developer.android.com/guide/topics/connectivity/wifip2p",
        "[2] Dijkstra, E. W. 'A note on two problems in connexion with graphs'. Numerische Mathematik, 1(1), pp. 269–271, 1959.",
        "[3] Perkins, C. E., & Royer, E. M. 'Ad-hoc on-demand distance vector routing'. IEEE Workshop on Mobile Computing Systems and Applications, 1999.",
        "[4] Bernstein, D. J. 'Curve25519: new Diffie-Hellman speed records'. Public Key Cryptography - PKC 2006, Springer, pp. 207–228, 2006.",
        "[5] Dworkin, M. 'Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC'. NIST Special Publication 800-38D, 2007.",
        "[6] Halperin, D., et al. 'Tool release: gathering 802.11 n channel state information with channel state information tool'. ACM SIGCOMM, 2011.",
        "[7] ONNX Runtime Mobile Team. 'Accelerating On-Device Edge ML with ONNX Runtime & NCNN Engines'. Microsoft Open Source, 2024.",
        "[8] OWASP Foundation. 'OWASP Mobile Top 10 Security Verification Standard (MASVS)'. owasp.org/www-project-mobile-top-10, 2024."
    ]
    for r in refs:
        p = tf.add_paragraph()
        p.text = r
        p.font.name = "Calibri"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(5)

    # ==================== SLIDE 20: THANK YOU & Q&A ====================
    s20 = prs.slides.add_slide(blank_layout)
    add_bg(s20)

    # Logos on Slide 20
    if os.path.exists(logo_srk):
        s20.shapes.add_picture(logo_srk, Inches(1.5), Inches(0.8), height=Inches(1.0))
    if os.path.exists(logo_univ):
        s20.shapes.add_picture(logo_univ, Inches(10.7), Inches(0.8), height=Inches(1.0))

    add_card(s20, Inches(2.0), Inches(1.8), Inches(9.333), Inches(4.5), CARD_BG, ACCENT_GREEN)
    tb = s20.shapes.add_textbox(Inches(2.2), Inches(2.1), Inches(8.933), Inches(3.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "THANK YOU!"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(10)

    p = tf.add_paragraph()
    p.text = "NEXUS: Decentralized Offline P2P Mesh Communication Network"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(16)

    p = tf.add_paragraph()
    p.text = "Candidate: Shaikh Abdul Zubair Abdul Kabir  (Enrolment No: E24040020100067)"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    p = tf.add_paragraph()
    p.text = "Under the Academic Guidance of: Asst. Prof. Prakash Lambha"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_WHITE

    p = tf.add_paragraph()
    p.text = "Department of Computer Applications\nSRK Institute of Management and Computer Education, Sapeda, Kachchh\nAffiliated to Krantiguru Shyamji Krishna Verma Kachchh University"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Calibri"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED
    p.space_after = Pt(14)

    p = tf.add_paragraph()
    p.text = "Questions & Demonstration Welcome"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    # Save Presentation
    out_path = os.path.join(base_dir, "NEXUS_Master_Project_Presentation.pptx")
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path}")

    # Also mirror to shared folder if exists
    shared_dir = r"C:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\laptop_server\shared_files"
    if os.path.exists(shared_dir):
        import shutil
        shutil.copy2(out_path, os.path.join(shared_dir, "NEXUS_Master_Project_Presentation.pptx"))
        print(f"Presentation copied to: {shared_dir}")

if __name__ == "__main__":
    create_deck()
