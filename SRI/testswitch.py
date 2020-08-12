import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
INPUT_PIN = 19           # Sets our input pin, in this example I'm connecting our button to pin 4. Pin 0 is the SDA pin so I avoid using it for sensors/buttons
GPIO.setup(INPUT_PIN, GPIO.IN)
while True:
    if (GPIO.input(INPUT_PIN) == True):  # Physically read the pin now
        print('3.3')
    else:
        print('0')
    # Sleep for a full second before restarting our loop
    time.sleep(1)
