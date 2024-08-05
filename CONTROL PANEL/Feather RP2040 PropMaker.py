#############################################################
#                          IMPORTS                          #
#############################################################
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
from time import sleep
import pwmio
from adafruit_motor import servo


#############################################################
#                         CONTENT                           #
#############################################################
BRB_ACTIVATE = False
SLOW = False
HIGH = False
SPEED_FACTOR = 1.0

#############################################################
#                          SETUP                            #
#############################################################
## ENABLE EXTERNAL POWER
external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True

## BUTTONS AND SWITCHES SETUP
buttons = []
button_pins = [board.D25,board.D24,board.A3, board.RX]
for button_pin in button_pins:
    tmp_btn_pin = DigitalInOut(button_pin)
    tmp_btn_pin.direction = Direction.INPUT
    tmp_btn_pin.pull = Pull.UP
    buttons.append([tmp_btn_pin, False])
print(buttons)

## BIG RED BUTTON LED SETUP
led = DigitalInOut(board.TX)
led.direction = Direction.OUTPUT

## JOYSTICK SETUP
joystick_y = AnalogIn(board.A0)
joystick_x = AnalogIn(board.A1)

## SERVO SETUP
PWM = pwmio.PWMOut(board.EXTERNAL_SERVO, frequency=50)
# Continuous Servo
# -----------------
SERVO = servo.ContinuousServo(PWM, min_pulse = 545, max_pulse = 2400)
SERVO.throttle = -0.03
sleep(0.1)
SERVO.throttle = 0
# -----------------

# 180 Servo
# -----------------
# SERVO = servo.Servo(PWM)
# SERVO.angle = 0
# -----------------

# pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
# pixel.brightness = 0

#############################################################
#                         FUNCTION                          #
#############################################################
# MAPS THE VALUES OF THE JOYSTICK TO DRIVE THE SERVO
def map_value(value, from_low = 0, from_high = 65535, to_low = 0.1, to_high = -0.1):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


#############################################################
#                           MAIN                            #
#############################################################
while True:
    led.value = BRB_ACTIVATE
    x = map_value(joystick_x.value)
    y = map_value(joystick_y.value)

    if y < -0.01 or y > 0.01:
        SERVO.throttle = y * SPEED_FACTOR
    else :
        SERVO.throttle = 0

    ## BLUE
    if not buttons[0][0].value and not buttons[0][1] :
        buttons[0][1] = True
        SPEED_FACTOR = 0.3
        print("Blue on")
        sleep(0.1)
    if buttons[0][0].value and buttons[0][1] :
        buttons[0][1] = False
        SPEED_FACTOR = 1.0
        print("Blue off")
        sleep(0.1)

    ## RED
    if not buttons[1][0].value and not buttons[1][1] :
        buttons[1][1] = True
        print("Red on")
        SPEED_FACTOR = 5.0
        sleep(0.1)
    if buttons[1][0].value and buttons[1][1] :
        buttons[1][1] = False
        SPEED_FACTOR = 1.0
        print("Red off")
        sleep(0.1)

    ## KEY
    if not buttons[2][0].value and not buttons[2][1] :
        buttons[2][1] = True
        BRB_ACTIVATE = True
        print("Key on")
        sleep(0.1)
    if buttons[2][0].value and buttons[2][1] :
        buttons[2][1] = False
        print("Key off")
        BRB_ACTIVATE = False
        sleep(0.1)

    ## BRB
    if not buttons[3][0].value and not buttons[3][1] :
        buttons[3][1] = True
        if BRB_ACTIVATE:
            if SPEED_FACTOR == 1:
                SPEED_FACTOR = 0
            else : SPEED_FACTOR = 1

        print("BRB on")
        sleep(0.1)
    if buttons[3][0].value and buttons[3][1] :
        buttons[3][1] = False
        print("BRB off")
        sleep(0.1)