# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
import board
import os
from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor
from audiopwmio import PWMAudioOut
from audiocore import WaveFile
import random

#############################################################
#                         VARIABLES                         #
#############################################################
TIMEOUT = 5
DURATION = 0.5
LENGTH = 6
ritual_sequence = [3, 1, 0, 4, 2]
rng_sequence = []
button_sequence = []
leds = []
buttons = []
audio_files = []
button_state = []
win = False
ritual = False
simon = True

to_send = [0x000000, 0x000001]

#############################################################
#                           SETUP                           #
#############################################################
## BLE
ble = BLERadio()
advertisement = AdafruitColor()

## SPEAKER SETUP
for file in sorted(os.listdir("audio")) :
    print(file)
    tmp_file = open(f"/audio/{file}", "rb")
    audio_files.append(WaveFile(tmp_file))

audio = PWMAudioOut(board.A0)  # Speaker

## LED SETUP
led_pins = (board.D12, board.D10, board.D6, board.SCL, board.D2, board.RX, board.MOSI, board.A5, board.A3, board.A1)
for led_pin in led_pins:
    tmp_led_pin = DigitalInOut(led_pin)
    tmp_led_pin.direction = Direction.OUTPUT
    tmp_led_pin.value = False
    leds.append(tmp_led_pin)

## BUTTONS AND SWITCHES SETUP
button_pins = (board.D11, board.D9, board.D5, board.SDA, board.TX, board.MISO, board.SCK, board.A4, board.A2, board.D13)
for button_pin in button_pins:
    tmp_btn_pin = DigitalInOut(button_pin)
    tmp_btn_pin.direction = Direction.INPUT
    tmp_btn_pin.pull = Pull.UP
    buttons.append(tmp_btn_pin)

#############################################################
#                          FUNCTION                         #
#############################################################
def light_led(index, audiofile):
    audio.play(audiofile)
    for __ in range(2) :
        leds[index].value = not leds[index].value
        time.sleep(DURATION)


def play_sequence() :
    for index in rng_sequence :
        audio.play(audio_files[0])
        for __ in range(2) :
            leds[index].value = not leds[index].value
            time.sleep(DURATION)


def timeout_read() :
    start_time = time.monotonic()
    while time.monotonic() - start_time < TIMEOUT :
        for index, button in enumerate(buttons) :
            if index in range(5, 10) :
                if not button.value :
                    return index


def read_sequence(seq) :
    for val in seq :
        if timeout_read() != val :
            return False
        light_led(val, audio_files[0])
    return True


def generate_simon() :
    rng = random.randrange(5, 10)

    if len(rng_sequence) == 0 :
        rng = random.randrange(5, 10)

    else :    
        while rng == rng_sequence[-1] :
            rng = random.randrange(5, 10)

    rng_sequence.append(rng)
    

def blink_increment() :
    for index in range(5, 10) :
        for _ in range(2) :
            leds[index].value = not leds[index].value
            time.sleep(0.1)

    for index in range(9, 4, -1) :
        for _ in range(2) :
            leds[index].value = not leds[index].value
            time.sleep(0.1)


def send(broadcast_color):
    advertisement.color = broadcast_color
    ble.start_advertising(advertisement)
    time.sleep(1)
    ble.stop_advertising()


#############################################################
#                         MAIN LOOP                         #
#############################################################
time.sleep(1)

while ritual == False :
    for index, button in enumerate(buttons) :
        if not button.value :
            if index in range(5) :
                if not index in button_state :
                    button_state.append(index)
                    light_led(index, audio_files[0])
                    print(index)
                    if len(button_state) == len(ritual_sequence) :
                        if not button_state == ritual_sequence :
                            button_state = []
                            audio.play(audio_files[2])
                            time.sleep(5) 
                            
                        else :
                            audio.play(audio_files[3])
                            blink_increment()
                            ritual = True
                            time.sleep(2)

while win == False :
    if simon == True : # DOESN'T UPDATE WHEN PLAYER PUSHES THE WRONG BUTTON
        generate_simon()

    play_sequence()
    if not read_sequence(rng_sequence) :
        audio.play(audio_files[4])
        time.sleep(TIMEOUT) 
        simon = False
        
    else :
        simon = True
        
        if len(rng_sequence) >= LENGTH :
            audio.play(audio_files[1])
            time.sleep(0.5)   
            blink_increment()
            print(rng_sequence)
            win = True
send(to_send[1])

            