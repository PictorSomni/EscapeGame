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
SPEED_FACTOR = 0.0
SPEED_BLOCK = True

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
joystick_z = AnalogIn(board.A2)

## SERVO SETUP
SERVO = ServoKit(channels=8)
SERVO.continuous_servo[7].set_pulse_width_range(560, 2500)

#############################################################
#                         FUNCTION                          #
#############################################################
## MAPS THE VALUES OF THE JOYSTICK TO DRIVE THE SERVO
def map_value(value, from_low = 0, from_high = 65535, to_low = 0.1, to_high = -0.1):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


def run() :
    print(f"Speed factor : {SPEED_FACTOR}")
    sleep(0.1)


def clamp(minimum, x, maximum):
    print("#" * 32)
    value = max(minimum, min(x, maximum))
    print(value)
    return value
    

#############################################################
#                           MAIN                            #
#############################################################
sleep(0.1)

while True:
    # ---------------- KEY SWITCH ---------------- #
    if not buttons[2][0].value and not buttons[2][1] :
        buttons[2][1] = True
        BRB_ACTIVATE = True
        led.value = True
        print("Key on")
        
    if buttons[2][0].value and buttons[2][1] :
        buttons[2][1] = False
        BRB_ACTIVATE = False
        led.value = False
        print("Key off")

    if BRB_ACTIVATE:
        # ---------------- X-AXIS JOYSTICK ---------------- # 
        x = map_value(joystick_x.value, 0, 2**15, 0, 90)
        if x < 88 or x > 92:
            SERVO.servo[1].angle = x
        else : 
            SERVO.servo[1].angle = 90


        # ---------------- Y-AXIS JOYSTICK ---------------- # 
        y = map_value(joystick_y.value, 0, 2**15, 0, 90)
        if y < 88 or y > 92:
            SERVO.servo[0].angle = y
        else :
            SERVO.servo[0].angle = 90        
        

        # ---------------- Z-AXIS JOYSTICK ---------------- # 
        ## HACK TO MAKE IT WORK
        negative_z = map_value(joystick_z.value, 50, 2200, 0.1, 0)
        positive_z = map_value(joystick_z.value, 2500, 2**15, 0, -0.07)

        ## Going down
        if joystick_z.value < 2000:
            z_speed = negative_z * SPEED_FACTOR
            SERVO.continuous_servo[7].throttle = z_speed
        ## Going up
        elif joystick_z.value > 3000:
            z_speed = positive_z * SPEED_FACTOR
            SERVO.continuous_servo[7].throttle = z_speed
        else:
            SERVO.continuous_servo[7].throttle = 0


        # ---------------- BLUE BUTTON ---------------- # 
        if not buttons[0][0].value and not buttons[0][1] :
            buttons[0][1] = True
            print("BLUE")
            while not buttons[0][0].value :
                xc = map_value(joystick_x.value, 50, 50000, -0.3, 0.24)
                yc = map_value(joystick_y.value, 50, 50000, -0.3, 0.3)

                SERVO.continuous_servo[2].throttle = xc
                SERVO.continuous_servo[3].throttle = yc
            run()

        if buttons[0][0].value and buttons[0][1] :
            buttons[0][1] = False
            if not SPEED_BLOCK:
                SPEED_FACTOR = 2.0
            run()


        # ---------------- RED BUTTON ---------------- #
        if not buttons[1][0].value and not buttons[1][1] :
            buttons[1][1] = True

            if not SPEED_BLOCK:
                SPEED_FACTOR = 0.3
            run()

        if buttons[1][0].value and buttons[1][1] :
            buttons[1][1] = False
            if not SPEED_BLOCK:
                SPEED_FACTOR = 2.0
            run()


        # ---------------- BIG RED BUTTON ---------------- #
        if not buttons[3][0].value and not buttons[3][1] :
            buttons[3][1] = True
            
            if SPEED_FACTOR == 2.0:
                SPEED_FACTOR = 0
                SPEED_BLOCK = True
            else :
                SPEED_FACTOR = 2.0
                SPEED_BLOCK = False
            run()
            
        if buttons[3][0].value and buttons[3][1] :
            buttons[3][1] = False
            sleep(0.1)    
