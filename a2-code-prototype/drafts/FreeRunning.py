from microbit import *
import music

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

def game_start():
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
        game_start()