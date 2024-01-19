# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials UART Serial example"""
import board
import busio
import digitalio
from time import sleep
from adafruit_motorkit import MotorKit

# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.A0)
led.direction = digitalio.Direction.OUTPUT

uart = busio.UART(board.TX, board.RX, baudrate=9600)

kit = MotorKit(i2c=board.I2C())

while True:
    data = uart.read()
    # print(data)  # this is a bytearray type

    if data is not None:
        if data == b'32' :

            kit.motor2.throttle = 1.0
            for i in range(6) :
                led.value = True
                sleep(0.1)
                led.value = False
                sleep(0.1)
            kit.motor2.throttle = 0

        elif data == b'15' :
            kit.motor1.throttle = 1.0
            for i in range(3) :
                led.value = True
                sleep(0.5)
                led.value = False
                sleep(0.5)
            kit.motor1.throttle = 0
