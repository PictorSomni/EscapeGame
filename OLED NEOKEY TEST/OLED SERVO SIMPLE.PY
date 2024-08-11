# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
import board
import displayio
import terminalio
import digitalio
import neopixel
import rainbowio
from adafruit_display_text import label
import adafruit_displayio_sh1107
from adafruit_servokit import ServoKit

#############################################################
#                          CONSTANT                         #
#############################################################
DEFAULT_TEXT = "READY"
sequence = ["DUMMY", "SERVO", "CONTINUOUS"]
MAX = len(sequence) - 1
#############################################################
#                          FUNCTION                         #
#############################################################
def back_to_default ():
    text_area.scale = 2
    text_area.x = 36
    text_area.y = 30
    text_area.text = DEFAULT_TEXT
    speed(0)


def speed(val):
    kit.continuous_servo[7].throttle = val


#############################################################
#                          CONTENT                          #
#############################################################
## SERVO
kit = ServoKit(channels=8)
kit.continuous_servo[7].set_pulse_width_range(575, 2500)

## CLEARS
displayio.release_displays()

## SETUP BUTTON PINS
pin_b = digitalio.DigitalInOut(board.D6)
pin_b.direction = digitalio.Direction.INPUT
pin_b.pull = digitalio.Pull.UP

pin_c = digitalio.DigitalInOut(board.D5)
pin_c.direction = digitalio.Direction.INPUT
pin_c.pull = digitalio.Pull.UP


## NEOPIXELS
pixels = neopixel.NeoPixel(board.D9, 2, brightness=0.1)
pixels.fill((0, 0, 0))

## I2C
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

## SH1107 OLED DISPLAY
WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
group = displayio.Group()
display.show(group)

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

text = DEFAULT_TEXT
text_area = label.Label(terminalio.FONT)
back_to_default()
group.append(text_area)

## A BIT OF WAIT
time.sleep(0.5)

#############################################################
#                         MAIN LOOP                         #
#############################################################
counter = 0
while True :
    pixels.fill(rainbowio.colorwheel(int(time.monotonic() * 13) & 255))

################################################

    ## LEFT BUTTON PRESSED AND MAINTAINED
    while not pin_c.value: 
        pixels.fill((255, 0, 255))
        text_area.x = 42
        text_area.text = "DOWN"
        speed(0.07)

################################################

    ## RIGHT BUTTON PRESSED AND MAINTAINED
    while not pin_b.value: 
        pixels.fill((0, 85, 255))
        text_area.x = 54
        text_area.text = "UP"
        speed(-0.07)

################################################
        
    ## A little pause so both buttons presses (for delete) is read a lot better
    time.sleep(0.1)
    back_to_default ()
    display.show(group)
