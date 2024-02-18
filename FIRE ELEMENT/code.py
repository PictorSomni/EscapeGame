# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
from adafruit_circuitplayground.bluefruit import cpb
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.color import AMBER
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor


#############################################################
#                         VARIABLES                         #
#############################################################
MAX_BRIGHTNESS = 0.3
POWER = 0.01
TO_SEND = 0x000001

#############################################################
#                           SETUP                           #
#############################################################
## BLE
ble = BLERadio()
advertisement = AdafruitColor()

## NEOPIXELS
cpb.pixels.brightness = 0
sparkle = Sparkle(cpb.pixels, speed=0.05, color=AMBER, num_sparkles=10)

#############################################################
#                          FUNCTION                         #
#############################################################
def send(broadcast_color):
    advertisement.color = broadcast_color
    ble.start_advertising(advertisement)
    time.sleep(1)
    ble.stop_advertising()

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    sparkle.animate()
    
    if cpb.loud_sound(sound_threshold=2000):
        if cpb.pixels.brightness < MAX_BRIGHTNESS :
            cpb.pixels.brightness += POWER
        else :
            print("BROADCASTING")
            send(TO_SEND)
    else:
        cpb.pixels.brightness -= POWER
        time.sleep(0.05)