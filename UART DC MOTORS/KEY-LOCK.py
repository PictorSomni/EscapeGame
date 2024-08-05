# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials UART Serial example"""
import board
import busio
import digitalio
from time import sleep
from adafruit_motorkit import MotorKit

## KEY
key = digitalio.DigitalInOut(board.A0)
key.direction = digitalio.Direction.INPUT
key.pull = digitalio.Pull.UP

kit = MotorKit(i2c=board.I2C())

while True:
    while not key.value :
        kit.motor1.throttle = 0.5
        sleep(0.5)
        kit.motor1.throttle = 0
