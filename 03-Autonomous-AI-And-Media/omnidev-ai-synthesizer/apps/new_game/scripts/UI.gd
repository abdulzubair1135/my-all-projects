extends Control
# ============================================================
# NEXUS PITCH DECK — Godot 4 Presentation Engine
# Palette: Black / Silver / White / Green
# Author: Shaikh Abdul Zubair Abdul Kabir
# ============================================================

var slides: Array = []
var current_index: int = 0
var slide_root: Control
var bg_layer: ColorRect
var accent_glow: ColorRect
var header_bar: ColorRect
var footer_bar: ColorRect
var progress_fill: ColorRect
var progress_track: ColorRect
var slide_num_label: Label
var deck_label: Label
var nav_hint: Label
var _animating: bool = false
var _pulse_t: float = 0.0
var _bg_particles: Array = []

const THEME = preload("res://scripts/PPT_Theme.gd")

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	_build_slides()
	_build_chrome()
	show_slide(0, false)

func _build_slides() -> void:
	# 14-slide NEXUS pitch deck (mirrors executive JSON outline)
	slides = [
		{
			"kind": "title",
			"category": "EXECUTIVE BRIEFING",
			"title": "NEXUS",
			"subtitle": "MeshLink Offline Tactical Mesh",
			"meta": "Autonomous Zero-Cloud Mesh Grid",
			"presenter": "Shaikh Abdul Zubair Abdul Kabir",
			"institution": "SRK Institute of Management and Computer Application",
			"bullets": []
		},
		{
			"kind": "content",
			"category": "STRATEGIC OVERVIEW",
			"title": "The Critical Problem",
			"subtitle": "Telecom Collapse Is a Life-Safety Failure",
			"bullets": [
				"Cell towers, 4G/5G backhaul, and cloud OTP fail under power loss, fiber cuts, or congestion.",
				"Kumbh Mela, stadiums, and evacuation zones overload capacity even when infrastructure stands.",
				"Victims cannot call, message, or authenticate; rescue loses situational awareness.",
				"Existing apps assume cloud identity, SIM, OTP, and internet — none survive the first 72 hours.",
				"Impact metric: over 70% of disaster comms failures trace to backhaul, power, or cloud dependency.",
				"Presenter Talking Point: NEXUS removes every single point of failure."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 1 — LIVE TODAY",
			"title": "Phase 1 Accomplishments",
			"subtitle": "Zero-login, zero-cloud, zero-OTP mesh foundation — running on device",
			"bullets": [
				"Zero-Login Cryptographic DID Identity: mesh@DID via hardware Ed25519 / X25519.",
				"BLE 5.0 Gossip Relay Discovery: peer-to-peer multi-hop text with no internet.",
				"Offline Browser Auto-Discovery: phone opens local laptop supernode at http://<host>:8888.",
				"Instant APK Sharing: peer-to-peer transfer straight from Android Settings.",
				"2.8 kHz Acoustic Rescue Siren: high-penetration audible beacon for rubble response.",
				"Optical Morse Distress Strobe: silent, RF-denied visual SOS.",
				"Presenter Talking Point: Phase 1 is installed, tested, demonstrable on hardware today."
			]
		},
		{
			"kind": "table",
			"category": "TECHNICAL ARCHITECTURE",
			"title": "Tri-Transport Architecture",
			"subtitle": "BLE + Wi-Fi Direct + Edge Supernode, coordinated by payload profile",
			"headers": ["Layer", "Transport", "Payload", "Metric"],
			"rows": [
				["L1", "BLE 5.0 Mesh", "Text / SOS / receipts", "<512 B · multi-hop"],
				["L2", "Wi-Fi Direct P2P", "Voice / video / photos", "150 Mbps direct"],
				["L3", "Edge Laptop Supernode", "Local web / maps / docs", "mDNS :8888"]
			],
			"bullets": [
				"Failover: BLE is always-on control plane; Wi-Fi Direct forms high-bandwidth islands; Supernode anchors local intranet.",
				"Presenter Talking Point: one radio is fragile; three coordinated transports create an adaptive mesh."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 2 — DEEP DIVE",
			"title": "Signal-Grade Cryptography",
			"subtitle": "Double Ratchet, Perfect Forward Secrecy, relay blindness",
			"bullets": [
				"Double Ratchet Algorithm: X3DH key agreement plus symmetric KDF chain per message.",
				"Perfect Forward Secrecy: current key compromise never decrypts past sessions.",
				"Break-in Recovery: post-compromise security via ongoing DH ratchet.",
				"Multi-hop relay blindness: intermediaries route ciphertext only.",
				"Duress PIN: alternate credential opens decoy vault or wipes sensitive state.",
				"Android FLAG_SECURE: blocks screenshots, recents, and screen recording.",
				"Presenter Talking Point: NEXUS is engineered to Signal-grade standards."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 2 — DEEP DIVE",
			"title": "Hardware-Accelerated P2P Media",
			"subtitle": "Low-latency Opus voice and 720p H.264 video over direct UDP",
			"bullets": [
				"Voice: Opus codec over direct UDP sockets, push-to-talk and full duplex.",
				"Video: 720p at 30 FPS via Android MediaCodec hardware H.264 encode/decode.",
				"Picture-in-Picture: multitask during maps, triage, or chat.",
				"Dynamic bitrate fallback: RSSI and packet-loss telemetry adapt resolution and rate.",
				"Metrics target: <150 ms mouth-to-ear voice; 200 kbps to 2 Mbps video envelope.",
				"Presenter Talking Point: nearby phones become a field radio and video link."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 2 — DEEP DIVE",
			"title": "Delay-Tolerant Networking",
			"subtitle": "Store-and-forward mules, deduplication, bounded TTL",
			"bullets": [
				"Digital Mules: volunteers physically carry encrypted bundles between disconnected sectors.",
				"Store-and-forward: messages persist in local vault until relay or destination appears.",
				"SHA-256 deduplication cache prevents broadcast packet storms.",
				"Dynamic 7-hop TTL: preserves reach across campus, village, or stadium.",
				"Bundle custody: optional delivery receipts and expiry for storage and battery discipline.",
				"Presenter Talking Point: DTN makes the network tolerant to delay, disruption, and human mobility."
			]
		},
		{
			"kind": "content",
			"category": "UI / UX PHILOSOPHY",
			"title": "Familiar, Fast, Field-Ready",
			"subtitle": "WhatsApp and Signal minimalism for sunlight and one-hand use",
			"bullets": [
				"Delivery states mirror WhatsApp: single tick sent, double gray tick delivered, double green tick read.",
				"High-sunlight legibility: white base, slate gray structure, emerald accents, large touch targets.",
				"One-handed thumb reach: bottom-anchored navigation and primary actions.",
				"2-second hold-to-activate SOS prevents accidental distress broadcasts.",
				"Minimal cognitive load: no cloud account screens, no OTP, no onboarding friction.",
				"Presenter Talking Point: in panic, users do not learn new UX."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 3 — DEEP DIVE",
			"title": "Laptop Edge Supernodes",
			"subtitle": "A pocket internet for offline survivors and responders",
			"bullets": [
				"Auto-connecting mobile offline browser: detects supernode, opens local portal silently.",
				"Local Kiwix offline Wikipedia: full knowledge corpus at survivor fingertips.",
				"Emergency medical first-aid encyclopedia: triage, bleeding, fractures, burns, hypothermia.",
				"Offline OpenStreetMap vector tile server: roads, landmarks, shelters — no internet.",
				"Central incident dispatch map: live pins for SOS, hazards, shelters, requests.",
				"Presenter Talking Point: the supernode converts a laptop into a community knowledge server."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 3 — DEEP DIVE",
			"title": "Autonomous Disaster Grid",
			"subtitle": "Geo-drops, micro-triage, localized hazard intelligence",
			"bullets": [
				"Dead-Man's Digital Geo-Drop: encrypted coordinates unlock only upon physical arrival.",
				"64-byte START triage micro-packets: color, vitals, location, needs — ultra-compact.",
				"Offline localized hazard mapping: downed powerlines, flood zones, blocked roads.",
				"Peer-validated reports: time-decay and confidence scoring reduce rumor propagation.",
				"Grid autonomy: nodes keep routing, mapping, and triaging even when isolated.",
				"Presenter Talking Point: NEXUS becomes an autonomous disaster grid, not just a chat app."
			]
		},
		{
			"kind": "content",
			"category": "PHASE 3 — DEEP DIVE",
			"title": "Asymmetric Satellite Uplink",
			"subtitle": "One gateway bridges thousands of offline survivors to cloud HQ",
			"bullets": [
				"Asymmetric uplink: one vehicle with Starlink or 5G relays up to 10,000 offline SOS alerts.",
				"Store-and-forward aggregation: mesh bundles compressed, deduplicated, encrypted metadata.",
				"Battery-adaptive scanning: 15% duty cycle below 20% battery; aggressive sleep otherwise.",
				"Gateway election: strongest link, power, and location wins — no permanent bottleneck.",
				"HQ interoperability: cloud dashboard receives structured SOS, triage, map, hazard feeds.",
				"Presenter Talking Point: we do not need 10,000 satellite phones — just one smart gateway."
			]
		},
		{
			"kind": "table",
			"category": "ROADMAP",
			"title": "Roadmap and Milestones",
			"subtitle": "Staged delivery: live demo to autonomous grid",
			"headers": ["Milestone", "Scope", "Status"],
			"rows": [
				["M1 — Phase 1", "DID identity, BLE relay, browser discovery, APK share, siren", "Completed · Live"],
				["M2 — Phase 2", "Double Ratchet, PFS, duress PIN, Opus, H.264, DTN", "In Progress"],
				["M3 — Phase 3", "Supernodes, Kiwix, OSM, geo-drop, START triage, gateway", "On Horizon"]
			],
			"bullets": [
				"Validation: lab throughput, multi-hop range, battery profiling, cryptographic review, field simulation.",
				"Presenter Talking Point: the roadmap delivers a demonstrable survival grid, not theory."
			]
		},
		{
			"kind": "content",
			"category": "IMPACT",
			"title": "Impact and Differentiation",
			"subtitle": "Why NEXUS outperforms cloud-first and single-radio alternatives",
			"bullets": [
				"Zero cloud dependency: no servers, OTP, SIM, or account required for core comms.",
				"Tri-radio resilience: BLE, Wi-Fi Direct, and Supernode uplink cover text, media, and local web.",
				"Security posture: Ed25519 / X25519, Double Ratchet, PFS, relay blindness, FLAG_SECURE, duress PIN.",
				"Deployment speed: APK share from Settings enables viral field installation without app stores.",
				"Scalability path: one satellite or 5G gateway aggregates up to 10,000 offline SOS alerts.",
				"Presenter Talking Point: NEXUS is not a feature — it is a missing layer of national resilience."
			]
		},
		{
			"kind": "closing",
			"category": "LIVE DEMONSTRATION",
			"title": "Live Demonstration",
			"subtitle": "Handover to physical device walkthrough",
			"presenter": "Shaikh Abdul Zubair Abdul Kabir",
			"bullets": [
				"Demo 1 — Zero-login DID identity and mesh@DID handshake.",
				"Demo 2 — BLE 5.0 multi-hop text and SOS relay between devices.",
				"Demo 3 — Offline browser auto-discovery to laptop supernode port 8888.",
				"Demo 4 — Acoustic 2.8 kHz siren and optical Morse distress strobe.",
				"Demo 5 — APK sharing directly from Android Settings.",
				"Closing — Phase 1 live; Phase 2 cryptography and media in progress; Phase 3 autonomous grid."
			]
		}
	]

# ============================================================
# CHROME — persistent header, footer, progress, particles
# ============================================================
func _build_chrome() -> void:
	# Background
	bg_layer = ColorRect.new()
	bg_layer.color = THEME.BG_DEEP
	bg_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg_layer)

	# Ambient green glow (top-right)
	accent_glow = ColorRect.new()
	accent_glow.color = Color(THEME.GREEN.r, THEME.GREEN.g, THEME.GREEN.b, 0.06)
	accent_glow.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	accent_glow.anchor_left = 0.72
	accent_glow.anchor_top = -0.05
	accent_glow.anchor_right = 1.15
	accent_glow.anchor_bottom = 0.55
	accent_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(accent_glow)

	# Slide content root
	slide_root = Control.new()
	slide_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	slide_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(slide_root)

	# Header bar
	header_bar = ColorRect.new()
	header_bar.color = Color(THEME.SILVER.r, THEME.SILVER.g, THEME.SILVER.b, 0.06)
	header_bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	header_bar.custom_minimum_size = Vector2(0, 48)
	header_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(header_bar)

	deck_label = THEME.make_label("NEXUS  ·  MeshLink Offline Tactical Mesh", THEME.FONT_SMALL, THEME.GREEN)
	deck_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
	deck_label.position = Vector2(THEME.MARGIN_X, 14)
	add_child(deck_label)

	slide_num_label = THEME.make_label("", THEME.FONT_SMALL, THEME.SILVER_DIM)
	slide_num_label.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	slide_num_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	slide_num_label.anchor_left = 0.75
	slide_num_label.anchor_right = 1.0
	slide_num_label.position = Vector2(0, 14)
	add_child(slide_num_label)

	# Footer bar
	footer_bar = ColorRect.new()
	footer_bar.color = Color(THEME.SILVER.r, THEME.SILVER.g, THEME.SILVER.b, 0.05)
	footer_bar.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	footer_bar.custom_minimum_size = Vector2(0, 40)
	footer_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(footer_bar)

	# Progress track + fill
	progress_track = ColorRect.new()
	progress_track.color = Color(THEME.SILVER.r, THEME.SILVER.g, THEME.SILVER.b, 0.15)
	progress_track.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	progress_track.anchor_top = 1.0
	progress_track.anchor_bottom = 1.0
	progress_track.offset_top = -4
	progress_track.offset_bottom = 0
	progress_track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(progress_track)

	progress_fill = ColorRect.new()
	progress_fill.color = THEME.GREEN
	progress_fill.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	progress_fill.anchor_top = 1.0
	progress_fill.anchor_bottom = 1.0
	progress_fill.offset_top = -4
	progress_fill.offset_bottom = 0
	progress_fill.custom_minimum_size = Vector2(0, 4)
	progress_fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(progress_fill)

	nav_hint = THEME.make_label("←  →  Navigate    ·    SPACE  Advance    ·    F  Fullscreen    ·    ESC  Restart", THEME.FONT_NUM, THEME.SILVER_DIM)
	nav_hint.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	nav_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	nav_hint.offset_top = -34
	add_child(nav_hint)

	# Input
	set_process_input(true)
	set_process(true)

# ============================================================
# INPUT
# ============================================================
func _input(event: InputEvent) -> void:
	if _animating:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_RIGHT, KEY_DOWN, KEY_SPACE, KEY_ENTER, KEY_PAGEDOWN:
				if current_index < slides.size() - 1:
					show_slide(current_index + 1, true)
				else:
					show_slide(0, true)
			KEY_LEFT, KEY_UP, KEY_PAGEUP, KEY_BACKSPACE:
				if current_index > 0:
					show_slide(current_index - 1, true)
				else:
					show_slide(slides.size() - 1, true)
			KEY_HOME:
				show_slide(0, true)
			KEY_END:
				show_slide(slides.size() - 1, true)
			KEY_F:
				var w := get_window()
				if w:
					w.mode = Window.MODE_FULLSCREEN if w.mode != Window.MODE_FULLSCREEN else Window.MODE_WINDOWED
			KEY_ESCAPE:
				show_slide(0, true)

func _process(delta: float) -> void:
	# Ambient pulse on green glow
	_pulse_t += delta
	if accent_glow:
		var a : float = 0.05 + 0.035 * (0.5 + 0.5 * sin(_pulse_t * 1.6))
		accent_glow.color = Color(THEME.GREEN.r, THEME.GREEN.g, THEME.GREEN.b, a)

# ============================================================
# SLIDE RENDERING
# ============================================================
func show_slide(index: int, animate: bool) -> void:
	if index < 0 or index >= slides.size():
		return
	current_index = index
	_animating = true
	_sync_chrome()

	# Fade out old content
	if slide_root.get_child_count() > 0:
		var t_out := create_tween()
		for ch in slide_root.get_children():
			if ch is CanvasItem:
				t_out.parallel().tween_property(ch, "modulate:a", 0.0, THEME.ANIM_SLIDE_FADE * 0.6)
		await t_out.finished

	# Clear old
	for ch in slide_root.get_children():
		ch.queue_free()
	await get_tree().process_frame

	# Build new slide
	var data: Dictionary = slides[index]
	_build_slide_content(data)

	# Entrance fade
	var t_in := create_tween()
	for ch in slide_root.get_children():
		if ch is CanvasItem:
			ch.modulate.a = 0.0
			t_in.parallel().tween_property(ch, "modulate:a", 1.0, THEME.ANIM_SLIDE_FADE)
	await t_in.finished

	# Staggered bullets + animation hooks
	_animate_entrance(data)
	await get_tree().create_timer(0.4).timeout
	_animating = false

func _sync_chrome() -> void:
	if slide_num_label:
		slide_num_label.text = "%02d / %02d" % [current_index + 1, slides.size()]
	if progress_fill:
		var ratio : float = float(current_index + 1) / float(slides.size())
		var vw : float = size.x
		if vw <= 0:
			vw = 1280.0
		progress_fill.custom_minimum_size = Vector2(vw * ratio, 4)
		progress_fill.size = Vector2(vw * ratio, 4)

func _build_slide_content(data: Dictionary) -> void:
	var kind : String = data.get("kind", "content")
	match kind:
		"title":
			_build_title_slide(data)
		"table":
			_build_table_slide(data)
		"closing":
			_build_closing_slide(data)
		_:
			_build_content_slide(data)

func _add_common_heading(data: Dictionary, y_start: float) -> float:
	# Category (green chip)
	var cat : String = data.get("category", "")
	if cat != "":
		var cat_lbl := THEME.make_label(cat, THEME.FONT_SMALL, THEME.GREEN)
		cat_lbl.position = Vector2(THEME.MARGIN_X, y_start)
		slide_root.add_child(cat_lbl)
		# Underline accent
		var line := ColorRect.new()
		line.color = THEME.GREEN
		line.position = Vector2(THEME.MARGIN_X, y_start + 26)
		line.size = Vector2(0, 2)
		line.custom_minimum_size = Vector2(0, 2)
		slide_root.add_child(line)
		var t := create_tween()
		t.tween_property(line, "size:x", 60.0, THEME.ANIM_LINE_GROW)
		y_start += 42

	# Title
	var title_lbl := THEME.make_label(data.get("title", ""), THEME.FONT_H1, THEME.WHITE_SOFT)
	title_lbl.position = Vector2(THEME.MARGIN_X, y_start)
	slide_root.add_child(title_lbl)
	y_start += 56

	# Subtitle
	var sub : String = data.get("subtitle", "")
	if sub != "":
		var sub_lbl := THEME.make_label(sub, THEME.FONT_BODY, THEME.SILVER)
		sub_lbl.position = Vector2(THEME.MARGIN_X, y_start)
		slide_root.add_child(sub_lbl)
		y_start += 46

	# Divider
	var divider := ColorRect.new()
	divider.color = Color(THEME.SILVER.r, THEME.SILVER.g, THEME.SILVER.b, 0.18)
	divider.position = Vector2(THEME.MARGIN_X, y_start)
	divider.custom_minimum_size = Vector2(0, 1)
	divider.size = Vector2(size.x - THEME.MARGIN_X * 2, 1)
	slide_root.add_child(divider)
	y_start += 24

	return y_start

# ---------- TITLE SLIDE ----------
func _build_title_slide(data: Dictionary) -> void:
	var center := Control.new()
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	slide_root.add_child(center)

	# Big NEXUS title
	var title := THEME.make_label(data.get("title", "NEXUS"), THEME.FONT_TITLE + 40, THEME.WHITE)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.set_anchors_preset(Control.PRESET_TOP_WIDE)
	title.offset_top = 190
	title.position.x = 0
	center.add_child(title)

	# Accent underline
	var ul := ColorRect.new()
	ul.color = THEME.GREEN
	ul.set_anchors_preset(Control.PRESET_TOP_WIDE)
	ul.anchor_left = 0.35
	ul.anchor_right = 0.65
	ul.offset_top = 300
	ul.custom_minimum_size = Vector2(0, 3)
	ul.size = Vector2(size.x * 0.3, 3)
	center.add_child(ul)

	# Subtitle
	var sub := THEME.make_label(data.get("subtitle", ""), THEME.FONT_H2, THEME.SILVER_BRIGHT)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.set_anchors_preset(Control.PRESET_TOP_WIDE)
	sub.offset_top = 320
	center.add_child(sub)

	# Meta line
	var meta := THEME.make_label(data.get("meta", ""), THEME.FONT_BODY, THEME.GREEN)
	meta.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	meta.set_anchors_preset(Control.PRESET_TOP_WIDE)
	meta.offset_top = 368
	center.add_child(meta)

	# Presenter card
	var card := THEME.make_panel(THEME.BG_PANEL, THEME.BORDER_GREEN, 12)
	card.set_anchors_preset(Control.PRESET_TOP_WIDE)
	card.anchor_left = 0.25
	card.anchor_right = 0.75
	card.offset_top = 450
	card.custom_minimum_size = Vector2(0, 130)
	center.add_child(card)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 6)
	card.add_child(v)
	var pres := THEME.make_label("PRESENTER", THEME.FONT_NUM, THEME.GREEN)
	pres.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(pres)
	var pname := THEME.make_label(data.get("presenter", ""), THEME.FONT_H2, THEME.WHITE)
	pname.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(pname)
	var inst := THEME.make_label(data.get("institution", ""), THEME.FONT_SMALL, THEME.SILVER)
	inst.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	v.add_child(inst)

# ---------- CONTENT SLIDE ----------
func _build_content_slide(data: Dictionary) -> void:
	var y := float(THEME.MARGIN_TOP + 48)
	y = _add_common_heading(data, y)

	var bullets : Array = data.get("bullets", [])
	var row_h : float = 44.0
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 10)
	vbox.position = Vector2(THEME.MARGIN_X, y)
	vbox.custom_minimum_size = Vector2(size.x - THEME.MARGIN_X * 2, 0)
	vbox.size = Vector2(size.x - THEME.MARGIN_X * 2, 0)
	slide_root.add_child(vbox)

	for i in range(bullets.size()):
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 14)
		row.modulate.a = 0.0
		row.name = "bullet_%d" % i

		# Green bullet dot
		var dot := ColorRect.new()
		dot.color = THEME.GREEN
		dot.custom_minimum_size = Vector2(8, 8)
		dot.size = Vector2(8, 8)
		var dot_wrap := CenterContainer.new()
		dot_wrap.custom_minimum_size = Vector2(16, 26)
		dot_wrap.add_child(dot)
		row.add_child(dot_wrap)

		var txt : String = String(bullets[i])
		var is_tp : bool = txt.begins_with("Presenter Talking Point")
		var body := THEME.make_label(txt, THEME.FONT_BODY, THEME.WHITE_SOFT if is_tp else THEME.SILVER_BRIGHT)
		body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(body)

		vbox.add_child(row)

# ---------- TABLE SLIDE ----------
func _build_table_slide(data: Dictionary) -> void:
	var y := float(THEME.MARGIN_TOP + 48)
	y = _add_common_heading(data, y)

	var headers : Array = data.get("headers", [])
	var rows : Array = data.get("rows", [])

	var grid := GridContainer.new()
	grid.columns = headers.size()
	grid.add_theme_constant_override("h_separation", 18)
	grid.add_theme_constant_override("v_separation", 12)
	grid.position = Vector2(THEME.MARGIN_X, y)
	grid.custom_minimum_size = Vector2(size.x - THEME.MARGIN_X * 2, 0)
	slide_root.add_child(grid)

	# Header row
	for h in headers:
		var hl := THEME.make_label(String(h), THEME.FONT_SMALL, THEME.GREEN)
		hl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		grid.add_child(hl)

	# Body rows
	for r_i in range(rows.size()):
		var row : Array = rows[r_i]
		for c in row:
			var cell := THEME.make_label(String(c), THEME.FONT_BODY, THEME.SILVER_BRIGHT)
			cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			cell.modulate.a = 0.0
			cell.name = "cell_%d_%d" % [r_i, grid.get_child_count()]
			grid.add_child(cell)

	# Extra bullets below table
	var bullets : Array = data.get("bullets", [])
	if bullets.size() > 0:
		var y2 : float = y + 90.0 + rows.size() * 40.0
		var vbox := VBoxContainer.new()
		vbox.add_theme_constant_override("separation", 10)
		vbox.position = Vector2(THEME.MARGIN_X, y2)
		vbox.custom_minimum_size = Vector2(size.x - THEME.MARGIN_X * 2, 0)
		slide_root.add_child(vbox)
		for i in range(bullets.size()):
			var row := HBoxContainer.new()
			row.add_theme_constant_override("separation", 14)
			row.modulate.a = 0.0
			row.name = "bullet_%d" % i
			var dot := ColorRect.new()
			dot.color = THEME.GREEN
			dot.custom_minimum_size = Vector2(8, 8)
			var wrap := CenterContainer.new()
			wrap.custom_minimum_size = Vector2(16, 26)
			wrap.add_child(dot)
			row.add_child(wrap)
			var body := THEME.make_label(String(bullets[i]), THEME.FONT_BODY, THEME.SILVER_BRIGHT)
			body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			row.add_child(body)
			vbox.add_child(row)

# ---------- CLOSING SLIDE ----------
func _build_closing_slide(data: Dictionary) -> void:
	var y := float(THEME.MARGIN_TOP + 48)
	y = _add_common_heading(data, y)

	# Bullets
	var bullets : Array = data.get("bullets", [])
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 12)
	vbox.position = Vector2(THEME.MARGIN_X, y)
	vbox.custom_minimum_size = Vector2(size.x - THEME.MARGIN_X * 2, 0)
	slide_root.add_child(vbox)
	for i in range(bullets.size()):
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 14)
		row.modulate.a = 0.0
		row.name = "bullet_%d" % i
		var dot := ColorRect.new()
		dot.color = THEME.GREEN
		dot.custom_minimum_size = Vector2(8, 8)
		var wrap := CenterContainer.new()
		wrap.custom_minimum_size = Vector2(16, 26)
		wrap.add_child(dot)
		row.add_child(wrap)
		var body := THEME.make_label(String(bullets[i]), THEME.FONT_BODY, THEME.SILVER_BRIGHT)
		body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(body)
		vbox.add_child(row)

	# Presenter chip
	if data.has("presenter"):
		var chip := THEME.make_panel(THEME.BG_PANEL, THEME.BORDER_GREEN, 10)
		chip.position = Vector2(THEME.MARGIN_X, size.y - 180)
		chip.custom_minimum_size = Vector2(520, 70)
		chip.size = Vector2(520, 70)
		slide_root.add_child(chip)
		var v := VBoxContainer.new()
		v.add_theme_constant_override("separation", 2)
		chip.add_child(v)
		var cap := THEME.make_label("PRESENTER", THEME.FONT_NUM, THEME.GREEN)
		v.add_child(cap)
		var nm := THEME.make_label(data.get("presenter", ""), THEME.FONT_BODY, THEME.WHITE)
		v.add_child(nm)

# ============================================================
# ANIMATION LAYER — staggered bullets, table cells, pulse
# ============================================================
func _animate_entrance(data: Dictionary) -> void:
	var delay : float = 0.0
	# Fade in all bullet rows with stagger
	for ch in slide_root.get_children():
		if ch is VBoxContainer:
			for row in ch.get_children():
				if row.name.begins_with("bullet_"):
					var t := create_tween()
					t.tween_interval(delay)
					t.tween_property(row, "modulate:a", 1.0, THEME.ANIM_BULLET_FADE)
					# Slight slide up
					var start_x : float = row.position.x
					row.position.x = start_x - 18
					t.parallel().tween_property(row, "position:x", start_x, THEME.ANIM_BULLET_FADE)\
						.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
					delay += THEME.ANIM_BULLET_DELAY

	# Fade in table cells with stagger
	var stagger : float = 0.0
	for ch in slide_root.get_children():
		if ch is GridContainer:
			for cell in ch.get_children():
				if cell.name.begins_with("cell_") or (cell is Label):
					var t := create_tween()
					t.tween_interval(stagger)
					t.tween_property(cell, "modulate:a", 1.0, THEME.ANIM_BULLET_FADE)
					stagger += 0.05

	# Title drop-in animation
	for ch in slide_root.get_children():
		if ch is Label and ch.text == data.get("title", ""):
			var start_y : float = ch.position.y
			ch.position.y = start_y - 24
			var t := create_tween()
			t.tween_property(ch, "position:y", start_y, THEME.ANIM_TITLE_DROP)\
				.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)