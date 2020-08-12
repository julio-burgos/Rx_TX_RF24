import RPi.GPIO as GPIO
from RF24 import *
import time
import spidev
GPIO.setmode(GPIO.BCM)
def configradio(pipe,channel,power,rate,listening,ce=25,csn=8):

    radio = RF24(ce,csn)
    radio.begin()
    radio.setChannel(channel)
    radio.setDataRate(rate)
    radio.setPALevel(power)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()
    radio.stopListening()
    radio.printDetails()
    if listening:
        radio.openReadingPipe(1, pipe)
        radio.startListening()
    else:
        radio.openWritingPipe(pipe)
    return radio