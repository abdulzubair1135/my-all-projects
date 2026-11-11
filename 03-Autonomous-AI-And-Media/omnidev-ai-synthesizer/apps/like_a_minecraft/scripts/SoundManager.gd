extends Node

# Procedural Sound Synthesizer for Godot 4
var sample_hz: float = 22050.0

func play_jump():
    play_tone(450.0, 750.0, 0.12)

func play_block_break():
    play_noise(0.15, 200.0)

func play_block_place():
    play_tone(220.0, 160.0, 0.08)

func play_tone(start_freq: float, end_freq: float, duration: float):
    var player = AudioStreamPlayer.new()
    add_child(player)
    var stream = AudioStreamGenerator.new()
    stream.mix_rate = sample_hz
    stream.buffer_length = duration
    player.stream = stream
    player.play()
    var playback = player.get_stream_playback()
    var total_frames = int(sample_hz * duration)
    for i in range(total_frames):
        var t = float(i) / sample_hz
        var freq = lerp(start_freq, end_freq, float(i) / total_frames)
        var phase = fmod(t * freq, 1.0)
        var sample = sin(phase * TAU) * (1.0 - float(i) / total_frames) * 0.4
        playback.push_frame(Vector2(sample, sample))
    await get_tree().create_timer(duration + 0.1).timeout
    player.queue_free()

func play_noise(duration: float, filter_cutoff: float):
    var player = AudioStreamPlayer.new()
    add_child(player)
    var stream = AudioStreamGenerator.new()
    stream.mix_rate = sample_hz
    stream.buffer_length = duration
    player.stream = stream
    player.play()
    var playback = player.get_stream_playback()
    var total_frames = int(sample_hz * duration)
    for i in range(total_frames):
        var sample = (randf() * 2.0 - 1.0) * (1.0 - float(i) / total_frames) * 0.3
        playback.push_frame(Vector2(sample, sample))
    await get_tree().create_timer(duration + 0.1).timeout
    player.queue_free()
