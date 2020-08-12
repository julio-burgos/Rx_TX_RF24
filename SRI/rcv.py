#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import time
import RPi.GPIO as GPIO
from configradio import configradio
import zlib


def rcv(pipe, channel, power, rate, BLINKLED_PIN,ce=25, csn=8, filename="recv.txt"):
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
            if currentID == 1:
                print("Recieved packet with id  = 1")

            radio.writeAckPayload(1, bytearray([currentID]))
            if currentID != previousID:
                rcv = str(recv_buffer[1:])
                strfile.append(rcv)
                previousID = currentID
                if currentID == 0:
                    isLast = True
            time.sleep(0.001)
            GPIO.output(BLINKLED_PIN, 0)

    except Exception as e:
        print(e)
    finally:
        print("Starting Joining")
        strfile = ''.join(strfile)
        print("Starting decompression")
        strfile = zlib.decompress(strfile)
        print("Starting file saving")
        #TODO: Add method writeToUSB(strFile) This method writes the received .txt into the corresponding USB device.
        file = open(filename, "wb")        
        # for pack in strfile:
        #     file.write(bytearray(pack))                
        file.write(strfile)
        file.close()
        radio.stopListening()
        print("Finished 💩 👹")
        return strfile
