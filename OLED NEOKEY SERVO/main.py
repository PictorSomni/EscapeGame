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

hall = analogio.AnalogIn(board.A0)

# ---------------- Neopixels ---------------- #
pixels = neopixel.NeoPixel(board.D9, 2, brightness=0.1)
pixels.fill((0, 0, 0))

uart = busio.UART(board.TX, board.RX, baudrate=9600)

# ---------------- I2C ---------------- #
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# ---------------- SH 1107 display ---------------- #
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

# ---------------- A bit of wait... ---------------- #
time.sleep(0.5)

#############################################################
#                         MAIN LOOP                         #
#############################################################
counter = 0
while True :
    while not vl53.data_ready:
        pass
    vl53.clear_interrupt()

    back_to_default(f"{vl53.distance} cm")
    
    pixels.fill(rainbowio.colorwheel(int(time.monotonic() * 13) & 255))  

    # ---------------- Hall sensor ---------------- #
    if hall.value < 30000 :
        text_area.x = 7
        text_area.text = "MAGNET ! "
        # print(f"HALL SENSOR : {hall.value}")

    # ---------------- Buttons ---------------- #
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
        back_to_default(f"{vl53.distance} cm")


################################################


    ## LEFT BUTTON PRESSED AND MAINTAINED
    if not button_c.value and not button_c_state: 
        pixels.fill((255, 0, 255))
        button_c_state = True
        text_area.x = 32
        text_area.text = "GAUCHE"
        while not button_c.value :
            if not button_b.value  :
                if counter < MAX :
                    counter += 1
                    text_area.x = 9
                    text_area.text = f"{sequence_gauche[counter]}"
                    time.sleep(0.2)


    ## LEFT BUTTON RELEASED
    if button_c.value and button_c_state:
        if counter > 0 :
            print(f"{sequence_gauche[counter]}")

        time.sleep(0.2)
        back_to_default(f"{vl53.distance} cm")
        button_c_state = False
        counter = 0


################################################


    ## RIGHT BUTTON PRESSED AND MAINTAINED
    if not button_b.value and not button_b_state: 
        pixels.fill((0, 85, 255))
        button_b_state = True
        text_area.x = 32
        text_area.text = "DROITE"
        while not button_b.value :

            if not button_c.value  :
                if counter < MAX :
                    counter += 1
                    text_area.x = 9
                    text_area.text = f"{sequence_droite[counter]}"
                    time.sleep(0.2)


    ## RIGHT BUTTON RELEASED
    if button_b.value and button_b_state:
        if counter > 0 :
            print(f"{sequence_droite[counter]}")

        time.sleep(0.2)
        back_to_default(f"{vl53.distance} cm")
        button_b_state = False
        counter = 0
        
    # ---------------- A bit of wait to better read button presses ---------------- #
    time.sleep(0.2)
    display.root_group = group
