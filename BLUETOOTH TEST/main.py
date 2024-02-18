# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
from time import sleep
from adafruit_servokit import ServoKit
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor


#############################################################
#                          FUNCTION                         #
#############################################################
def speed(val, duration = 1):
    kit.continuous_servo[7].throttle = val
    sleep(duration)
    kit.continuous_servo[7].throttle = 0
    sleep(duration)
    kit.continuous_servo[7].throttle = -val
    sleep(duration - 0.3) # Faster when coming back for some reasons so the duration is shorter
#############################################################
#                          CONTENT                          #
#############################################################
## STATE
prev_state = None

## BLE
ble = BLERadio()
# uart = UARTService()
# advertisement = ProvideServicesAdvertisement(uart)
advertisement = AdafruitColor()    

## SERVO
kit = ServoKit(channels=8)
kit.continuous_servo[7].set_pulse_width_range(550, 2500)

## A BIT OF WAIT
sleep(0.5)

#############################################################
#                          ACTIONS                          #
#############################################################
actions = {
    0x000000:[0.05, 2],
    0x000001:[-0.1, 2]
}

#############################################################
#                         MAIN LOOP                         #
#############################################################
counter = 0
while True :        
    for entry in ble.start_scan(AdafruitColor, timeout=5):
        color = entry.color
        print(f"0x{color:06x}")

        if color in actions.keys() :
            speed(actions[color][0], actions[color][1])
            break

    kit.continuous_servo[7].throttle = 0   
    ble.stop_scan()

