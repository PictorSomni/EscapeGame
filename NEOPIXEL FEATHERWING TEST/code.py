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
from adafruit_seesaw import seesaw, rotaryio, digitalio, neopixel
# from adafruit_led_animation.animation.comet import Comet
# from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
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
SPEED = 0.05
index = 0

## NEOPIXEL FEATHERWING -->
# pixels = np.NeoPixel(board.D12, 32, brightness=0.1 , auto_write=False)
# pixels.fill((0, 0, 0))
# pixels.show()

# pixel_wing_vertical = helper.PixelMap.vertical_lines(pixels, 8, 4, helper.horizontal_strip_gridmap(8, alternating=False))
# comet_v = Comet(pixel_wing_vertical, speed=SPEED, color=COLORS[index], tail_length=6, bounce=True)
# sparkle = Sparkle(pixels, speed=SPEED, color=color.RED, num_sparkles=3)

## EXTERNAL -->
num_pixels = 32
pixels = np.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels)
pixels.brightness = 0.2

rainbow = Rainbow(pixels, speed=0.01, period=30)
rainbow_comet = RainbowComet(pixels, speed=0.01, tail_length=30, bounce=True)
# comet_v = Comet(pixels, speed=SPEED, color=COLORS[index], tail_length=6, bounce=True)
# sparkle = Sparkle(pixels, speed=SPEED, color=COLORS[index], num_sparkles=3)


animations = AnimationSequence(rainbow, rainbow_comet) #comet_v, sparkle)
stop = False
current_sequence = 0

# ---------------- I2S AUDIO ---------------- #
audio = audiobusio.I2SOut(board.I2S_BIT_CLOCK, board.I2S_WORD_SELECT, board.I2S_DATA)
mixer = audiomixer.Mixer(voice_count=1, sample_rate=22050, channel_count=1,
                         bits_per_sample=16, samples_signed=True)
audio.play(mixer) # attach mixer to audio playback
mixer.voice[0].level = 0.4

# ---------------- I2C ---------------- #
i2c = board.I2C()  # uses board.SCL and board.SDA

qt_enc1 = seesaw.Seesaw(i2c, addr=0x36)
qt_enc2 = seesaw.Seesaw(i2c, addr=0x39)

qt_enc1.pin_mode(24, qt_enc1.INPUT_PULLUP)
button1 = digitalio.DigitalIO(qt_enc1, 24)
button_held1 = False

qt_enc2.pin_mode(24, qt_enc2.INPUT_PULLUP)
button2 = digitalio.DigitalIO(qt_enc2, 24)
button_held2 = False

encoder1 = rotaryio.IncrementalEncoder(qt_enc1)
last_position1 = None

encoder2 = rotaryio.IncrementalEncoder(qt_enc2)
last_position2 = None

# pixel1 = neopixel.NeoPixel(qt_enc1, 6, 1)
# pixel1.brightness = 0.2
# pixel1.fill(0xff0000)

# pixel2 = neopixel.NeoPixel(qt_enc2, 6, 1)
# pixel2.brightness = 0.2
# pixel2.fill(0x0000ff)

# ---------------- SERVO ---------------- #
pwm = pwmio.PWMOut(board.EXTERNAL_SERVO, duty_cycle=2 ** 15, frequency=50)
prop_servo = servo.Servo(pwm)
# angle = 0
prop_servo.angle = 0

# ---------------- POTENTIOMETERS ---------------- #
pot1 = analogio.AnalogIn(board.A0)
# pin.deinit()


#############################################################
#                          FUNCTION                         #
#############################################################
def scale(value):
    # Scale a value from 0-65535 (AnalogIn range) to 0-255 (RGB range)
    return int(value / 65535 * 255)

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    animations.animate()
    # prop_servo.angle = angle
    position1 = encoder1.position
    position2 = encoder2.position

    if position1 != last_position1:
        try:
            if position1 > last_position1:
                index += 1
                if index == len(COLORS) :
                    index = 0
            else:
                index -= 1
                
                if index < 0 :
                    index = len(COLORS) - 1

        except Exception :
            print(Exception)

        last_position1 = position1
        # comet_v.color = COLORS[index]
        # sparkle.color = COLORS[index]

    ## BUTTON PRESS
    if not button1.value and not button_held1:
        button_held1 = True
        print("Button 1 pressed")

        pixels.brightness = 0.0
        pixels.show()
        sleep(0.1)
        mixer.voice[0].play(audiocore.WaveFile(open("Mad Donkey.wav","rb"))) 

        for new_angle in range(0, 100, 1):
            prop_servo.angle = new_angle
            sleep(0.01)                                                                                                                                                                                                                                                                                                                                                                                                       

        sleep(5)

        for new_angle in range(100, 0, -1):
            prop_servo.angle = new_angle
            sleep(0.01)  

        pixels.brightness = 0.2
        # animations.activate(0)
        mixer.voice[0].stop()
                 
    if button1.value and button_held1:
        button_held1 = False
        print("Button 1 released")
        print(prop_servo.angle)

    if position2 != last_position2:
        try:
            # if position2 > last_position2:
            #     SPEED += 0.01
            # else :
            #     SPEED -= 0.01
            #     if SPEED < 0:
            #         SPEED = 0

            if position2 > last_position2:
                pixels.brightness += 0.05
            else :
                pixels.brightness -= 0.05
                if pixels.brightness < 0:
                    pixels.brightness = 0
        
        except Exception :
            print(Exception)

        # print(SPEED)
        last_position2 = position2

    if not button2.value and not button_held2:
        button_held2 = True
        # pixel2.brightness = 0.5
        print(scale(pot1.value))
        current_sequence = not current_sequence
        animations.activate(current_sequence)

    if button2.value and button_held2:
        button_held2 = False
        # pixel2.brightness = 0.2

    # comet_v.speed = SPEED