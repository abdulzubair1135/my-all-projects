def build_player_tscn():
    # anims: (name, row, count, speed, loop)
    anims = [
        ('idle_down', 0, 4, 5.0, True),
        ('idle_up', 1, 4, 5.0, True),
        ('idle_side', 2, 4, 5.0, True),
        ('walk_down', 3, 4, 8.0, True),
        ('walk_up', 4, 4, 8.0, True),
        ('walk_side', 5, 4, 8.0, True),
        ('attack_down', 6, 4, 16.0, False),
        ('attack_up', 7, 4, 16.0, False),
        ('attack_side', 8, 4, 16.0, False),
        ('heavy_down', 9, 4, 9.0, False),
        ('heavy_side', 10, 4, 9.0, False),
        ('dodge', 11, 4, 16.0, False),
        ('hurt', 12, 2, 8.0, False),
    ]

    atlas_subresources = []
    anim_defs = []

    for anim_name, row, count, speed, loop in anims:
        frame_refs = []
        for f in range(count):
            sub_id = f'Atlas_{anim_name}_{f}'
            x = f * 32
            y = row * 32
            atlas_subresources.append(
f'''[sub_resource type="AtlasTexture" id="{sub_id}"]
atlas = ExtResource("2_tex")
region = Rect2({x}, {y}, 32, 32)
'''
            )
            frame_refs.append(
f'''{{
"duration": 1.0,
"texture": SubResource("{sub_id}")
}}'''
            )
        frames_joined = ',\n'.join(frame_refs)
        anim_defs.append(
f'''{{
"frames": [
{frames_joined}
],
"loop": {str(loop).lower()},
"name": &"{anim_name}",
"speed": {speed}
}}'''
        )

    # Add death animation manually from row 12, frames 2 and 3
    for f in range(2):
        sub_id = f'Atlas_death_{f}'
        x = (f + 2) * 32
        y = 12 * 32
        atlas_subresources.append(
f'''[sub_resource type="AtlasTexture" id="{sub_id}"]
atlas = ExtResource("2_tex")
region = Rect2({x}, {y}, 32, 32)
'''
        )
    anim_defs.append(
'''{
"frames": [
{
"duration": 1.0,
"texture": SubResource("Atlas_death_0")
},
{
"duration": 1.0,
"texture": SubResource("Atlas_death_1")
}
],
"loop": false,
"name": &"death",
"speed": 3.0
}'''
    )

    total_sub = len(atlas_subresources) + 4
    load_steps = total_sub + 5

    content = f'''[gd_scene load_steps={load_steps} format=3]

[ext_resource type="Script" path="res://scripts/player/player.gd" id="1_script"]
[ext_resource type="Texture2D" path="res://assets/characters/player_placeholder.png" id="2_tex"]
[ext_resource type="Script" path="res://scripts/combat/CombatController.gd" id="3_combat"]
[ext_resource type="Script" path="res://scripts/combat/Hurtbox.gd" id="4_hurtbox"]
[ext_resource type="Script" path="res://scripts/combat/Hitbox.gd" id="5_hitbox"]

''' + '\n'.join(atlas_subresources) + f'''
[sub_resource type="SpriteFrames" id="SpriteFrames_player"]
animations = [
''' + ',\n'.join(anim_defs) + f'''
]

[sub_resource type="CapsuleShape2D" id="CapsuleShape2D_player"]
radius = 5.0
height = 14.0

[sub_resource type="CapsuleShape2D" id="CapsuleShape2D_hurtbox"]
radius = 6.0
height = 18.0

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hitbox"]
size = Vector2(24, 22)

[node name="Player" type="CharacterBody2D" groups=["player"]]
y_sort_enabled = true
collision_layer = 2
collision_mask = 1
script = ExtResource("1_script")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -14)
sprite_frames = SubResource("SpriteFrames_player")
animation = &"idle_down"
autoplay = "idle_down"

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, -2)
rotation = 1.5708
shape = SubResource("CapsuleShape2D_player")

[node name="Camera2D" type="Camera2D" parent="."]
zoom = Vector2(2, 2)
position_smoothing_enabled = true
position_smoothing_speed = 8.0

[node name="CombatController" type="Node" parent="." node_paths=PackedStringArray("character", "hitbox_pivot", "attack_hitbox", "character_hurtbox")]
script = ExtResource("3_combat")
character = NodePath("..")
hitbox_pivot = NodePath("../HitboxPivot")
attack_hitbox = NodePath("../HitboxPivot/Hitbox")
character_hurtbox = NodePath("../Hurtbox")

[node name="Hurtbox" type="Area2D" parent="." node_paths=PackedStringArray("owner_node")]
collision_layer = 32
collision_mask = 0
script = ExtResource("4_hurtbox")
owner_node = NodePath("..")

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
position = Vector2(0, -10)
shape = SubResource("CapsuleShape2D_hurtbox")

[node name="HitboxPivot" type="Node2D" parent="."]
position = Vector2(0, 10)

[node name="Hitbox" type="Area2D" parent="HitboxPivot" node_paths=PackedStringArray("owner_node")]
collision_layer = 8
collision_mask = 64
script = ExtResource("5_hitbox")
owner_node = NodePath("../..")

[node name="CollisionShape2D" type="CollisionShape2D" parent="HitboxPivot/Hitbox"]
shape = SubResource("RectangleShape2D_hitbox")
'''

    with open('scenes/player/player.tscn', 'w') as f:
        f.write(content)
    print('Generated expanded scenes/player/player.tscn successfully')

if __name__ == '__main__':
    build_player_tscn()
