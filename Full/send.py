#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import time
from getPackets import getPackets
from addPacketID import addPacketID
from configradio import configradio
import zlib
import RPi.GPIO as GPIO
from FullModeCTE import *


def send(pipe, channel, power, rate, data, ce=25, csn=8):
    radio = configradio(pipe, channel, power, rate, False, ce, csn)
    strFile = zlib.compress(data, 9)
    packetsList = getPackets(strFile, SRI_PAYLOAD_SIZE)
    packetsList = addPacketID(packetsList)
    for index, packet in enumerate(packetsList):
        ackischecked = False
        while not ackischecked:
            is_sended = radio.write(packet.getBufferString())
            if is_sended:
                if radio.isAckPayloadAvailable():
                    GPIO.output(BLINKLED_PIN, 1)
                    ackPL = radio.read(radio.getDynamicPayloadSize())
                    ackischecked = True
                    time.sleep(0.001)
                    GPIO.output(BLINKLED_PIN, 0)

    print("Finished 💩 👹")
