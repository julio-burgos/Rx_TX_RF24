from usbmanager import *
import RPi.GPIO as GPIO
from colors import Color
from colors import lightLED
import time
import os

GPIO.setmode(GPIO.BCM)
COMMLED_PIN_0 = 21
COMMLED_PIN_1 = 16
COMMLED_PIN_2 = 20
GPIO.setup(COMMLED_PIN_0, GPIO.OUT)
GPIO.setup(COMMLED_PIN_1, GPIO.OUT)
GPIO.setup(COMMLED_PIN_2, GPIO.OUT)
commLedPins = [COMMLED_PIN_0, COMMLED_PIN_1, COMMLED_PIN_2]



while True:
    lightLED(commLedPins, Color.red)
    print("waiting for usb")
    wait_til_usb_connected()
    print("usb connected")
    lightLED(commLedPins, Color.green)
    read_copy("a.txt","/home/pi/test.txt")
    print("file copied from usb")
    lightLED(commLedPins, Color.blue)
    time.sleep(15)
    lightLED(commLedPins, Color.yellow)
    print("waiting for usb")
    wait_til_usb_connected()
    print("usb connected")
    lightLED(commLedPins, Color.cyan)
    print("Writing file to usb")
    write_file_usb("/home/pi/test.txt","copied.txt")
    print("Writed file to usb ")
    lightLED(commLedPins, Color.magenta)
    time.sleep(15)
