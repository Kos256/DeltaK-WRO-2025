from XRPLib.defaults import *
import sys
import select
from time import sleep as wait


i = 0
while True:
    # Check if there's data waiting on USB
    if select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        # print("Got:", line)
        sys.stdout.write(f"Recv data checked at #{i}:{line}\n")
    else:
        # Do other stuff without blocking
        # print("No data yet...")
        sys.stdout.write(f"Check #{i} yields no data...\n")
        wait(1)
    i += 1


# available variables from defaults: left_motor, right_motor, drivetrain,
#      imu, rangefinder, reflectance, servo_one, board, webserver
# Write your code Here
