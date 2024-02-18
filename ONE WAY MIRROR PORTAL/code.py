import time
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor
import adafruit_led_animation.color as lac
from adafruit_led_animation.animation import Sparkle, AnimationGroup, AnimationSequence

TRESHOLD = -40
LIMIT = -70
ANIMATION = False

### Configure the user switch of the Feather nRF52840
switch = DigitalInOut(board.SWITCH)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

### Configure the NeoPixel available on the Feather nRF52840
onboard = neopixel.NeoPixel(board.NEOPIXEL, 1)
onboard.brightness = 0
onboard[0] = (0, 0, 0)
STRIP_PIXEL_NUMBER = 44
# Setup for sparkle animation
SPARKLE_SPEED = 0.1  # Lower numbers increase the animation speed
# Create the NeoPixel strip
strip_pixels = neopixel.NeoPixel(board.D5, STRIP_PIXEL_NUMBER, auto_write=False)
strip_pixels.brightness = 0.1
strip_pixels.fill((0,0,0))
strip_pixels.show()

# animations = AnimationGroup(Sparkle(strip_pixels, SPARKLE_SPEED, lac.PURPLE))
animations = AnimationGroup(Sparkle(strip_pixels, SPARKLE_SPEED, lac.YELLOW))


ble = BLERadio()
advertisement = AdafruitColor()

# The color pickers will cycle through this list with buttons A and B.
color_options = [0x110000,
                 0x111100,
                 0x001100,
                 0x001111,
                 0x000011,
                 0x110011,
                 0x111111]

i = 0
### Trick to force a first color "change"
last_i = -1

print("Listening for color")

while ANIMATION == False :        
    for entry in ble.start_scan(AdafruitColor, timeout=5):
        color = entry.color

        if color == 0x000001 : 
            ANIMATION = True

    ble.stop_scan()

while True:
    animations.animate()

### The original code has two mode, the Feather nRF52840 version is broadcasts only.
# while True:
#     closest = None
#     closest_rssi = -80
#     closest_last_time = 0

# ### If the color has change, or if this is the first time, start advertising the color and set the onboard as feedback indicator.
#     if last_i != i:
#         last_i = i
#         color = color_options[i]
#         # onboard[0] = ( (color>>16)&0xFF , (color>>8)&0xFF , color&0xFF )
#         print("New color {:06x}".format(color))
#         advertisement.color = color
#         ble.stop_advertising()
#         ble.start_advertising(advertisement)
#         time.sleep(0.5)

# ### Verify if the user press the button (false if pressed) and change color.
#     if not switch.value:
#         i += 1
#         i %= len(color_options)

### We should never reach this point because of the infinit loop.
# ble.stop_advertising()