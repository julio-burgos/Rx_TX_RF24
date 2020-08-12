#This function adds a packet identification to the last byte of each packet. 
#The ID goes from 1 to 255 (1 BYTE)
#The last packet will have the ID = 0

import math
from buffer import Buffer 

def addPacketID(packetsList):

    packetsWithID = []
    numPackets = len(packetsList)

    #We have to define two different auxiliar iteration variables, as the ID = 0 is always skipped, an offset appears every time we get ID = 0.
    #iterationID = 1 #This defines which ID will be assigned to the current iteration packet
    #iterationPacket = 0 #This iterates over the packets

    for index,packet in enumerate(packetsList):
        IdPacket = packet.getBuffer()   

        if index < (numPackets - 1):            
            ID = index % 255 +1 #ID Values {1, 2, ..., 255} -> 1 Byte
            #ID = index % 2 +1 #ID Values {1, 2} -> 1 Byte
            IdPacket.insert(0,ID)             
                
        else: #Last packet
            IdPacket.insert(0,0)

        packetsWithID.append(packet)
        

    return packetsWithID
