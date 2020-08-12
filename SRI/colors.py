#from enum import Enum
import RPi.GPIO as GPIO

class Color():
    red = [1, 0, 0] 
    green = [0, 1, 0]
    blue = [0, 0, 1]
    cyan = [0, 1, 1]
    magenta = [1, 0, 1]
    yellow = [1, 1, 0]
    none = [0, 0, 0]

def lightLED(ledPins, color):
    GPIO.output(ledPins[0], color[0])
    GPIO.output(ledPins[1], color[1])
    GPIO.output(ledPins[2], color[2])
    
    # GPIO.output(16,sw1)
    # GPIO.output(20,sw2)




