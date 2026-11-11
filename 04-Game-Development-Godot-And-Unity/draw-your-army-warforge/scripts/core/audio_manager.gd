class_name AudioManagerNode
extends Node

# Procedural audio generator using AudioStreamGenerator & AudioStreamPlayer
var master_bus: AudioStreamPlayer
var sfx_bus: AudioStreamPlayer

func _ready() -> void:
	sfx_bus = AudioStreamPlayer.new()
	sfx_bus.name = "SFXPlayer"
	add_child(sfx_bus)

func play_sword_clash() -> void:
	_play_procedural_tone(380.0, 0.12, 0.4)

func play_arrow_shot() -> void:
	_play_procedural_tone(720.0, 0.08, 0.25)

func play_unit_death() -> void:
	_play_procedural_tone(150.0, 0.35, 0.5)

func play_button_click() -> void:
	_play_procedural_tone(880.0, 0.05, 0.2)

func play_victory_fanfare() -> void:
	_play_procedural_tone(523.25, 0.5, 0.6) # C5 chord root

func _play_procedural_tone(freq: float, duration: float, volume: float) -> void:
	var sample_rate = 22050
	var gen = AudioStreamGenerator.new()
	gen.mix_rate = sample_rate
	gen.buffer_length = duration + 0.05
	
	var player = AudioStreamPlayer.new()
	player.stream = gen
	player.volume_db = linear_to_db(volume * SettingsManager.sfx_volume * SettingsManager.master_volume)
	add_child(player)
	player.play()
	
	var playback = player.get_stream_playback() as AudioStreamGeneratorPlayback
	if playback:
		var frames = int(duration * sample_rate)
		for i in range(frames):
			var t = float(i) / float(sample_rate)
			# Envelope decay
			var env = max(0.0, 1.0 - (t / duration))
			var sample = sin(TAU * freq * t) * env
			playback.push_frame(Vector2(sample, sample))
			
	# Cleanup
	var tw = create_tween()
	tw.tween_interval(duration + 0.1)
	tw.tween_callback(player.queue_free)
