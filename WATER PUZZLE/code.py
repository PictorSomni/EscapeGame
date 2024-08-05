#############################################################
#                          IMPORTS                          #
#############################################################
from time import sleep
import board
import neopixel as np
import audiocore
import audiobusio
import audiomixer
import pwmio
import analogio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.sequence import AnimationSequence
from adafruit_motor import servo
from rainbowio import colorwheel

#############################################################
#                          CONTENT                          #
#############################################################
# ---------------- Power ---------------- #
# provides power to the external components
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# ---------------- Colors ---------------- #
SPEED = 0.1
POT1_OK = False
POT2_OK = False
POT3_OK = False
# ALERT = False
index = 0

## EXTERNAL -->
num_pixels = 8
pixels = np.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)
pixels.brightness = 0.2

comet_v = Comet(pixels, speed=0.1, color=(0,0,0), tail_length=8)
pulse = Pulse(pixels, speed=0.1, color=(255, 255, 255), period=3)
rainbow_comet = RainbowComet(pixels, speed=0.05, tail_length=13)

animations = AnimationSequence(comet_v, pulse, rainbow_comet)
current_sequence = 0

# ---------------- I2S AUDIO ---------------- #
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback
mixer.voice[0].level = 0.3

# ---------------- SERVO ---------------- #
pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2 ** 15, frequency=50)
prop_servo = servo.Servo(pwm)
prop_servo.angle = 0

# ---------------- POTENTIOMETERS ---------------- #
pot1 = analogio.AnalogIn(board.A0)
pot2 = analogio.AnalogIn(board.A1)
pot3 = analogio.AnalogIn(board.A2)
# pin.deinit()

# ---------------- BALL BUTTON ---------------- #
ball_button = DigitalInOut(board.D4)
ball_button.switch_to_input(pull=Pull.UP)
number_of_balls = 0
#############################################################
#                          FUNCTION                         #
#############################################################
def scale(value):
    # Scale a value from 0-65535 (AnalogIn range) to 0.0-1.0
    return (value / 65535)


def map_value(value, from_low = 0, from_high = 65535, to_low = 0, to_high = 255):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    # ---------------- WAITING FOR ACTIVATION ---------------- #
    while number_of_balls < 5:
        if not ball_button.value:
            number_of_balls += 1
            print(f"Number of balls = {number_of_balls}")
            sleep(1)

    animations.animate()
    # print(f"1 : {pot1.value} - 2 : {pot2.value} - 3 : {pot3.value}")

    # ---------------- POTENTIOMETERS ---------------- #
    # >>> POT 1 >>>
    if pot1.value > 40000:
        index = int(map_value(pot1.value, 40000, 65535, 75, 0))
        POT1_OK = False
        # ALERT = False
    elif pot1.value < 25000:
        index = int(map_value(pot1.value, 0, 25000, 164, 75))
        POT1_OK = False
        # ALERT = False
    else :
        index = 75
        # if ALERT == False:
        #     mixer.voice[0].play(audiocore.WaveFile(open("mgs_alert.wav","rb")))
        #     ALERT = True
        
        POT1_OK = True

    comet_v.color = colorwheel(index)
    pulse.color = colorwheel(index)
    comet_v.speed = SPEED
    pulse.speed = SPEED

    # >>> POT 2 >>>
    SPEED = map_value(pot2.value, 65535, 0, 0.005, 0.05)
    if 55000 > pot2.value > 45000:
        animations.activate(1)
        POT2_OK = True
    else:
        animations.activate(0)
        POT2_OK = False

    # >>> POT 3 >>>    
    pixels.brightness = map_value(pot3.value, 0, 65535, 0.05, 1.0)
    if 26000 > pot3.value > 20000:
        if POT1_OK and POT2_OK:
                       

            if POT3_OK == False:
                mixer.voice[0].play(audiocore.WaveFile(open("Mad Donkey.wav","rb"))) 
                for new_angle in range(0, 100, 1):
                    prop_servo.angle = new_angle
                    sleep(0.01)                                                                                                                                                                                                                                                                                                                                                                                    
                sleep(5)
                mixer.voice[0].stop()
                POT3_OK = True

    if POT3_OK == True:
        pixels.brightness = 0.5 
        animations.activate(2)

        if pot1.value < 500 and pot2.value < 500 and pot3.value < 500:
            print("END")
            for new_angle in range(100, 0, -1):
                    prop_servo.angle = new_angle
                    sleep(0.01) 

            pixels.brightness = 0.0
            external_power.value = False
            break

