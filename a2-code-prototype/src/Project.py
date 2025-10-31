from microbit import *
import music

pattern = "TRAINING"

# Breath training modes configuration
TRAINING_MODES = {
    1: ("NORAML",4000,4000),
    2: ("RELAX",4000,6000),
    3: ("FOCUS",6000,4000)
}
active_mode = 1
is_training = False
total_breaths = 0

SOUND_THRESHOLD = 100

# Heart shape position
HEART = [
    [0, 1, 0, 1, 0],
    [1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 0, 1, 0, 0]
]

# Free running game configuration
mario_x = 1   # Player initial position x
mario_y = 3   # Player initial position y
obstacles = []
is_jumping = False
jump_velocity = -0.005

sound_jump = False
check_sound_interval = 100  # Sound detect interval
sound_level = 0      # Current sound level
last_sound_check = 0

create_interval = 4000 # create obstacel interval
last_create_time = 0
game_score = 0

game_active = False


"""
Breath training functions
"""
def training_start():
    global pattern
    show_training_mode(active_mode)
    while True:
        if button_a.was_pressed() and not is_training:
            change_training_mode()
            
        if button_b.was_pressed():
            toggle_training()

        if pin_logo.is_touched():
            pattern = "GAME"
            break

def show_training_mode(modeIndex):
    display.show(modeIndex)

def change_training_mode():
    global active_mode
    if not is_training:
        active_mode = active_mode % 3 + 1
        show_training_mode(active_mode)

# Toggle training on or off with button b
def toggle_training():
    global is_training,training_score, total_breaths

    if not is_training:
        is_training = True
        total_breaths = 0
        display.clear()

        modename,inhale_time,exhale_time = TRAINING_MODES[active_mode]
        display.scroll(modename + "GO!", delay=80)
        breath_training(inhale_time, exhale_time)

    else:
        is_training = False
        music.play(["C5", "G4"])
        #display.clear()
        display.scroll("SCORE:" + str(total_breaths))
        
        show_training_mode(active_mode)

def breath_training(inhale_time, exhale_time):
    global training_score, total_breaths, good_breaths
    total_breath = 0
    breath_phase = "inhale"
    breath_start_time = running_time()

    while is_training:
        phase_time = running_time() - breath_start_time
        if breath_phase == "inhale":
            target_time = inhale_time 
            if running_time() - breath_start_time >= target_time:
                music.pitch(800, 50)
                breath_phase = "exhale"
                breath_start_time = running_time()
        else:
            target_time = exhale_time
            if running_time() - breath_start_time >= target_time:
                music.pitch(800, 50)
                breath_phase = "inhale"
                breath_start_time = running_time()
                total_breaths += 1

        percent = phase_time/target_time
        breathing_guide(breath_phase,percent)

        if button_b.was_pressed():
            toggle_training()

        if not is_training:
            break
def breathing_guide(phase,percent):
    if phase == "inhale":
        brightness = int(percent * 9)
    else:
        brightness = int((1 - percent) * 9)

    display.show(create_heart_shape(brightness)) 

# Create heart shape with brightness
def create_heart_shape(brightness):
    global HEART
    heart_bytes = []
    for row in HEART:
        for position in row:
            if position:
                heart_bytes.append(brightness)
            else:
                heart_bytes.append(0)
    return Image(5,5,bytearray(heart_bytes))

"""
Free running game functions
"""
def game_start():
    global pattern
    global mario_x, mario_y, game_active, is_jumping
    global obstacles, last_create_time, game_score
    mario_x = 1
    mario_y = 3
    
    game_active = True
    is_jumping = False
    obstacles = []
    last_create_time = 0
    game_score = 0

    display.scroll("FREE RUNNING!")
    
    while True:
        if button_b.was_pressed() and game_active:            
            music.play(music.JUMP_UP)
            game_running()

        if pin_logo.is_touched():
            pattern = "TRAINING"
            break
             
        if not game_active:
            break


def game_running():
    global mario_x, mario_y, is_jumping, jump_velocity
    global obstacles, last_create_time, game_score
    global last_sound_check
    if not game_active:
        return

    while game_active:
        current_time = running_time()
    
        # Detect microphone sound jump
        if sound_jump:
            if current_time - last_sound_check >= check_sound_interval:
                last_sound_check = current_time
                sound_level = microphone.sound_level()
                if sound_level > 100 and not is_jumping:
                    jump_velocity = -0.005
                    is_jumping = True
    
        # press button_a to jump
        if button_a.was_pressed() and not is_jumping:
            jump_velocity = -0.005
            is_jumping = True
    
        if is_jumping:
            mario_y += jump_velocity
            if mario_y >= 3:
                mario_y = 3
                jump_velocity = -0.005
                is_jumping = False
            elif mario_y <= 0:
                mario_y = 0
                jump_velocity = 0.005
    
        # Create new obstacle
        if current_time - last_create_time > create_interval:
            obstacles.append(4)
            game_score += 1
            last_create_time = current_time
        
        # move obstacle
        for i in range(len(obstacles)):
            obstacles[i] -= 0.002
    
        # Check touched 
        for dot in obstacles:
            obstacle_x = int(dot)
            if obstacle_x == mario_x and mario_y >=2:
                game_score -=1
                game_over()
                return
                
        game_display()
    

def game_display():
    # Initial create blank image
    game_img = Image("00000:00000:00000:00000:00000")

    # Draw player mario (two pixels)
    mario_row = int(mario_y)
    if mario_row < 4:  #Ensure out of bounds
        game_img.set_pixel(mario_x, mario_row, 9)
        game_img.set_pixel(mario_x, mario_row+1, 9)
    else:
        game_img.set_pixel(mario_x, mario_row, 9)
    
    # Draw obstacles
    for dot in obstacles:
        obstacle_x = int (dot)
        if 0 <= obstacle_x <=4:
            game_img.set_pixel(obstacle_x, 4, 9) # obstacle y=4 means at bottom
            
    display.show(game_img)

def game_over():
    global game_active
    game_active = False 
    music.play(music.BADDY)
    display.scroll("SCORE:" + str(game_score))


if __name__ == "__main__":
    while True:                
        if pattern == "TRAINING":
            display.scroll("TRAINING")
            training_start()
        else:
            display.scroll("GAME")
            game_start()