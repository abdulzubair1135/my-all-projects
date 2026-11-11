def make_zombie_tscn(scene_path, script_res, tex_res, node_name, hitbox_size=(22, 22), anim_speeds=(4.0, 6.0, 10.0, 12.0, 4.0)):
    anims = [
        ('idle', 0, 4, anim_speeds[0], True),
        ('walk', 1, 4, anim_speeds[1], True),
        ('attack', 2, 4, anim_speeds[2], False),
        ('hurt', 3, 4, anim_speeds[3], False),
        ('death', 4, 4, anim_speeds[4], False),
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

    total_sub = len(atlas_subresources) + 4
    load_steps = total_sub + 4

    content = f'''[gd_scene load_steps={load_steps} format=3]

[ext_resource type="Script" path="{script_res}" id="1_script"]
[ext_resource type="Texture2D" path="{tex_res}" id="2_tex"]
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
size = Vector2({hitbox_size[0]}, {hitbox_size[1]})

[node name="{node_name}" type="CharacterBody2D" groups=["enemies"]]
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

    with open(scene_path, 'w') as f:
        f.write(content)
    print(f'Generated {scene_path}')

def generate_all():
    # 1. Walker Zombie
    make_zombie_tscn(
        'scenes/enemies/walker_zombie.tscn',
        'res://scripts/enemies/walker_zombie.gd',
        'res://assets/enemies/zombie_training.png',
        'WalkerZombie',
        hitbox_size=(22, 22),
        anim_speeds=(3.5, 5.0, 9.0, 12.0, 3.5)
    )

    # 2. Runner Zombie
    make_zombie_tscn(
        'scenes/enemies/runner_zombie.tscn',
        'res://scripts/enemies/runner_zombie.gd',
        'res://assets/enemies/zombie_runner.png',
        'RunnerZombie',
        hitbox_size=(24, 22),
        anim_speeds=(5.0, 9.0, 14.0, 14.0, 5.0)
    )

    # 3. Royal Guard Zombie (wider sword hitbox)
    make_zombie_tscn(
        'scenes/enemies/royal_zombie.tscn',
        'res://scripts/enemies/royal_zombie.gd',
        'res://assets/enemies/zombie_royal.png',
        'RoyalZombie',
        hitbox_size=(32, 26),
        anim_speeds=(3.0, 4.5, 8.0, 10.0, 3.0)
    )

if __name__ == '__main__':
    generate_all()
