#############################################################
#                          IMPORTS                          #
#############################################################
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
from time import sleep
from adafruit_servokit import ServoKit

#############################################################
#                         CONTENT                           #
#############################################################
BRB_ACTIVATE = False
SLOW = False
HIGH = False
SPEED_FACTOR = 1.0
SPEED_BLOCK = False

#############################################################
#                          SETUP                            #
#############################################################
## BUTTONS AND SWITCHES SETUP
buttons = []
button_pins = [board.A5, board.A4, board.A3, board.RX]
for button_pin in button_pins:
    tmp_btn_pin = DigitalInOut(button_pin)
    tmp_btn_pin.direction = Direction.INPUT
    tmp_btn_pin.pull = Pull.UP
    buttons.append([tmp_btn_pin, False])

## BIG RED BUTTON LED SETUP
led = DigitalInOut(board.TX)
led.direction = Direction.OUTPUT

## JOYSTICK SETUP
joystick_y = AnalogIn(board.A0)
joystick_x = AnalogIn(board.A1)

## SERVO SETUP
SERVO = ServoKit(channels=8)
SERVO.continuous_servo[7].set_pulse_width_range(560, 2500)

#############################################################
#                         FUNCTION                          #
#############################################################
# MAPS THE VALUES OF THE JOYSTICK TO DRIVE THE SERVO
def map_value(value, from_low = 0, from_high = 65535, to_low = 0.1, to_high = -0.1):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

def run() :
    print(f"Speed factor : {SPEED_FACTOR}")
    sleep(0.1)

#############################################################
#                           MAIN                            #
#############################################################
sleep(0.1)

while True:
    led.value = BRB_ACTIVATE
    x = map_value(joystick_x.value)
    y = map_value(joystick_y.value)

    if y < -0.01 or y > 0.01:
        SERVO.continuous_servo[7].throttle = y * SPEED_FACTOR
    else :
        SERVO.continuous_servo[7].throttle = 0

    ## BLUE
    if not buttons[0][0].value and not buttons[0][1] :
        buttons[0][1] = True
        if not SPEED_BLOCK:
            SPEED_FACTOR = 0.3
        run()
    if buttons[0][0].value and buttons[0][1] :
        buttons[0][1] = False
        if not SPEED_BLOCK:
            SPEED_FACTOR = 1.0
        run()

    ## RED
    if not buttons[1][0].value and not buttons[1][1] :
        buttons[1][1] = True
        if not SPEED_BLOCK:
            SPEED_FACTOR = 5.0
        run()
    if buttons[1][0].value and buttons[1][1] :
        buttons[1][1] = False
        if not SPEED_BLOCK:
            SPEED_FACTOR = 1.0
        run()
    ## KEY
    if not buttons[2][0].value and not buttons[2][1] :
        buttons[2][1] = True
        BRB_ACTIVATE = True
        print("Key on")
        
    if buttons[2][0].value and buttons[2][1] :
        buttons[2][1] = False
        print("Key off")
        BRB_ACTIVATE = False

    ## BRB
    if not buttons[3][0].value and not buttons[3][1] :
        buttons[3][1] = True
        if BRB_ACTIVATE:
            if SPEED_FACTOR == 1:
                SPEED_FACTOR = 0
                SPEED_BLOCK = True
            else :
                SPEED_FACTOR = 1
                SPEED_BLOCK = False

        run()
    if buttons[3][0].value and buttons[3][1] :
        buttons[3][1] = False
        sleep(0.1)    
