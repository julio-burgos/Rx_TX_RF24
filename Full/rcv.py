#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import time
import RPi.GPIO as GPIO
from configradio import configradio
import zlib
from FullModeCTE import *


def rcv(pipe, channel, power, rate, ce=25, csn=8):
    radio = configradio(pipe, channel, power, rate, True, ce, csn)
    strfile = []
    previousID = None
    currentID = None
    isLast = False
    try:
        while not isLast:
            pipe = [0]
            while not radio.available():
                time.sleep(0.00001)
            GPIO.output(BLINKLED_PIN, 1)
            recv_buffer = radio.read(radio.getDynamicPayloadSize())
            currentID = recv_buffer[0]
            radio.writeAckPayload(1, bytearray([currentID]))
            if currentID != previousID:
                rcv = str(recv_buffer[1:])
                strfile.append(rcv)
                previousID = currentID
                if currentID == 0:
                    isLast = True
            # Sleep to see the LED blinking
            time.sleep(0.001)
            GPIO.output(BLINKLED_PIN, 0)

    except Exception as e:
        print(e)
    finally:
        strfile = ''.join(strfile)
        strfile = zlib.decompress(strfile)
        file = open(SRI_FILENAME_OUTPUT, "wb")
        file.write(strfile)
        file.close()
        radio.stopListening()
        print("Finished 💩 👹")
        return strfile
