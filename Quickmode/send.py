#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import RPi.GPIO as GPIO
from RF24 import *
import time
import spidev
from getPackets import getPackets
from addPacketID import addPacketID
GPIO.setmode(GPIO.BCM)


pipes = [0xe7e7e7e7e7 , 0xc2c2c2c2c2]

radio = RF24(25,8)
radio.begin()

time.sleep(1)
radio.setRetries(15,15)
#radio.setPayloadSize(32)
radio.setChannel(0x60)

radio.setDataRate(RF24_2MBPS)
radio.setPALevel(RF24_PA_HIGH)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[1])
radio.stopListening()
radio.printDetails()

filename = "file_test.txt"

file = open(filename, "rb")
strFile = file.read()

packetsList = getPackets(strFile,maxPayloadSize=31)
packetsList = addPacketID(packetsList)


pcg = int(len(packetsList)*0.1)+1

for index,packet in enumerate(packetsList):
    ackischecked = False
    
    
    #print(str(index+1)+"/"+str(len(packetsList)))
    if index%pcg ==0 :
            print(str(index+1)+" / "+str(len(packetsList)))
    while not ackischecked:
        
        is_sended = radio.write(packet.getBufferString())
        if is_sended:
                #print(" Only Sended")
                if radio.isAckPayloadAvailable():
                        ackPL = radio.read(radio.getDynamicPayloadSize())
                        #print(" Ack received ")
                        #print (packet.getBufferString()[0])
                        #if ackPL[0] == packet.getBufferString()[0]:
                        ackischecked = True
print("Finished 💩 👹")



