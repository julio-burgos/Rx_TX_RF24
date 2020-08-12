import RPi.GPIO as GPIO
from RF24 import *
import time
import spidev

GPIO.setmode(GPIO.BCM)

pipes = [0xe7e7e7e7e7 , 0xc2c2c2c2c2]

radio = RF24(25,8)
radio.begin()

time.sleep(1)
radio.setRetries(15,15)
#radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(RF24_2MBPS)
radio.setPALevel(RF24_PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[1])
radio.printDetails()

while True:
    message = list("Hello World")
    radio.write(bytearray("Hello World"))
    print("We sent the message of {}".format(message))

    # Check if it returned a ackPL
    if radio.isAckPayloadAvailable():
        returnedPL = radio.read(radio.getDynamicPayloadSize())
        print("Our returned payload was {}".format(returnedPL))
    else:
        print("No payload received")
    time.sleep(1)

