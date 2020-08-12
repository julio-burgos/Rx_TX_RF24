import RPi.GPIO as GPIO
from colors import Color
from colors import lightLED
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN)
GPIO.setup(19, GPIO.IN)

GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

commLedPins = [16, 20]

# while True:
#     time.sleep(0.1)
#     sw1= GPIO.input(26) #on/off
#     sw2= GPIO.input(19) #tx/rx
#     GPIO.output(16,sw1)
#     GPIO.output(20,sw2)
#     print('SW1:' sw1)
#     print('SW2:' sw2)

while True:
    lightLED(commLedPins, Color.cyan)
    time.sleep(0.5)
    lightLED(commLedPins, Color.green)
    time.sleep(0.5)