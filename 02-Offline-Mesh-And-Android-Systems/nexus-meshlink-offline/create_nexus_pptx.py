import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    COLOR_BG_DARK = RGBColor(15, 23, 42)      # #0F172A
    COLOR_CARD_BG = RGBColor(30, 41, 59)      # #1E293B
    COLOR_GREEN = RGBColor(22, 163, 74)       # #16A34A
    COLOR_TEAL = RGBColor(0, 200, 150)        # #00C896
    COLOR_TEXT_LIGHT = RGBColor(248, 250, 252)# #F8FAFC
    COLOR_TEXT_MUTED = RGBColor(148, 163, 184)# #94A3B8
    COLOR_CODE_BG = RGBColor(9, 13, 22)       # #090D16

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, badge_text="NEXUS MESHLINK"):
        # Header Box
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.8))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = COLOR_CARD_BG
        header_shape.line.color.rgb = COLOR_GREEN

        tf = header_shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_TEXT_LIGHT

        # Badge
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.8), Inches(0.65), Inches(2.5), Inches(0.5))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_GREEN
        badge.line.fill.background()
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = badge_text
        bp.alignment = PP_ALIGN.CENTER
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = COLOR_TEXT_LIGHT

    def add_card(slide, left, top, width, height, title, items, code_snippet=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = COLOR_GREEN

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.2)
        tf.margin_right = Inches(0.2)

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(16)
        p0.font.bold = True
        p0.font.color.rgb = COLOR_GREEN
        p0.space_after = Pt(10)

        for item in items:
            p = tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_TEXT_MUTED
            p.space_after = Pt(6)

        if code_snippet:
            p_code = tf.add_paragraph()
            p_code.text = code_snippet
            p_code.font.size = Pt(11)
            p_code.font.bold = True
            p_code.font.color.rgb = COLOR_TEAL

    # -------------------------------------------------------------
    # SLIDE 1: Cover Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_BG_DARK
    bg1.line.fill.background()

    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(1.5), Inches(9.333), Inches(4.5))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_CARD_BG
    card1.line.color.rgb = COLOR_GREEN

    tf1 = card1.text_frame
    tf1.word_wrap = True
    tf1.margin_top = Inches(0.5)

    p1 = tf1.paragraphs[0]
    p1.text = "📡 NEXUS MESHLINK"
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_TEXT_LIGHT
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "Off-Grid P2P Mesh Communication Suite (Phase 2 & Phase 3)"
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_GREEN
    p2.space_after = Pt(30)

    p3 = tf1.add_paragraph()
    p3.text = "Presenter: Shaikh Abdul Zubair Abdul Kabir"
    p3.alignment = PP_ALIGN.CENTER
    p3.font.size = Pt(16)
    p3.font.color.rgb = COLOR_TEXT_LIGHT

    p4 = tf1.add_paragraph()
    p4.text = "SRK Institute of Management and Computer Application"
    p4.alignment = PP_ALIGN.CENTER
    p4.font.size = Pt(14)
    p4.font.color.rgb = COLOR_TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 2: Problem Statement & Vision
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    bg2 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg2.fill.solid()
    bg2.fill.fore_color.rgb = COLOR_BG_DARK
    bg2.line.fill.background()

    add_header(slide2, "02. Problem Statement & Vision", "CORE MOTIVATION")
    add_card(slide2, 0.8, 1.6, 5.6, 5.2, "🚨 The Off-Grid Crisis", [
        "Cellular Network Outages: Disasters, tower crashes, and remote zones leave citizens stranded.",
        "Server Dependency: Standard apps (WhatsApp, Telegram) freeze without active internet infrastructure.",
        "Emergency Isolation: Standard phones cannot reach nearby devices 10 meters away without cell towers."
    ])
    add_card(slide2, 6.8, 1.6, 5.6, 5.2, "🌐 The Nexus Solution Architecture", [
        "Zero Internet & Zero SIM: Operates 100% locally over BLE 5.0 and Wi-Fi Direct P2P.",
        "Decentralized Mesh Relay: Every device acts as a repeating router, relaying encrypted packets.",
        "Full Communication Suite: Text messaging, E2EE security, voice calls, 720p video calls, and SOS sirens."
    ])

    # -------------------------------------------------------------
    # SLIDE 3: Phase 2: Mesh Messaging & Multi-Hop Protocol
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    bg3 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg3.fill.solid()
    bg3.fill.fore_color.rgb = COLOR_BG_DARK
    bg3.line.fill.background()

    add_header(slide3, "03. Phase 2: Mesh Messaging & Protocol", "PHASE 2 MILESTONE")
    add_card(slide3, 0.8, 1.6, 5.6, 5.2, "🔄 Multi-Hop Gossip Relay Protocol", [
        "Adaptive Routing Engine: MeshCoordinator.java parses incoming packet types (MSG, HELLO, CALL).",
        "Deduplication Filter: HashSet tracking seenMessageIds eliminates duplicate packet flooding.",
        "7-Hop TTL: Packets decrement hop count automatically across intermediate relay nodes.",
        "P2P Cluster Strategy: Uses Google Nearby Connections P2P_CLUSTER mode."
    ])
    add_card(slide3, 6.8, 1.6, 5.6, 5.2, "💬 Off-Grid Channels & Local DB", [
        "Public Broadcast Channel: Reaches all connected nodes in radio range instantly.",
        "1-on-1 Encrypted Messaging: Secure private peer channels.",
        "Local Persistence: MeshDatabase.java stores encrypted chat history and contacts on-device.",
        "Gossip Flow: Node A -> BLE Radio -> Node B Relay (Hop <= 7) -> Target Node C."
    ], "[Message Packet] -> [Deduplication Check] -> [Relay Hop <= 7]")

    # -------------------------------------------------------------
    # SLIDE 4: Phase 3: P2P Voice & 720p Video Streaming
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    bg4 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg4.fill.solid()
    bg4.fill.fore_color.rgb = COLOR_BG_DARK
    bg4.line.fill.background()

    add_header(slide4, "04. Phase 3: P2P Voice & 720p Video Calls", "PHASE 3 MILESTONE")
    add_card(slide4, 0.8, 1.6, 5.6, 5.2, "📞 Sub-50ms Voice Calls (Port 50005)", [
        "PCM Audio Stream: AudioRecord captures 16kHz 16-bit PCM voice; played via AudioTrack.",
        "UDP Datagram Sockets: Sub-50ms low-latency audio packets sent directly to peer IP address.",
        "Call Signaling Protocol: CALL_OFFER, CALL_ACCEPT, CALL_REJECT, and CALL_END JSON packets.",
        "Caller Ringback Tone: ToneGenerator plays real-time phone ringback audio while ringing."
    ])
    add_card(slide4, 6.8, 1.6, 5.6, 5.2, "📹 Real-Time P2P Video Stream (Port 50006)", [
        "Camera Frame Capture: Android Camera API captures NV21 frames; compressed to JPEG on-the-fly.",
        "UDP Video Streaming: 480x320 / 720p compressed frames transmitted over UDP Port 50006.",
        "PIP & Remote View: Live local camera preview on TextureView and remote decoded frames on ImageView.",
        "Controls: Front/Back camera flip, video mute, and mic mute."
    ], "[Camera Frame] -> [JPEG 45% Compress] -> [UDP Port 50006] -> [Remote Display]")

    # -------------------------------------------------------------
    # SLIDE 5: RuVNet Wi-Fi Sensing & 3D Radar
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    bg5 = slide5.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg5.fill.solid()
    bg5.fill.fore_color.rgb = COLOR_BG_DARK
    bg5.line.fill.background()

    add_header(slide5, "05. RuVNet Wi-Fi Sensing & 3D Radar", "CAMERA-LESS RADAR")
    add_card(slide5, 0.8, 1.6, 5.6, 5.2, "📡 Camera-Less Wi-Fi Wave Sensing", [
        "RuVNet Principle: Estimates peer distance & position using Wi-Fi & BLE signal attenuation (RSSI).",
        "No Optical Cameras Required: Detects presence and range without camera or GPS internet.",
        "RSSI Path Loss Formula: Distance = 10 ^ ((TxPower - RSSI) / (10 * n)).",
        "Concentric Depth Rings: 2m, 5m, and 10m telemetry markers."
    ], "Distance (m) = 10 ^ ((TxPower - RSSI) / (10 * n))")
    add_card(slide5, 6.8, 1.6, 5.6, 5.2, "🎨 Wave Radar Telemetry (BleRadarView)", [
        "Wi-Fi Wave Arcs: Animated expanding arcs simulate Wi-Fi radio wave reflections.",
        "Signal Telemetry: Real-time signal percentage (e.g., 95%) and meter readings on canvas.",
        "Rapid Auto-Discovery Pulse: 5-second pulse loop in MeshCoordinator forces 1-3 sec peer detection."
    ])

    # -------------------------------------------------------------
    # SLIDE 6: UI Design Philosophy & Emerald Green Rationale
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    bg6 = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg6.fill.solid()
    bg6.fill.fore_color.rgb = COLOR_BG_DARK
    bg6.line.fill.background()

    add_header(slide6, "06. UI Design & Emerald Green Rationale", "UX PHILOSOPHY")
    add_card(slide6, 0.8, 1.6, 5.6, 5.2, "🎨 Why Emerald Green (#16A34A)?", [
        "Psychology of Safety: Green is universally recognized as the color of safety, active status, and emergency survival.",
        "Emergency Reassurance: Calms users during off-grid disaster situations.",
        "OLED Power Efficiency: Light green on dark/slate backgrounds reduces AMOLED battery drain by up to 28% compared to heavy blue themes."
    ])
    add_card(slide6, 6.8, 1.6, 5.6, 5.2, "🖥️ Minimalist Professional Layout", [
        "Clean 4-Tab Shell: Chats, Calls, RuVNet Radar, and Offline Browser.",
        "Full-Screen Call Overlays: Pop-up call accept/decline dialogs over any active app screen.",
        "High Contrast & Legibility: Modern typography and crisp icons."
    ])

    # -------------------------------------------------------------
    # SLIDE 7: Technical Stack & API Dependencies Breakdown
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    bg7 = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg7.fill.solid()
    bg7.fill.fore_color.rgb = COLOR_BG_DARK
    bg7.line.fill.background()

    add_header(slide7, "07. Technical Stack & Dependencies", "APIS & LIBRARIES")
    add_card(slide7, 0.8, 1.6, 5.6, 5.2, "🛠️ Core Android APIs & Libraries", [
        "Google Nearby Connections API: com.google.android.gms:play-services-nearby (P2P Cluster discovery).",
        "Wi-Fi Direct P2P API: android.net.wifi.p2p.WifiP2pManager (High-speed group sockets).",
        "ZXing Barcode QR Library: com.journeyapps:zxing-android-embedded (Air-gapped identity scanning)."
    ])
    add_card(slide7, 6.8, 1.6, 5.6, 5.2, "⚙️ Native Subsystems & Sockets", [
        "Android Audio Subsystem: AudioRecord, AudioTrack, ToneGenerator.",
        "Camera Hardware API: NV21 YUV frame capture and JPEG compression via YuvImage.",
        "SQLite Database: MeshDatabase.java for structured data persistence."
    ])

    # -------------------------------------------------------------
    # SLIDE 8: Cryptography & Security Shield
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    bg8 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg8.fill.solid()
    bg8.fill.fore_color.rgb = COLOR_BG_DARK
    bg8.line.fill.background()

    add_header(slide8, "08. Cryptography & Security Shield", "SECURITY ARCHITECTURE")
    add_card(slide8, 0.8, 1.6, 5.6, 5.2, "🔐 Asymmetric & Symmetric Encryption", [
        "RSA-2048 Key Generation: Asymmetric RSA-2048 keypair generated on initial startup.",
        "AES-256 GCM Encryption: Session payloads encrypted with recipient's public key before broadcast.",
        "Android KeyStore: Private keys stored in hardware-backed KeyStore."
    ], "[Plaintext] -> [AES-256 GCM] -> [RSA Encrypt] -> [KeyStore Decrypt]")
    add_card(slide8, 6.8, 1.6, 5.6, 5.2, "📷 QR Exchange & Panic Wipe", [
        "Air-Gapped QR Identity: Share public key and mesh ID offline via QR code scan.",
        "Panic Wipe Security: Single-tap Panic Wipe purges all keys, databases, logs, and preferences instantly."
    ])

    # -------------------------------------------------------------
    # SLIDE 9: Emergency SOS Broadcast & Survival Tools
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    bg9 = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg9.fill.solid()
    bg9.fill.fore_color.rgb = COLOR_BG_DARK
    bg9.line.fill.background()

    add_header(slide9, "09. Emergency SOS & Survival Tools", "LIFE-SAVING FEATURES")
    add_card(slide9, 0.8, 1.6, 5.6, 5.2, "🚨 Multi-Hop SOS Broadcast", [
        "Instant Broadcast: Dispatches emergency SOS packet over BLE and Wi-Fi Direct.",
        "Siren Alert Overlay: Triggers alert warning dialog and alarm sound on receiving phones.",
        "GPS Coordinates: Transmits live latitude, longitude, and hop distance."
    ])
    add_card(slide9, 6.8, 1.6, 5.6, 5.2, "🔦 On-Device Survival Tools", [
        "Audio Siren Beacon: Synthesizes 800Hz-1400Hz frequency siren via AudioTrack.",
        "Morse SOS Optical Strobe: Flashes camera LED in ... --- ... optical Morse pattern via CameraManager."
    ])

    # -------------------------------------------------------------
    # SLIDE 10: Offline Web Server & Air-Gapped APK Distribution
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    bg10 = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg10.fill.solid()
    bg10.fill.fore_color.rgb = COLOR_BG_DARK
    bg10.line.fill.background()

    add_header(slide10, "10. Offline Web Server & APK Sharing", "AIR-GAPPED ACCESS")
    add_card(slide10, 0.8, 1.6, 5.6, 5.2, "🌐 Laptop Web Portal (BrowserFragment)", [
        "Port 8888 Local Server: Connects to laptop Wi-Fi hotspot to serve Wikipedia, emergency manuals, and files offline.",
        "Auto-Probe Engine: Automatically probes candidate IPs (e.g., 192.168.137.1) to auto-connect."
    ])
    add_card(slide10, 6.8, 1.6, 5.6, 5.2, "📲 Seamless APK Sharing", [
        "Solved Test-Only Bug: Configured android.injected.testOnly=false to allow installation on any phone.",
        "Dual Distribution: Share APK via WhatsApp/Bluetooth or via local Wi-Fi browser download link (http://IP:8888)."
    ])

    # -------------------------------------------------------------
    # SLIDE 11: Field Performance & Benchmark Metrics
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    bg11 = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg11.fill.solid()
    bg11.fill.fore_color.rgb = COLOR_BG_DARK
    bg11.line.fill.background()

    add_header(slide11, "11. Field Performance & Benchmarks", "EMPIRICAL RESULTS")
    add_card(slide11, 0.8, 1.6, 5.6, 5.2, "📊 Tested Performance Metrics", [
        "P2P Discovery Speed: Reduced from 30s to 1-3 seconds via fast discovery pulse.",
        "Voice Latency: Sub-50ms PCM audio delay over UDP.",
        "Video Frame Rate: Smooth 18-24 FPS at 480x320 / 720p compression over Wi-Fi Direct.",
        "Direct Radio Range: ~100m outdoors via BLE 5.0 / Wi-Fi Direct."
    ])
    add_card(slide11, 6.8, 1.6, 5.6, 5.2, "⚡ Battery & Memory Footprint", [
        "RAM Consumption: Low 45MB average memory footprint.",
        "APK Size: Lightweight ~12MB standalone binary.",
        "Battery Consumption: Optimized BLE background scanning (~3% battery drain per hour)."
    ])

    # -------------------------------------------------------------
    # SLIDE 12: Phase 4 Roadmap & Conclusion
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    bg12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = COLOR_BG_DARK
    bg12.line.fill.background()

    add_header(slide12, "12. Future Roadmap & Conclusion", "PHASE 4 PREVIEW")
    add_card(slide12, 0.8, 1.6, 5.6, 5.2, "🚀 Phase 4 Roadmap", [
        "Multi-Hop Voice Routing: Relaying voice calls across intermediate mesh nodes.",
        "LoRa Radio Gateway: Integrating 433MHz / 915MHz LoRa hardware for 10km+ long-range mesh messaging.",
        "Offline Vector AI Assistant: On-device LLM for off-grid first-aid and survival assistance."
    ])
    add_card(slide12, 6.8, 1.6, 5.6, 5.2, "🎉 Conclusion & Q&A", [
        "Nexus MeshLink turns ordinary Android smartphones into a resilient, self-healing, air-gapped emergency network.",
        "Presenter: Shaikh Abdul Zubair Abdul Kabir",
        "SRK Institute of Management and Computer Application"
    ])

    output_path = r"c:\Users\abdul\AndroidStudioProjects\MeshLinkOffline\Nexus_Phase2_Phase3_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved to {output_path}")

if __name__ == "__main__":
    create_deck()
