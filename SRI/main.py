import time
import RPi.GPIO as GPIO
from colors import Color
from colors import lightLED
from send import send
from rcv import rcv
from RF24 import *
from usbmanager import *
GPIO.setmode(GPIO.BCM)
# 19 or 16 Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
SWITCH_PIN_ON_OFF = 26
GPIO.setup(SWITCH_PIN_ON_OFF, GPIO.IN)
# 19 or 16 Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
SWITCH_PIN_TX_RX = 19
GPIO.setup(SWITCH_PIN_TX_RX, GPIO.IN)
# 19 or 16 Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
SWITCH_PIN_SRI_NW = 13
GPIO.setup(SWITCH_PIN_SRI_NW, GPIO.IN)

filenamesri = "MTP-F19-SRI-B-TX.txt"
filereceivedsri = "MTP-F19-SRI-B-RX.txt"

COMMLED_PIN_0 = 21
COMMLED_PIN_1 = 16
COMMLED_PIN_2 = 20
GPIO.setup(COMMLED_PIN_0, GPIO.OUT)
GPIO.setup(COMMLED_PIN_1, GPIO.OUT)
GPIO.setup(COMMLED_PIN_2, GPIO.OUT)

BLINKLED_PIN = 12
GPIO.setup(BLINKLED_PIN, GPIO.OUT)

pipe = 0xc2c2c2c2c2
channel = 0x60
rate = RF24_2MBPS
power = RF24_PA_HIGH
commLedPins = [COMMLED_PIN_0, COMMLED_PIN_1, COMMLED_PIN_2]
netwLedPins = [0, 0]  # TODO: To be defined

is_on = False
# is_on = GPIO.input(SWITCH_PIN_ON_OFF)

while True:
    # is_on=False
    try:
        is_on = GPIO.input(SWITCH_PIN_ON_OFF)

        if GPIO.input(SWITCH_PIN_SRI_NW) == True:
            print("Starting SRI mode transmission")
            if GPIO.input(SWITCH_PIN_TX_RX) == True:
                lightLED(commLedPins, Color.red)
                wait_til_usb_connected()
                data = read_file_usb(filenamesri)
            lightLED(commLedPins, Color.cyan)
            while not is_on:
                #print("Waiting for beginning communication")
                is_on = GPIO.input(SWITCH_PIN_ON_OFF)
                time.sleep(0.2)
            #is_on = True
            
            
            if GPIO.input(SWITCH_PIN_TX_RX) == True:  # Physically read the pin now
                print("Starting sender")
                
                lightLED(commLedPins, Color.blue)
                send(pipe, channel, power, rate, BLINKLED_PIN, data)

            else:
                print("Starting receiver")
                lightLED(commLedPins, Color.yellow)
                datarcv = rcv(pipe, channel, power, rate, BLINKLED_PIN)
                lightLED(commLedPins, Color.magenta)
                wait_til_usb_connected()
                write_data_usb(datarcv, filereceivedsri)
            # Sleep for a full second before restarting our loop

            print("Ended comunnication")
            lightLED(commLedPins, Color.green)

        else:
            print("Starting NW transmission")
            lightLED(commLedPins, Color.yellow)

        while is_on:
            is_on = GPIO.input(SWITCH_PIN_ON_OFF)
            time.sleep(0.2)
        #print("Leaving  is_on loop")

    except Exception as e:
        print(e)
