from microbit import *
import music
import math

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

def training_start():
    show_training_mode(active_mode)
    while True:
        if button_a.was_pressed():
            change_training_mode()
            
        if button_b.was_pressed():
            toggle_training()
    
        sleep(100)
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
        display.scroll("Result:" + str(total_breaths))
        
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


if __name__ == "__main__":
    training_start()
    



        