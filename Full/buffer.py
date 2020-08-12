class Buffer:

    def __init__(self, maxLength):
        self.maxLength = maxLength
        self.sizeAvailable = self.maxLength
        self.bufferDataSize = 0
        self.bufferOffset = 0
        self.buffer = []

    def getMaxLength(self):
        return self.maxLength
    
    def getSizeAvailable(self):
        return self.sizeAvailable

    def getBufferDataSize(self):
        return self.bufferDataSize
        
    def getBuffer(self):
        return self.buffer

    def getBufferString(self):
        return bytearray(self.buffer)

    def getBufferOffset(self):
        return self.bufferOffset

    def fillBuffer(self, data):
        L = len(data)
    
        if(L > self.sizeAvailable):
            print("Not available memory space!")
        else:
            self.buffer[self.bufferOffset:(self.bufferOffset + L)] = data
            self.bufferOffset = self.bufferOffset + L
            self.bufferDataSize = len(self.buffer)
            self.sizeAvailable = self.sizeAvailable - L