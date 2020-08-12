from RF24 import *
import time

PIPES = [0xe7e7e7e7e7, 0xc2c2c2c2c2]
rate = RF24_2MBPS
power =  RF24_PA_HIGH
channel=0x60
ce=25
csn=8

pipe_master_tx = pipe_slave_rx= PIPES[0]
pipe_master_rx = pipe_slave_tx= PIPES[1]

def confradio():
    radio = RF24(ce,csn)
    radio.begin()
    radio.setChannel(channel)
    radio.setDataRate(rate)
    radio.setPALevel(power)
    radio.enableDynamicPayloads()
    radio.setAutoAck(False)
    radio.stopListening()
    radio.printDetails()
    return radio

radio = confradio()
def send(pipe_tx,data):
    radio.stopListening()
    radio.openWritingPipe(pipe_tx)
    while not radio.write(data):
        time.sleep(0.01)
    

def receive(pipe_rx):
    radio.openReadingPipe(1,pipe_rx)
    radio.startListening()
    while not radio.available():
        time.sleep(0.1)
    data =  radio.read(radio.getDynamicPayloadSize())
    radio.stopListening()
    radio.closeReadingPipe(1)
    return data

dataM = b"M"
dataS = b"I am ACK "
amImaster=True
radio = confradio()

for i in range(6):
    if amImaster:
        print("I am in master if")
        time.sleep(3)
        send(pipe_master_tx,bytearray(b"1"+dataM))
        data = receive(pipe_master_rx)
        
        print(data)
    else:
        print("I am in slave else")
        data = receive(pipe_slave_rx)
        print(data)
        send(pipe_slave_tx,bytearray(b"0"+dataS))
    if i==2:
        amImaster= not amImaster
    time.sleep(1)
