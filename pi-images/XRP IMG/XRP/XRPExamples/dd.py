from XRPLib.defaults import *
from XRPLib.rangefinder import Rangefinder
import time

# Configure your custom pins here
TIMEOUT_US = 500 * 2 * 30   # Optional: adjust timeout in microseconds

# Create rangefinder with custom pins
rangefinder = Rangefinder(18, 19, TIMEOUT_US)

# Polling data from the ultrasonic sensor in a loop
while True:
    distance = rangefinder.distance()
    print(f"Distance: {distance} cm")
    time.sleep(0.1)
    
