extends Node

var sample_hz: float = 22050.0

func play_jump():
    play_tone(450.0, 750.0, 0.12)

func play_block_break():
    play_noise(0.15, 200.0)

func play_block_place():
    play_tone(220.0, 160.0, 0.08)

func play_footstep():
    play_noise(0.04, 100.0)

func play_hit():
    play_noise(0.1, 150.0)

func play_pickup():
    play_tone(600.0, 900.0, 0.06)

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

[gd_scene load_steps=6 format=3 uid="uid://mainscene01"]

[ext_resource type="Script" path="res://scripts/WorldGenerator.gd" id="1_world"]
[ext_resource type="Script" path="res://scripts/SoundManager.gd" id="2_sound"]
[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="3_player"]
[ext_resource type="PackedScene" path="res://scenes/UI.tscn" id="4_ui"]

[sub_resource type="Environment" id="Env_1"]
background_mode = 2
sky = SubResource("ProceduralSkyMaterial_sky")
ambient_light_source = 2
ambient_light_color = Color(0.05, 0.05, 0.1, 1)
ambient_light_energy = 0.4
tonemap_mode = 2

[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_sky"]
sky_top_color = Color(0.02, 0.02, 0.08, 1)
sky_horizon_color = Color(0.08, 0.08, 0.15, 1)
ground_bottom_color = Color(0.01, 0.01, 0.03, 1)
ground_horizon_color = Color(0.05, 0.05, 0.1, 1)

[node name="Main" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Env_1")

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866, -0.353, 0.353, 0, 0.707, 0.707, -0.5, -0.612, 0.612, 0, 20, 0)
shadow_enabled = true
light_energy = 0.5
light_color = Color(0.4, 0.5, 0.7, 1)

[node name="WorldGenerator" type="Node3D" parent="."]
script = ExtResource("1_world")

[node name="SoundManager" type="Node" parent="."]
script = ExtResource("2_sound")

[node name="Player" parent="." instance=ExtResource("3_player")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 15, 0)

[node name="UI" parent="." instance=ExtResource("4_ui")]
