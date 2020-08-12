#!/usr/bin/python
# -*- coding: utf-8 -*-
#
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
radio.setPALevel(RF24_PA_HIGH)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openReadingPipe(1, pipes[1])
radio.stopListening()
radio.printDetails()
radio.startListening()
#radio.writeAckPayload(1,bytearray([]))
strfile = []
previousID = None
currentID = None
isLast =False
try:
    timestart = time.time()
    while not isLast:
        pipe = [0]
        while not radio.available():
                #print "Waitiin"
                time.sleep(0.00001)
        
        recv_buffer = radio.read(radio.getDynamicPayloadSize())
        currentID = recv_buffer[0]
        #print(str(rcv))
        #print("Packet Received")
        #print("Packet ID " +str(currentID))

        #radio_rx.writeAckPayload(0,ackpl,len(ackpl))
        radio.writeAckPayload(1,bytearray([currentID]))
        if currentID != previousID:
                rcv =str(recv_buffer[1:])
                strfile.append(rcv)
                #print("Appending to file 😂")
                #print(rcv)
                previousID = currentID
                if currentID == 0:
                        file = open("recv.txt","wb")
                        
                        for pack in strfile:       
                                file.write(bytearray(pack))
                        file.close()
                        isLast=True
                
except Exception as e:
        print(e)
finally:
        timend = time.time()
        print(timend - timestart)
        radio.stopListening()
print("Finished 💩 👹")