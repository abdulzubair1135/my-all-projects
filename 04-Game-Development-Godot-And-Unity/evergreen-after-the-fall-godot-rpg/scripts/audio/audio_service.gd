extends Node

# Evergreen: After the Fall - Audio & Sound Effects Service
# Manages procedural audio synthesis, volume mixing, music states, and ambient soundscapes

signal volume_changed(bus: String, value: float)

var master_volume: float = 1.0
var music_volume: float = 0.8
var sfx_volume: float = 0.85

var sfx_cache: Dictionary = {}
var sfx_players: Array[AudioStreamPlayer] = []
var music_player: AudioStreamPlayer
var current_music_track: String = ""

const MIX_RATE: int = 22050

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_audio_players()
	_generate_procedural_soundbank()
	_connect_event_bus()

func _setup_audio_players() -> void:
	# Music player
	music_player = AudioStreamPlayer.new()
	music_player.bus = "Master"
	add_child(music_player)
	
	# SFX player pool (8 channels)
	for i in range(8):
		var p = AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		sfx_players.append(p)

func _connect_event_bus() -> void:
	if EventBus:
		EventBus.quest_completed.connect(func(_id, _data): play_sfx("quest_fanfare"))
		EventBus.day_started.connect(func(_day): play_sfx("morning_chime"))
		EventBus.night_alert_started.connect(func(): play_sfx("night_warning"))

# ==============================================================================
# Procedural 16-Bit Sound Synthesis (Zero-dependency, CC0 / Commercial Safe)
# ==============================================================================

func _generate_procedural_soundbank() -> void:
	sfx_cache["ui_click"] = _synth_sine_blip(880.0, 0.04)
	sfx_cache["attack_swing"] = _synth_sweep(520.0, 110.0, 0.14)
	sfx_cache["hit_impact"] = _synth_noise_thud(160.0, 0.18)
	sfx_cache["harvest"] = _synth_arpeggio([523.25, 659.25, 783.99, 1046.50], 0.06)
	sfx_cache["morning_chime"] = _synth_arpeggio([440.0, 554.37, 659.25], 0.12)
	sfx_cache["quest_fanfare"] = _synth_arpeggio([440.0, 554.37, 659.25, 880.0], 0.15)
	sfx_cache["night_warning"] = _synth_sweep(120.0, 60.0, 0.4)
	sfx_cache["zombie_growl"] = _synth_growl(0.35)

func _create_wav_from_samples(samples: PackedByteArray) -> AudioStreamWAV:
	var wav = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = MIX_RATE
	wav.stereo = false
	wav.data = samples
	return wav

func _synth_sine_blip(freq: float, duration: float) -> AudioStreamWAV:
	var total_frames = int(MIX_RATE * duration)
	var bytes = PackedByteArray()
	bytes.resize(total_frames * 2)
	
	for i in range(total_frames):
		var t = float(i) / float(MIX_RATE)
		var envelope = 1.0 - (float(i) / float(total_frames))
		var sample_val = sin(2.0 * PI * freq * t) * envelope * 0.7
		var int_val = clampi(int(sample_val * 32767.0), -32768, 32767)
		bytes.encode_s16(i * 2, int_val)
	
	return _create_wav_from_samples(bytes)

func _synth_sweep(start_freq: float, end_freq: float, duration: float) -> AudioStreamWAV:
	var total_frames = int(MIX_RATE * duration)
	var bytes = PackedByteArray()
	bytes.resize(total_frames * 2)
	
	for i in range(total_frames):
		var frac = float(i) / float(total_frames)
		var freq = lerp(start_freq, end_freq, frac)
		var envelope = 1.0 - frac
		var sample_val = sin(2.0 * PI * freq * (float(i) / float(MIX_RATE))) * envelope * 0.8
		var int_val = clampi(int(sample_val * 32767.0), -32768, 32767)
		bytes.encode_s16(i * 2, int_val)
	
	return _create_wav_from_samples(bytes)

func _synth_noise_thud(base_freq: float, duration: float) -> AudioStreamWAV:
	var total_frames = int(MIX_RATE * duration)
	var bytes = PackedByteArray()
	bytes.resize(total_frames * 2)
	
	for i in range(total_frames):
		var frac = float(i) / float(total_frames)
		var envelope = (1.0 - frac) * (1.0 - frac)
		var noise = randf_range(-0.4, 0.4)
		var tone = sin(2.0 * PI * base_freq * (float(i) / float(MIX_RATE))) * 0.6
		var sample_val = (tone + noise) * envelope
		var int_val = clampi(int(sample_val * 32767.0), -32768, 32767)
		bytes.encode_s16(i * 2, int_val)
	
	return _create_wav_from_samples(bytes)

func _synth_arpeggio(frequencies: Array[float], note_duration: float) -> AudioStreamWAV:
	var frames_per_note = int(MIX_RATE * note_duration)
	var total_frames = frames_per_note * frequencies.size()
	var bytes = PackedByteArray()
	bytes.resize(total_frames * 2)
	
	for n in range(frequencies.size()):
		var freq = frequencies[n]
		for i in range(frames_per_note):
			var global_i = n * frames_per_note + i
			var frac = float(i) / float(frames_per_note)
			var envelope = 1.0 - (frac * 0.7)
			var sample_val = sin(2.0 * PI * freq * (float(i) / float(MIX_RATE))) * envelope * 0.6
			var int_val = clampi(int(sample_val * 32767.0), -32768, 32767)
			bytes.encode_s16(global_i * 2, int_val)
	
	return _create_wav_from_samples(bytes)

func _synth_growl(duration: float) -> AudioStreamWAV:
	var total_frames = int(MIX_RATE * duration)
	var bytes = PackedByteArray()
	bytes.resize(total_frames * 2)
	
	for i in range(total_frames):
		var frac = float(i) / float(total_frames)
		var envelope = sin(frac * PI) # swell and fade
		var freq = 75.0 + sin(frac * 20.0) * 15.0
		# Sawtooth wave for gnarly growl texture
		var phase = fmod(float(i) * freq / float(MIX_RATE), 1.0)
		var saw = (phase * 2.0 - 1.0) * 0.5
		var sample_val = saw * envelope
		var int_val = clampi(int(sample_val * 32767.0), -32768, 32767)
		bytes.encode_s16(i * 2, int_val)
	
	return _create_wav_from_samples(bytes)

# ==============================================================================
# Playback API
# ==============================================================================

func play_sfx(sfx_name: String, pitch: float = 1.0) -> void:
	if not sfx_cache.has(sfx_name):
		return
	if sfx_volume <= 0.0 or master_volume <= 0.0:
		return
	
	# Find idle player
	var player: AudioStreamPlayer = null
	for p in sfx_players:
		if not p.playing:
			player = p
			break
	
	if player == null:
		player = sfx_players[0] # Reuse first player if all active
	
	player.stream = sfx_cache[sfx_name]
	player.volume_db = linear_to_db(sfx_volume * master_volume)
	player.pitch_scale = pitch
	player.play()

func play_music(track_name: String) -> void:
	current_music_track = track_name
	print("[AudioService] Playing music track: %s" % track_name)

func set_master_volume(val: float) -> void:
	master_volume = clampf(val, 0.0, 1.0)
	volume_changed.emit("Master", master_volume)

func set_music_volume(val: float) -> void:
	music_volume = clampf(val, 0.0, 1.0)
	volume_changed.emit("Music", music_volume)

func set_sfx_volume(val: float) -> void:
	sfx_volume = clampf(val, 0.0, 1.0)
	volume_changed.emit("SFX", sfx_volume)
