import math
from buffer import Buffer

def getPackets(strFile,maxPayloadSize = 32):
    lOffset = 0
 
    # It is a full raw text file, so the length defines the bytes. Every character is a byte.
    lFile = len(strFile)

    kPackets = math.floor(lFile / maxPayloadSize)  # Number of packets to be sent
    kPackets = int(kPackets)

    # Remaining bytes to be sent in the last packet.
    lStrRemaining = lFile - kPackets*maxPayloadSize

    #Fill the packets
    bufferList = []

    for k in range(0, kPackets):
        bufferList.append(Buffer(maxPayloadSize))
        bufferList[k].fillBuffer(strFile[lOffset:(lOffset + maxPayloadSize)])        
        lOffset = lOffset + maxPayloadSize

    #Last bytes in the file.
    bufferList.append(Buffer(maxPayloadSize))
    bufferList[-1].fillBuffer(strFile[lOffset:(lOffset + lStrRemaining)])

    # Now you have a list with buffers of length 'maxPayloadSize'.
    # The last buffer will have the last bytes of the txt file.

    return bufferList