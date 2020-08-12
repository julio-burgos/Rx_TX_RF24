import time
import RPi.GPIO as GPIO
from colors import Color
from colors import lightLED
from send import send
from rcv import rcv
from RF24 import *
from USBManager import *
from FullModeCTE import *
from NetworkModeFSM import NetworkModeFSM
from RFfunctions import config_radio
import sys

GPIO.setmode(GPIO.BCM)

# Set up the pins for the switches
GPIO.setup(SWITCH_PIN_ON_OFF, GPIO.IN)
GPIO.setup(SWITCH_PIN_TX_RX, GPIO.IN)
GPIO.setup(SWITCH_PIN_SRI_NW, GPIO.IN)

# Set up the pins for the LEDs
GPIO.setup(COMMLED_PIN_0, GPIO.OUT)
GPIO.setup(COMMLED_PIN_1, GPIO.OUT)
GPIO.setup(COMMLED_PIN_2, GPIO.OUT)

GPIO.setup(BLINKLED_PIN, GPIO.OUT)

commLedPins = [COMMLED_PIN_0, COMMLED_PIN_1, COMMLED_PIN_2]

is_on = False

while True:
    try:
        is_on = GPIO.input(SWITCH_PIN_ON_OFF)
        if GPIO.input(SWITCH_PIN_SRI_NW) == True:
            print("We are in SRI")
            if GPIO.input(SWITCH_PIN_TX_RX) == True:
                lightLED(commLedPins, Color.red)
                wait_til_usb_connected()
                data = read_file_usb(SRI_FILENAME_INPUT)

            lightLED(commLedPins, Color.cyan)
            while not is_on:
                is_on = GPIO.input(SWITCH_PIN_ON_OFF)
                time.sleep(0.2)

            if GPIO.input(SWITCH_PIN_TX_RX) == True:
                print("Starting sender")
                lightLED(commLedPins, Color.blue)
                send(PIPES[0], SRI_CHANNEL, SRI_PA_LEVEL,
                     SRI_DATARATE, data)

            else:
                print("Starting receiver")
                lightLED(commLedPins, Color.yellow)
                datarcv = rcv(PIPES[0], SRI_CHANNEL,
                              SRI_PA_LEVEL, SRI_DATARATE)
                lightLED(commLedPins, Color.magenta)
                wait_til_usb_connected()
                write_data_usb(datarcv, SRI_FILENAME_OUTPUT)
            lightLED(commLedPins, Color.green)

        else:
            print("We are in NM")
            lightLED(commLedPins, Color.yellow)
            # Iniciar el Network Mode
            radio = config_radio(channel=NETWORK_CHANNEL,
                                 power=NETWORK_PA_LEVEL, rate=NETWORK_DATARATE)

            state = {"addr": NETWORK_SELF_ADDR, "first_tx": False, "token_pl": [], "reply_yes": [], "reply_no": [],
                     "retransmission": 0, "data": [], "src_token": None, "polling_addr": None}

            first = is_usb_connected_NM()
            lightLED(commLedPins, Color.cyan)
            while not is_on:
                is_on = GPIO.input(SWITCH_PIN_ON_OFF)
                time.sleep(0.2)

            networkfsm = NetworkModeFSM(state, radio, commLedPins, first)

        while is_on:
            is_on = GPIO.input(SWITCH_PIN_ON_OFF)
            time.sleep(0.2)

    except Exception as e:
        print(e)
