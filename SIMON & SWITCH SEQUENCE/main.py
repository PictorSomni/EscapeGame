# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
import board
import os
from adafruit_debouncer import Debouncer
from digitalio import DigitalInOut, Direction, Pull
from audiopwmio import PWMAudioOut
from audiocore import WaveFile
import random

#############################################################
#                         VARIABLES                         #
#############################################################
TIMEOUT = 3
DURATION = 0.5
LENGTH = 6
ritual_sequence = [3, 1, 0, 4, 2]
rng_sequence = []
button_sequence = []
leds = []
buttons = []
audio_files = []
button_state = []
win = True
ritual = False

#############################################################
#                           SETUP                           #
#############################################################
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
    print("play_sequence")
    for index in rng_sequence :
        audio.play(audio_files[0])
        for __ in range(2) :
            leds[index].value = not leds[index].value
            time.sleep(DURATION)


def timeout_read() :
    print("timeout_read")
    start_time = time.monotonic()
    while time.monotonic() - start_time < TIMEOUT :
        for index, button in enumerate(buttons) :
            if not button.value :
                print(index)
                return index


def read_sequence(seq) :
    for val in seq :
        if timeout_read() != val :
            return False
        light_led(val, audio_files[0])
    return True


def generate_simon() :
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


#############################################################
#                         MAIN LOOP                         #
#############################################################
blink_increment()
time.sleep(1)

while ritual == False :

    if win == True : # DOESN'T UPDATE WHEN PLAYER PUSHES THE WRONG BUTTON
        generate_simon()

    play_sequence()
    if not read_sequence(rng_sequence) :
        audio.play(audio_files[4])
        time.sleep(TIMEOUT) 
        print("Game Over")
        win = False
        

    else :
        win = True
        print("+1")
        
        if len(rng_sequence) >= LENGTH :
            audio.play(audio_files[1])
            time.sleep(0.5)   
            blink_increment()
            print(rng_sequence)
            ritual = True

while True :
    for index, button in enumerate(buttons) :
        if not button.value :
            if not index in button_state :
                button_state.append(index)
                light_led(index, audio_files[0])
                print(index)
                if len(button_state) == len(ritual_sequence) :
                    if not button_state == ritual_sequence :
                        button_state = []
                        audio.play(audio_files[2])
                        print("Game Over")
                        time.sleep(5) 
                        
                    else :
                        print("Game finished")
                        audio.play(audio_files[3])
