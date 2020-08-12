import RPi.GPIO as GPIO
from RF24 import *
import time
import spidev

GPIO.setmode(GPIO.BCM)

pipes = [0xe7e7e7e7e7, 0xc2c2c2c2c2]

radio = RF24(25,8)
radio.begin()
#radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(RF24_2MBPS)
radio.setPALevel(RF24_PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[1])
radio.printDetails()

radio.startListening()

while True:
    ackPL = [1]
    while not  radio.available():
        time.sleep(1/100)

    receivedMessage =radio.read(radio.getDynamicPayloadSize())
    print("Received: {}".format(receivedMessage))

    print("Translating the receivedMessage into unicode characters...")
    string = ""
    for n in receivedMessage:
        # Decode into standard unicode set
        if (n >= 32 and n <= 126):
            string += chr(n)
    print(string)

    radio.writeAckPayload(1, bytearray(ackPL))
    print("Loaded payload reply of {}".format(ackPL))
