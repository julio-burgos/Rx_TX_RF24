#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import time
from getPackets import getPackets
from addPacketID import addPacketID
from configradio import configradio
import zlib
import RPi.GPIO as GPIO
def send(pipe, channel, power, rate, BLINKLED_PIN,data,ce=25, csn=8, filename="file_test.txt", log=True):
    radio = configradio(pipe, channel, power, rate, False, ce, csn)
    
    #TODO: Add method file = readFromUSB() -> This method will look for the USB path and read the corresponding .txt file
    
    strFile= zlib.compress(data,9)
    packetsList = getPackets(strFile, maxPayloadSize=31)
    packetsList = addPacketID(packetsList)
    pcg = int(len(packetsList)*0.1)+1
    for index, packet in enumerate(packetsList):
        ackischecked = False
        if log and index % pcg == 0:
             print(str(index+1)+" / "+str(len(packetsList)))
        #print(str(index+1)+" / "+str(len(packetsList)))
        while not ackischecked:

            is_sended = radio.write(packet.getBufferString())
            if is_sended:

                #print(" Only Sended")
                if radio.isAckPayloadAvailable():
                    GPIO.output(BLINKLED_PIN, 1)
                    ackPL = radio.read(radio.getDynamicPayloadSize())
                    ackischecked = True
                    time.sleep(0.001)
                    GPIO.output(BLINKLED_PIN, 0)
    print("Finished 💩 👹")
