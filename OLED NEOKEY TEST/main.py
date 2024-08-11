                                                                                     # -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
import board
import busio
import displayio
import terminalio
import digitalio
import analogio
import rotaryio
import neopixel
import rainbowio
from adafruit_display_text import label
import adafruit_displayio_sh1107
import adafruit_vl53l4cd

#############################################################
#                          CONSTANT                         #
#############################################################
DEFAULT_TEXT = "READY"
sequence_gauche = ["DUMMY", "Commande 1", "Commande 2", "Commande 3", "Commande 4"]
sequence_droite = ["DUMMY", "Commande 5", "Commande 6", "Commande 7", "Commande 8"]
MAX = len(sequence_gauche) - 1
#############################################################
#                          FUNCTION                         #
#############################################################
def back_to_default (text):
    text_area.scale = 2
    text_area.x = 21
    text_area.y = 30
    text_area.text = text


#############################################################
#                          CONTENT                          #
#############################################################
## CLEARS
displayio.release_displays()

# ---------------- Buttons ---------------- #
button_b = digitalio.DigitalInOut(board.D6)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.UP

button_c = digitalio.DigitalInOut(board.D5)
button_c.direction = digitalio.Direction.INPUT
button_c.pull = digitalio.Pull.UP

button_b_state = False
button_c_state = False
buttons_state = False
sensor = True

hall = analogio.AnalogIn(board.A0)

# ---------------- Neopixels ---------------- #
pixels = neopixel.NeoPixel(board.D9, 2, brightness=0.1)
pixels.fill((0, 0, 0))

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# ---------------- I2C ---------------- #
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# ---------------- SH1107 OLED display ---------------- #
WIDTH = 128
HEIGHT = 64

display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)

group = displayio.Group()
display.root_group = group

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White


text_area = label.Label(terminalio.FONT)
back_to_default(DEFAULT_TEXT)
group.append(text_area)

# ---------------- Encoder ---------------- #
encoder = rotaryio.IncrementalEncoder(board.MISO, board.D4)
last_position = 0

# ---------------- VL53 Time of flight ---------------- #
vl53 = adafruit_vl53l4cd.VL53L4CD(i2c)

# OPTIONAL: can set non-default values
# vl53.inter_measurement = 0
# vl53.timing_budget = 200

print("VL53L4CD Simple Test.")
print("--------------------")
model_id, module_type = vl53.model_info
print("Model ID: 0x{:0X}".format(model_id))
print("Module Type: 0x{:0X}".format(module_type))
print("Timing Budget: {}".format(vl53.timing_budget))
print("Inter-Measurement: {}".format(vl53.inter_measurement))
print("--------------------")

vl53.start_ranging()

# ---------------- A bit of wait ---------------- #
time.sleep(0.5)

#############################################################
#                         MAIN LOOP                         #
#############################################################
counter = 0
while True :
    while not vl53.data_ready:
        pass
    vl53.clear_interrupt()

    if sensor == True :
        back_to_default(f"{vl53.distance} cm")
    else:
        back_to_default(f"Turn {position}")
    
    pixels.fill(rainbowio.colorwheel(int(time.monotonic() * 13) & 255))  

    ## ENCODER POSITION
    position = encoder.position
    # if position != last_position:
    #     text_area.text = f"Turn: {position}"

    ## HALL SENSOR
    if hall.value < 30000 :
        text_area.x = 7
        text_area.text = "MAGNET ! "

    ## BOTH BUTTONS PRESSED
    if not button_b.value and not button_c.value :
        buttons_state = True
        while not button_b.value and not button_c.value :
            pixels.fill((255, 0, 0))
            text_area.x = 7
            text_area.text = "-< H@CK >-"


    ## BOTH BUTTONS RELEASED
    if button_b.value and button_c.value and buttons_state : 
        buttons_state = False
        print("LES 2")


################################################


    ## LEFT BUTTON PRESSED AND MAINTAINED
    if not button_c.value and not button_c_state: 
        pixels.fill((255, 0, 255))
        button_c_state = True

    ## LEFT BUTTON RELEASED
    if button_c.value and button_c_state:
        time.sleep(0.2)
        sensor = True
        button_c_state = False


################################################


    ## RIGHT BUTTON PRESSED AND MAINTAINED
    if not button_b.value and not button_b_state: 
        pixels.fill((0, 85, 255))
        button_b_state = True

    ## RIGHT BUTTON RELEASED
    if button_b.value and button_b_state:
        time.sleep(0.2)
        sensor = False
        button_b_state = False

    last_position = position
    display.root_group = group
