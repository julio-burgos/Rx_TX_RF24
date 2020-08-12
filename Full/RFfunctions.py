import RPi.GPIO as GPIO
from RF24 import *
import spidev
import time
from FullModeCTE import *


def config_radio(channel, power, rate, autoAck=False, ce=25, csn=8):
    radio = RF24(ce, csn)
    radio.begin()
    radio.setChannel(channel)
    radio.setDataRate(rate)
    radio.setPALevel(power)
    radio.setAutoAck(autoAck)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()
    radio.stopListening()
    return radio


def send_radio_packet(data, radio, pipe_tx):
    radio.stopListening()
    # radio.openWritingPipe(pipe_tx)
    time.sleep(0.01)
    radio.write(data)


def wait_radio_packet(radio, pipe_rx):
    # radio.openReadingPipe(1, pipe_rx)
    radio.startListening()
    while not radio.available():
        time.sleep(0.001)
    packet = radio.read(radio.getDynamicPayloadSize())
    radio.stopListening()
    # radio.closeReadingPipe(1)
    return packet


def wait_radio_packet_timeout(radio, pipe_rx, timeout):
    # radio.openReadingPipe(1, pipe_rx)
    radio.startListening()
    time_first = time.time()
    packet = []
    timeout_reached = False
    while not radio.available():
        time.sleep(0.001)
        time_actual = time.time()
        if time_actual >= time_first + timeout:
            timeout_reached = True
            break

    if not timeout_reached:
        packet = radio.read(radio.getDynamicPayloadSize())

    radio.stopListening()
    # radio.closeReadingPipe(1)
    return packet, timeout_reached


def arrayToString(arrayBytes):
    return str(arrayBytes)


def close_radio(radio):
    radio.stopListening()
