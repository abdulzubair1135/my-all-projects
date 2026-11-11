extends CharacterBody2D

var speed = 100
var current_dir = "down"

func _ready():
	$AnimatedSprite2D.play("front idle")


func _physics_process(delta):
	player_movement()
	move_and_slide()


func player_movement():
	var input_vector = Vector2.ZERO
	input_vector.x = Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left")
	input_vector.y = Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	
	if input_vector != Vector2.ZERO:
		input_vector = input_vector.normalized()
		velocity = input_vector * speed
		
		if abs(input_vector.x) > abs(input_vector.y):
			current_dir = "right" if input_vector.x > 0 else "left"
		else:
			current_dir = "down" if input_vector.y > 0 else "up"
	else:
		velocity = Vector2.ZERO
		
	play_anim()


func play_anim():

	var anim = $AnimatedSprite2D

	if velocity.length() == 0:

		if current_dir == "right":
			anim.play("right idel")

		elif current_dir == "left":
			anim.play("left idel")

		elif current_dir == "down":
			anim.play("front idle")

		elif current_dir == "up":
			anim.play("back idle")

	else:

		if current_dir == "right":
			anim.play("right run")

		elif current_dir == "left":
			anim.play("left run")

		elif current_dir == "down":
			anim.play("front run")

		elif current_dir == "up":
			anim.play("back run")
