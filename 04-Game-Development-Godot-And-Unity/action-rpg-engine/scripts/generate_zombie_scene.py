def build_zombie_tscn():
    anims = [
        ('idle', 0, 4, 4.0, True),
        ('walk', 1, 4, 6.0, True),
        ('attack', 2, 4, 10.0, False),
        ('hurt', 3, 4, 12.0, False),
        ('death', 4, 4, 4.0, False),
    ]

    atlas_subresources = []
    anim_defs = []

    for anim_name, row, count, speed, loop in anims:
        frame_refs = []
        for f in range(count):
            sub_id = f'Atlas_zombie_{anim_name}_{f}'
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

    total_sub = len(atlas_subresources) + 4
    load_steps = total_sub + 4

    content = f'''[gd_scene load_steps={load_steps} format=3]

[ext_resource type="Script" path="res://scripts/enemies/training_zombie.gd" id="1_script"]
[ext_resource type="Texture2D" path="res://assets/enemies/zombie_training.png" id="2_tex"]
[ext_resource type="Script" path="res://scripts/combat/Hurtbox.gd" id="3_hurtbox"]
[ext_resource type="Script" path="res://scripts/combat/Hitbox.gd" id="4_hitbox"]

''' + '\n'.join(atlas_subresources) + f'''
[sub_resource type="SpriteFrames" id="SpriteFrames_zombie"]
animations = [
''' + ',\n'.join(anim_defs) + f'''
]

[sub_resource type="CapsuleShape2D" id="CapsuleShape2D_zombie"]
radius = 5.0
height = 14.0

[sub_resource type="CapsuleShape2D" id="CapsuleShape2D_hurtbox"]
radius = 7.0
height = 20.0

[sub_resource type="RectangleShape2D" id="RectangleShape2D_claw"]
size = Vector2(22, 22)

[node name="TrainingZombie" type="CharacterBody2D" groups=["enemies"]]
y_sort_enabled = true
collision_layer = 4
collision_mask = 7
script = ExtResource("1_script")

[node name="AnimatedSprite2D" type="AnimatedSprite2D" parent="."]
position = Vector2(0, -14)
sprite_frames = SubResource("SpriteFrames_zombie")
animation = &"idle"
autoplay = "idle"

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, -2)
rotation = 1.5708
shape = SubResource("CapsuleShape2D_zombie")

[node name="Hurtbox" type="Area2D" parent="." node_paths=PackedStringArray("owner_node")]
collision_layer = 64
collision_mask = 0
script = ExtResource("3_hurtbox")
owner_node = NodePath("..")

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
position = Vector2(0, -10)
shape = SubResource("CapsuleShape2D_hurtbox")

[node name="AttackHitbox" type="Area2D" parent="." node_paths=PackedStringArray("owner_node")]
collision_layer = 16
collision_mask = 32
script = ExtResource("4_hitbox")
owner_node = NodePath("..")

[node name="CollisionShape2D" type="CollisionShape2D" parent="AttackHitbox"]
position = Vector2(0, -6)
shape = SubResource("RectangleShape2D_claw")
'''

    with open('scenes/enemies/training_zombie.tscn', 'w') as f:
        f.write(content)
    print('Generated scenes/enemies/training_zombie.tscn successfully')

if __name__ == '__main__':
    build_zombie_tscn()
