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
# from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation import helper
from adafruit_led_animation.sequence import AnimationSequence
import adafruit_led_animation.color as color
from adafruit_motor import servo

#############################################################
#                          CONTENT                          #
#############################################################
# ---------------- Power ---------------- #
# provides power to the external components
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

# ---------------- Colors ---------------- #
COLORS = [color.BLUE, color.CYAN, color.GREEN, color.GOLD, color.AMBER, color.RED, color.PURPLE]
SPEED = 0.06
BRIGHTNESS = 0.2
index = 0
print(len(COLORS))

## EXTERNAL -->
num_pixels = 8
pixels = np.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)
pixels.brightness = 0.2

comet_v = Comet(pixels, speed=SPEED, color=COLORS[index], tail_length=8, bounce=True)
sparkle = Sparkle(pixels, speed=SPEED, color=COLORS[index], num_sparkles=3)

animations = AnimationSequence(comet_v, sparkle) #rainbow, rainbow_comet)
stop = False
current_sequence = 0

# ---------------- I2S AUDIO ---------------- #
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback
mixer.voice[0].level = 0.4

# # ---------------- I2C ---------------- #
# i2c = board.I2C()  # uses board.SCL and board.SDA

# qt_enc1 = seesaw.Seesaw(i2c, addr=0x36)
# qt_enc2 = seesaw.Seesaw(i2c, addr=0x39)

# qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
# button1 = digitalio.DigitalIO(qt_enc1, 24)
# button_held1 = False

# qt_enc2.pin_mode(24, qt_enc2.INPUT_PULLUP)
# button2 = digitalio.DigitalIO(qt_enc2, 24)
# button_held2 = False

# encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
# last_position1 = None

# encoder2 = rotaryio.IncrementalEncoder(qt_enc2)
# last_position2 = None

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
    # Scale a value from 0-65535 (AnalogIn range) to 0-255 (RGB range)
    # return int(value / 65535 * 255)
    return (value / 65535)

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    # ---------------- WAITING FOR ACTIVATION ---------------- #
    # while number_of_balls < 5:
    #     if not ball_button.value:
    #         number_of_balls += 1
    #         print(f"Number of balls = {number_of_balls}")
    #         sleep(1)
            
    animations.animate()
    # ---------------- POTENTIOMETERS ---------------- #
    pixels.brightness = 1 - scale(pot1.value)
    SPEED = scale(pot2.value / 10)
    index = int(scale(pot3.value * len(COLORS))) -1

    # # ---------------- ENCODERS ---------------- #
    # position1 = encoder1.position
    # position2 = encoder2.position

    # # ---------------- ENCODER 1 ---------------- #
    # if position1 != last_position1:
    #     try:
    #         if position1 > last_position1:
    #             SPEED -= 0.01
    #             if SPEED < 0:
    #                 SPEED = 0
    #         else:
    #             SPEED += 0.01

    #     except Exception :
    #         print(Exception)
    #     print(f" SPEED = {SPEED}")
    #     last_position1 = position1

    # # ---------------- BUTTON 1 ---------------- #
    # if not button1.value and not button_held1:
    #     button_held1 = True
    #     print("Button 1 pressed")

    #     pixels.brightness = 0.0
    #     pixels.show()
    #     sleep(0.1)
    #     mixer.voice[0].play(audiocore.WaveFile(open("Mad Donkey.wav","rb"))) 

    #     for new_angle in range(0, 100, 1):
    #         prop_servo.angle = new_angle
    #         sleep(0.01)                                                                                                                                                                                                                                                                                                                                                                                                       

    #     sleep(5)

    #     for new_angle in range(100, 0, -1):
    #         prop_servo.angle = new_angle
    #         sleep(0.01)  

    #     pixels.brightness = 0.2
    #     mixer.voice[0].stop()
                 
    # if button1.value and button_held1:
    #     button_held1 = False
    #     print("Button 1 released")
    #     print(prop_servo.angle)

    # # ---------------- ENCODER 2 ---------------- #
    # if position2 != last_position2:
    #     try:
    #         if position2 > last_position2:
    #             index += 1
    #             if index > len(COLORS) -1 :
    #                 index = 0
    #         else :
    #             index -= 1
    #             if index < 0 :
    #                 index = len(COLORS) -1
        
    #     except Exception :
    #         print(Exception)

    #     last_position2 = position2
    #     print(index)
    #     comet_v.color = COLORS[index]
    #     sparkle.color = COLORS[index]

    # # ---------------- BUTTON 2 ---------------- #
    # if not button2.value and not button_held2:
    #     button_held2 = True
    #     print(scale(pot1.value))
    #     current_sequence = not current_sequence
    #     animations.activate(current_sequence)

    # if button2.value and button_held2:
    #     button_held2 = False
    comet_v.color = COLORS[index]
    sparkle.color = COLORS[index]
    comet_v.speed = SPEED
    sparkle.speed = SPEED
    